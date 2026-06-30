import os
import re
import sys
import argparse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# The script functions as a Manual Aesthetic Lint for the "Creative Technologist"
# It specifically rejects generic solutions in UI files to enforce high-fidelity output.

def scan_file_for_aesthetics(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    errors = []
    warnings = []

    # Check 1: Generic Flutter Colors
    # Catch things like Colors.red, Colors.blue, but intentionally exclude safe utilities like transparent/white/black if they are just for masks
    generic_colors = re.findall(r'(Colors\.(?:red|blue|green|yellow|purple|orange|pink|teal|cyan|indigo|brown|lime|amber))(?!\.shade)', content)
    if generic_colors:
        errors.append(f"Hardcoded generic color found: {', '.join(set(generic_colors))}. Use Theme data or designated 'Liquid Glass' color tokens.")

    # Check 2: Inline React/Next.js styles with generic colors
    inline_styles = re.findall(r'style=\{\{\s*color:\s*[\'"](?:red|blue|green|yellow|purple)[\'"]', content)
    if inline_styles:
        errors.append(f"Inline CSS with generic colors found. Use design system variables or predefined Tailwind classes.")
        
    # Check 3: Raw hex codes that aren't mapped to a semantic variable
    # We only error on these if we see a lot of them, or we can just issue a warning for now
    raw_hexes = re.findall(r'(0xFF[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{6})', content)
    if len(raw_hexes) > 5:
        warnings.append(f"High usage of raw hex codes ({len(raw_hexes)} found). Consider extracting these to semantic design tokens.")

    if errors:
        print(f"❌ [AESTHETIC VIOLATION] {os.path.basename(filepath)}")
        for e in errors:
            print(f"   - {e}")
        return False
    else:
        # Check for micro-interactions / animations (Warning level)
        has_animation = bool(re.search(r'(AnimatedContainer|Tween|AnimationController|Duration|AnimatedOpacity|motion|framer-motion|transition-all)', content, re.IGNORECASE))
        
        # We only really expect animations in Custom UI components, not simple utilities or models, so we check if file sounds like a UI widget
        is_ui_component = bool(re.search(r'(Widget|Component|View|Screen|Button|Card)', content, re.IGNORECASE))
        
        if is_ui_component and not has_animation:
            warnings.append("No micro-interactions or animation primitives detected in a UI component. Ensure the interface feels responsive and premium.")
            
        print(f"✅ [AESTHETIC PASS] {os.path.basename(filepath)}")
        for w in warnings:
            print(f"   ⚠️ {w}")
        return True

def run_audit(target_dir="."):
    print("🎨 Initiating Manual Aesthetic Lint...")
    files_to_scan = []
    
    for root, _, files in os.walk(target_dir):
        # Ignore system directories and builds
        if any(ignored in root for ignored in [".agents", ".git", "node_modules", "build", ".dart_tool"]): 
            continue
        for file in files:
            if file.endswith((".dart", ".tsx", ".jsx", ".css")):
                files_to_scan.append(os.path.join(root, file))

    if not files_to_scan:
        print("ℹ️ No UI files found to scan in the target directory.")
        return

    failed = 0
    for f in files_to_scan:
        if not scan_file_for_aesthetics(f):
            failed += 1

    if failed > 0:
        print(f"\n❌ Aesthetic Audit Failed. {failed} files violated the Creative Technologist standards.")
        print("ACTION REQUIRED: Refactor the offending components to use premium design tokens and remove generic styling.")
        sys.exit(1)
    else:
        print(f"\n✨ Aesthetic Audit Passed. All scanned components comply with foundational design constraints.")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit codebase for aesthetic constraints.")
    parser.add_argument("--dir", default=".", help="Directory to scan (default is current directory)")
    args = parser.parse_args()
    run_audit(args.dir)