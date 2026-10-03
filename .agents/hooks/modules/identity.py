import os
import json
import time
import re
from datetime import datetime

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
                    lesson_lines = [l.strip() for l in learnings_content.split('\n') 
                                    if l.strip().startswith('- ') and len(l.strip()) > 10]
                    top_lessons = lesson_lines[:5]
                
                lessons_str = '\n'.join(f"{i+1}. {l[2:]}" for i, l in enumerate(top_lessons)) if top_lessons else "_(no lessons recorded yet)_"
                
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
                print(f"[IDENTITY] Auto-generated {identity_path}")
            except Exception as e:
                print(f"[IDENTITY] Failed to generate identity: {e}")
    else:
        if os.path.exists(learnings_path):
            with open(learnings_path, 'r', encoding='utf-8') as f:
                learnings_content = f.read()
            lesson_lines = [l.strip() for l in learnings_content.split('\n') 
                            if l.strip().startswith('- ') and len(l.strip()) > 10]
            top_lessons = [l[2:] for l in lesson_lines[:5]]
            
            if os.path.exists(identity_path):
                try:
                    with open(identity_path, 'r', encoding='utf-8') as f:
                        identity_content = f.read()
                        
                    if top_lessons:
                        lessons_str = '\n'.join(f"{i+1}. {l}" for i, l in enumerate(top_lessons))
                        identity_content = re.sub(
                            r'(## Active Lessons \(Top 5\)).*?(?=## |$)', 
                            f'\\1\n\n{lessons_str}\n\n', 
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
                                f'\\1\n\n{traits_str}\n\n', 
                                identity_content, flags=re.DOTALL)
                        
                    with open(identity_path, 'w', encoding='utf-8') as f:
                        f.write(identity_content)
                    print("[IDENTITY] Synced top lessons and genome traits to AGENT_IDENTITY.md")
                except Exception as e:
                    print(f"[IDENTITY] Failed to write-back identity data: {e}")
                    
    return identity_exists, top_lessons
