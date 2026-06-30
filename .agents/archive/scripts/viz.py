import os
import json
import sqlite3
import webbrowser
import urllib.parse

def setup_parser(subparsers):
    viz_parser = subparsers.add_parser('viz', help='Generate HTML visualization of the Orion graph')
    viz_parser.add_argument('--open', action='store_true', help='Open the HTML in default browser automatically')

def main(args):
    agents_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    workspace_dir = os.path.dirname(agents_dir)
    orion_dir = os.path.join(workspace_dir, '.orion')
    working_dir = os.path.join(orion_dir, 'working')
    db_path = os.path.join(orion_dir, 'orion.db')
    out_path = os.path.join(working_dir, 'orion_graph.html')
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return
        
    os.makedirs(working_dir, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    nodes = []
    edges = []
    
    # Vis.js node colors by type
    color_map = {
        'rule': '#f56565',     # red
        'skill': '#4299e1',    # blue
        'concept': '#48bb78',  # green
        'memory': '#ecc94b',   # yellow
        'document': '#a0aec0', # gray
        'file': '#ed8936',     # orange
        'entity': '#9f7aea'    # purple
    }
    
    import re
    # 1. Fetch nodes from 'nodes' table (AST & Triplets)
    c.execute("SELECT id, type, name FROM nodes")
    for row in c.fetchall():
        n_id, n_type, n_name = row
        n_type = n_type or 'concept'
        color = color_map.get(n_type.lower(), '#a0aec0')
        nodes.append({
            'id': n_id,
            'label': n_name,
            'group': n_type,
            'color': color,
            'title': f"[{n_type.upper()}] {n_name}"
        })
        
    # 2. Fetch pages from 'pages' table (Rules, Skills, Context)
    page_ids = set()
    c.execute("SELECT path, category FROM pages")
    for row in c.fetchall():
        p_path, p_cat = row
        p_name = os.path.basename(p_path)
        p_cat = p_cat or 'document'
        color = color_map.get(p_cat.lower(), '#a0aec0')
        nodes.append({
            'id': p_name, # using basename as id for easy linking
            'label': p_name,
            'group': p_cat,
            'color': color,
            'title': f"[{p_cat.upper()}] {p_path}"
        })
        page_ids.add(p_name)
        
    # 3. Fetch edges from 'edges' table (AST & Triplets)
    c.execute("SELECT source_id, target_id, relation FROM edges")
    for row in c.fetchall():
        s_id, t_id, rel = row
        # Optional: simplify source_id if it's a path, to match page node ID
        if '/' in s_id or '\\' in s_id:
            s_id = os.path.basename(s_id)
        if '/' in t_id or '\\' in t_id:
            t_id = os.path.basename(t_id)
        edges.append({
            'from': s_id,
            'to': t_id,
            'label': rel,
            'arrows': 'to'
        })
        
    # 4. Extract wiki links from 'pages_fts' (Markdown links)
    c.execute("SELECT path, content FROM pages_fts")
    for row in c.fetchall():
        p_path, p_content = row
        s_id = os.path.basename(p_path)
        links = re.findall(r'\[\[(.*?)\]\]', p_content)
        for link in links:
            parts = link.split('|')
            t_id = parts[0].strip()
            rel = parts[1].strip() if len(parts) > 1 else "mentions"
            
            # Prevent self-loop if necessary
            if s_id != t_id:
                edges.append({
                    'from': s_id,
                    'to': t_id,
                    'label': rel,
                    'arrows': 'to',
                    'dashes': True  # Make wiki links dashed to differentiate
                })
                # Add target node if it doesn't exist yet (ghost node)
                if t_id not in page_ids:
                    nodes.append({
                        'id': t_id,
                        'label': t_id,
                        'group': 'concept',
                        'color': '#cbd5e0',
                        'title': f"[GHOST] {t_id}"
                    })
                    page_ids.add(t_id)
        
    conn.close()
    
    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Orion Knowledge Graph</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        body {{
            margin: 0;
            padding: 0;
            background-color: #1a202c;
            color: #cbd5e0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        #mynetwork {{
            width: 100vw;
            height: 100vh;
            border: none;
        }}
        #header {{
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 10;
            background: rgba(45, 55, 72, 0.9);
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        h1 {{
            margin: 0 0 5px 0;
            font-size: 1.5rem;
            color: #fff;
        }}
        p {{
            margin: 0;
            font-size: 0.9rem;
        }}
        .legend {{
            margin-top: 15px;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85rem;
        }}
        .dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
    </style>
</head>
<body>
    <div id="header">
        <h1>Orion Graph</h1>
        <p>Total Nodes: {len(nodes)} | Total Edges: {len(edges)}</p>
        <div class="legend">
            <div class="legend-item"><div class="dot" style="background:#f56565;"></div>Rule</div>
            <div class="legend-item"><div class="dot" style="background:#4299e1;"></div>Skill</div>
            <div class="legend-item"><div class="dot" style="background:#48bb78;"></div>Concept</div>
            <div class="legend-item"><div class="dot" style="background:#ecc94b;"></div>Memory</div>
            <div class="legend-item"><div class="dot" style="background:#9f7aea;"></div>Entity (Triplet)</div>
            <div class="legend-item"><div class="dot" style="background:#a0aec0;"></div>Document/Other</div>
        </div>
    </div>
    <div id="mynetwork"></div>

    <script type="text/javascript">
        var nodes = new vis.DataSet({nodes_json});
        var edges = new vis.DataSet({edges_json});

        var container = document.getElementById('mynetwork');
        var data = {{
            nodes: nodes,
            edges: edges
        }};
        var options = {{
            nodes: {{
                shape: 'dot',
                size: 16,
                font: {{
                    color: '#e2e8f0',
                    size: 14, // px
                    face: 'arial'
                }},
                borderWidth: 2,
                shadow: true
            }},
            edges: {{
                width: 1.5,
                color: {{ inherit: 'from', opacity: 0.6 }},
                smooth: {{
                    type: 'continuous'
                }},
                font: {{
                    color: '#a0aec0',
                    size: 10,
                    align: 'middle'
                }}
            }},
            physics: {{
                forceAtlas2Based: {{
                    gravitationalConstant: -100,
                    centralGravity: 0.01,
                    springLength: 100,
                    springConstant: 0.08,
                    damping: 0.4
                }},
                solver: 'forceAtlas2Based',
                stabilization: {{
                    iterations: 150
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200,
                hideEdgesOnDrag: true
            }}
        }};
        var network = new vis.Network(container, data, options);
    </script>
</body>
</html>
"""
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"[OK] Graph visualization generated at: {out_path}")
    
    if getattr(args, 'open', False):
        print("Opening in default browser...")
        file_url = 'file://' + urllib.parse.quote(out_path.replace('\\', '/'))
        webbrowser.open(file_url)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('command', nargs='?', help='Command name passed by orion.py')
    parser.add_argument('--open', action='store_true', help='Open automatically')
    args = parser.parse_args()
    main(args)
