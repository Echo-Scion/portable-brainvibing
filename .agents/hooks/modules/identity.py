import os
import json
import time
import re
import sys
from datetime import datetime

def extract_top_lessons(learnings_content):
    lessons = []
    for line in learnings_content.split('\n'):
        line_s = line.strip()
        if line_s.startswith('- ') and len(line_s) > 10:
            lessons.append(line_s[2:].strip())
        elif line_s.startswith('* ') and len(line_s) > 10:
            lessons.append(line_s[2:].strip())
        elif line_s.startswith('**Self-Evolve Rule**:') and len(line_s) > 22:
            lessons.append(line_s.replace('**Self-Evolve Rule**:', '').strip())
        elif line_s.startswith('## 20') and '—' in line_s:
            lessons.append(line_s.lstrip('#').strip())
    return lessons[:5]

def bootstrap_identity(identity_path, base_agents_dir, learnings_path, workspace_dir):
    identity_exists = os.path.exists(identity_path)
    top_lessons = []
    
    if not identity_exists:
        template_path = os.path.join(base_agents_dir, 'templates', 'agent-identity-template.md')
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = f.read()
                
                if os.path.exists(learnings_path):
                    with open(learnings_path, 'r', encoding='utf-8') as f:
                        learnings_content = f.read()
                    top_lessons = extract_top_lessons(learnings_content)
                
                lessons_str = '\n'.join(f"{i+1}. {l}" for i, l in enumerate(top_lessons)) if top_lessons else "_(no lessons recorded yet)_"
                
                identity_content = template.replace('{{project_name}}', os.path.basename(workspace_dir))
                identity_content = identity_content.replace('{{framework}}', 'detected at runtime')
                identity_content = identity_content.replace('{{user_name}}', '_(set during onboarding)_')
                identity_content = identity_content.replace('{{user_role}}', '_(set during onboarding)_')
                identity_content = identity_content.replace('{{timezone}}', time.strftime('%Z'))
                identity_content = identity_content.replace('{{primary_stack}}', '_(extracted from BLUEPRINT.md)_')
                identity_content = identity_content.replace('{{top_lessons}}', lessons_str)
                identity_content = identity_content.replace('{{anti_goals}}', '- Do NOT re-initialize .orion.db repeatedly\n- Do NOT destroy handoff.md during brain sync\n- Do NOT use sed/awk for file modifications')
                identity_content = identity_content.replace('{{timestamp}}', datetime.now().strftime('%Y-%m-%d'))
                
                context_dir_path = os.path.dirname(identity_path)
                if not os.path.exists(context_dir_path):
                    os.makedirs(context_dir_path)
                with open(identity_path, 'w', encoding='utf-8') as f:
                    f.write(identity_content)
                identity_exists = True
                print(f"[IDENTITY] Auto-generated {identity_path}", file=sys.stderr)
            except Exception as e:
                print(f"[IDENTITY] Failed to generate identity: {e}", file=sys.stderr)
    else:
        if os.path.exists(learnings_path):
            with open(learnings_path, 'r', encoding='utf-8') as f:
                learnings_content = f.read()
            top_lessons = extract_top_lessons(learnings_content)
            
            if os.path.exists(identity_path):
                try:
                    with open(identity_path, 'r', encoding='utf-8') as f:
                        old_content = f.read()
                    identity_content = old_content
                        
                    if top_lessons:
                        lessons_str = '\n'.join(f"{i+1}. {l}" for i, l in enumerate(top_lessons))
                        identity_content = re.sub(
                            r'(## Active Lessons \(Top 5\)).*?(?=## |$)', 
                            lambda m: f"{m.group(1)}\n\n{lessons_str}\n\n", 
                            identity_content, flags=re.DOTALL)
                    
                    genome_path = os.path.join(base_agents_dir, ".genome.json")
                    if os.path.exists(genome_path):
                        with open(genome_path, 'r', encoding='utf-8') as gf:
                            genome = json.load(gf)
                        
                        traits = []
                        if genome.get("evolved_skills"):
                            traits.append("- **Evolved Skills**: " + ", ".join(genome["evolved_skills"]))
                        if genome.get("evolved_rules"):
                            traits.append("- **Evolved Rules**: " + ", ".join(genome["evolved_rules"]))
                        if genome.get("pruned_assets"):
                            traits.append("- **Pruned Assets**: " + ", ".join(genome["pruned_assets"]))
                        
                        traits_str = '\n'.join(traits) if traits else "_(no mutations yet)_"
                        
                        if "## Evolutionary Traits" not in identity_content:
                            identity_content = identity_content.replace(
                                "## Anti-Goals", 
                                f"## Evolutionary Traits\n\n{traits_str}\n\n## Anti-Goals"
                            )
                        else:
                            identity_content = re.sub(
                                r'(## Evolutionary Traits).*?(?=## |$)', 
                                lambda m: f"{m.group(1)}\n\n{traits_str}\n\n", 
                                identity_content, flags=re.DOTALL)
                    
                    if identity_content != old_content:
                        with open(identity_path, 'w', encoding='utf-8') as f:
                            f.write(identity_content)
                        print("[IDENTITY] Synced top lessons and genome traits to AGENT_IDENTITY.md", file=sys.stderr)
                except Exception as e:
                    print(f"[IDENTITY] Failed to write-back identity data: {e}", file=sys.stderr)
                    
    return identity_exists, top_lessons
