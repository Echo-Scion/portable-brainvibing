#!/usr/bin/env python
"""
contradict.py — Contradiction Resolution Engine (IDE-1)
Detects and manages conflicting knowledge triplets in the Orion Graph.
"""
import os
import sys
import sqlite3
from datetime import datetime

# Force utf-8
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
WORKSPACE_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
DB_PATH = os.path.join(WORKSPACE_DIR, '.orion', 'orion.db')


def get_db():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database not found: {DB_PATH}")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)


def detect_contradictions():
    """Scan edges for predicate collisions: same source+relation, different target."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Find edges where same source_id + relation points to different targets
    cursor.execute("""
        SELECT e1.source_id, e1.relation, e1.target_id, e2.target_id
        FROM edges e1
        JOIN edges e2 ON e1.source_id = e2.source_id 
            AND e1.relation = e2.relation 
            AND e1.target_id != e2.target_id
        WHERE e1.target_id < e2.target_id  -- avoid duplicates
    """)
    
    collisions = cursor.fetchall()
    
    if not collisions:
        print("[OK] No predicate collisions detected in the graph.")
        conn.close()
        return
    
    print(f"[DETECT] Found {len(collisions)} potential contradictions:\n")
    
    new_count = 0
    for src, rel, target_a, target_b in collisions:
        # Check if this contradiction is already recorded
        cursor.execute("""
            SELECT id FROM contradictions 
            WHERE edge_a_source = ? AND edge_a_relation = ? 
            AND edge_a_target = ? AND edge_b_target = ?
        """, (src, rel, target_a, target_b))
        
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO contradictions 
                (edge_a_source, edge_a_target, edge_a_relation, edge_b_source, edge_b_target, edge_b_relation)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (src, target_a, rel, src, target_b, rel))
            new_count += 1
            print(f"  [NEW] ({src}) --[{rel}]--> ({target_a}) vs ({target_b})")
        else:
            print(f"  [KNOWN] ({src}) --[{rel}]--> ({target_a}) vs ({target_b})")
    
    conn.commit()
    conn.close()
    print(f"\n[DETECT] {new_count} new contradictions recorded, {len(collisions) - new_count} already known.")


def list_unresolved():
    """List all unresolved contradictions."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, edge_a_source, edge_a_relation, edge_a_target, edge_b_target, detected_at
        FROM contradictions 
        WHERE resolution = 'unresolved'
        ORDER BY detected_at DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("[OK] No unresolved contradictions.")
        return
    
    print(f"[LIST] {len(rows)} unresolved contradictions:\n")
    for cid, src, rel, ta, tb, detected in rows:
        print(f"  #{cid}: ({src}) --[{rel}]--> ({ta}) vs ({tb})  [detected: {detected}]")


def resolve(contradiction_id, resolution, evidence=""):
    """Resolve a contradiction by ID."""
    if resolution not in ('a_wins', 'b_wins', 'merged'):
        print(f"[ERROR] Invalid resolution: {resolution}. Must be: a_wins, b_wins, merged")
        sys.exit(1)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get the contradiction
    cursor.execute("SELECT * FROM contradictions WHERE id = ?", (contradiction_id,))
    row = cursor.fetchone()
    if not row:
        print(f"[ERROR] Contradiction #{contradiction_id} not found.")
        conn.close()
        sys.exit(1)
    
    # Update resolution
    cursor.execute("""
        UPDATE contradictions 
        SET resolution = ?, evidence = ?, resolved_at = datetime('now')
        WHERE id = ?
    """, (resolution, evidence, contradiction_id))
    
    # Adjust confidence scores
    if resolution == 'a_wins':
        cursor.execute("""
            UPDATE edges SET confidence = MIN(confidence * 1.2, 2.0) 
            WHERE source_id = ? AND target_id = ? AND relation = ?
        """, (row[1], row[2], row[3]))
        cursor.execute("""
            UPDATE edges SET confidence = MAX(confidence * 0.5, 0.1) 
            WHERE source_id = ? AND target_id = ? AND relation = ?
        """, (row[4], row[5], row[6]))
    elif resolution == 'b_wins':
        cursor.execute("""
            UPDATE edges SET confidence = MAX(confidence * 0.5, 0.1) 
            WHERE source_id = ? AND target_id = ? AND relation = ?
        """, (row[1], row[2], row[3]))
        cursor.execute("""
            UPDATE edges SET confidence = MIN(confidence * 1.2, 2.0) 
            WHERE source_id = ? AND target_id = ? AND relation = ?
        """, (row[4], row[5], row[6]))
    
    conn.commit()
    conn.close()
    print(f"[RESOLVED] Contradiction #{contradiction_id} → {resolution}")


def main():
    if len(sys.argv) < 2:
        print("Usage: contradict.py [detect|list|resolve]")
        print("  detect          — Scan graph for predicate collisions")
        print("  list            — Show unresolved contradictions")
        print("  resolve ID RES  — Resolve (RES: a_wins|b_wins|merged)")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    if action == 'detect':
        detect_contradictions()
    elif action == 'list':
        list_unresolved()
    elif action == 'resolve':
        if len(sys.argv) < 4:
            print("Usage: contradict.py resolve <ID> <a_wins|b_wins|merged> [evidence]")
            sys.exit(1)
        cid = int(sys.argv[2])
        res = sys.argv[3]
        evidence = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""
        resolve(cid, res, evidence)
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


if __name__ == '__main__':
    main()
