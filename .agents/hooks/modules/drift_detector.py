import os

def check_drift(active_file, base_dir):
    drift_warnings = []
    if active_file:
        active_base = os.path.basename(active_file)
        if active_base and active_base != "unknown":
            try:
                import sqlite3
                db_path = os.path.join(base_dir, '.orion', 'orion.db')
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    c = conn.cursor()
                    c.execute("SELECT source_id, relation FROM edges WHERE target_id LIKE ? LIMIT 5", (f"%{active_base}%",))
                    rows = c.fetchall()
                    for source_id, relation in rows:
                        source_base = os.path.basename(source_id)
                        if source_base != active_base:
                            drift_warnings.append(f"CRITICAL DRIFT RISK: `{source_base}` {relation} this active file. If you modify `{active_base}`, you MUST verify if `{source_base}` needs updating!")
                    conn.close()
            except Exception as e:
                print(f"[DRIFT] Failed to query graph: {e}")
                
    return drift_warnings
