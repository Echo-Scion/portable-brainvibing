# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Native Aesthetic & Design Fidelity Evaluator for .agents
Audits codebase for purposeful design tokens, animation primitives,
state completeness, comment hygiene, and WCAG 2.x contrast ratios.
"""
import os
import re
import sys
import json
import argparse

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# --- WCAG 2.x MATHEMATICAL CONTRAST ENGINE ---

def parse_hex(val: str):
    val = val.strip().lstrip("#")
    if len(val) == 3:
        val = "".join(c * 2 for c in val)
    if not re.fullmatch(r"[0-9A-Fa-f]{6}", val):
        raise ValueError(f"Invalid hex color format: {val}")
    return tuple(int(val[i:i+2], 16) for i in (0, 2, 4))

def linearize(c: int) -> float:
    v = c / 255.0
    return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

def relative_luminance(rgb) -> float:
    r, g, b = (linearize(ch) for ch in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast_ratio(c1, c2) -> float:
    l1 = relative_luminance(c1)
    l2 = relative_luminance(c2)
    brightest = max(l1, l2)
    darkest = min(l1, l2)
    return (brightest + 0.05) / (darkest + 0.05)

def audit_contrast_cli(fg_str: str, bg_str: str) -> bool:
    try:
        fg = parse_hex(fg_str)
        bg = parse_hex(bg_str)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return False

    ratio = contrast_ratio(fg, bg)
    pass_normal = ratio >= 4.5
    pass_large = ratio >= 3.0

    print("=" * 45)
    print(" 🎨 WCAG 2.x CONTRAST RATIO AUDIT")
    print("=" * 45)
    print(f"Foreground   : {fg_str}")
    print(f"Background   : {bg_str}")
    print(f"Ratio        : {ratio:.2f}:1")
    print(f"Normal Text  : {'PASS (>= 4.5:1)' if pass_normal else 'FAIL (< 4.5:1)'}")
    print(f"Large Text   : {'PASS (>= 3.0:1)' if pass_large else 'FAIL (< 3.0:1)'}")
    print("=" * 45)
    return pass_normal and pass_large

# --- AESTHETIC & CRAFT SCANNER ---

GENERIC_GRADIENT_PATTERNS = [
    re.compile(r'(?:from-indigo-\d+\s+to-purple-\d+|from-purple-\d+\s+to-pink-\d+|from-cyan-\d+\s+to-blue-\d+)', re.IGNORECASE),
    re.compile(r'linear-gradient\s*\([^)]*#(?:6366f1|a855f7|ec4899|3b82f6|06b6d4)[^)]*\)', re.IGNORECASE),
]

TAUTOLOGICAL_COMMENT_PATTERNS = [
    re.compile(r'//\s*(?:set|initialize|increment|decrement)\s+\w+\s+to\s+\w+', re.IGNORECASE),
    re.compile(r'//\s*(?:return|returns)\s+(?:true|false|null|result|data)', re.IGNORECASE),
]

ASCII_BANNER_PATTERNS = [
    re.compile(r'//\s*[=\-_*~]{5,}'),
    re.compile(r'/\*\s*[=\-_*~]{5,}'),
]

SPARKLE_ICON_PATTERNS = re.compile(r'<(?:Sparkles?|Wand2?|MagicWand|FaMagic|RiMagicLine)\b', re.IGNORECASE)
ITALIC_HEADING_PATTERNS = re.compile(r'<h[1-6][^>]*>[^<]*<(?:em|i|span\s+class="[^"]*italic[^"]*")[^>]*>.*?</(?:em|i|span)>.*?</h[1-6]>', re.IGNORECASE)
FAKE_CHROME_PATTERNS = re.compile(r'(?:bg-red-500\s+rounded-full.*bg-yellow-500.*bg-green-500|window-controls|traffic-lights|mock-browser)', re.IGNORECASE)

EMOJI_ICON_TELL_PATTERNS = re.compile(r'[\u2728\U0001F680\u26A1\U0001F525\U0001F3AF\u2705]', re.UNICODE)
RE_ARBITRARY_SPACING = re.compile(r'\b(margin|padding|gap):\s*([0-9]+)px', re.IGNORECASE)
ALLOWED_8PT_STEPS = {0, 1, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 56, 64, 80, 96, 128}

AESTHETIC_DEGENERACY_RULES = [
    (re.compile(r'\btransition-all\b', re.IGNORECASE), "Visual Craft Violation: Use specific transition properties (e.g., transition-colors) instead of broad 'transition-all'."),
    (re.compile(r'\bhover:scale-10[1-9]\b', re.IGNORECASE), "Visual Craft Violation: Universal hover:scale-* detected. Pick one purposeful interactive signal instead of generic scaling."),
    (re.compile(r'cubic-bezier\([^)]*1\.[1-9][^)]*\)', re.IGNORECASE), "Visual Craft Violation: Bouncy overshoot easing detected on UI state. Use standard ease-out transitions."),
    (re.compile(r'(?:z-index:\s*999+|z-\[999+\])', re.IGNORECASE), "Visual Craft Violation: Arbitrary high z-index (999+) detected. Use a constrained layering token scale."),
    (re.compile(r'(?:width:\s*100vw\b|\bw-screen\b)', re.IGNORECASE), "Visual Craft Violation: 100vw/w-screen detected. Use 100% or container width to prevent horizontal scrollbar breaking."),
    (re.compile(r'\bh-screen\b', re.IGNORECASE), "Visual Craft Violation: 'h-screen' causes mobile viewport jumping on address bar collapse. Use 'min-h-[100dvh]' instead."),
    (re.compile(r'(?:Lottie|@lottiefiles/lottie-player)', re.IGNORECASE), "Visual Craft Violation: External Lottie player detected. Build native CSS/SVG animations instead."),
    (re.compile(r'\b(?:Fraunces|Instrument[\s_-]Serif)\b', re.IGNORECASE), "Visual Craft Violation: Generic default AI display serif detected. Default to sans display, or use project-specific typography."),
    (re.compile(r'box-shadow:\s*0\s+0\s+[0-9]+px', re.IGNORECASE), "Visual Craft Violation: Zero-offset glowing shadow halo detected. Shadows must carry realistic vertical offset and soft blur."),
    (re.compile(r'(?:transition:\s*[^;]*(?:\bwidth\b|\bheight\b|\btop\b|\bleft\b|\bbottom\b|\bright\b|\bmargin\b|\bpadding\b)|transition-(?:\[?(?:width|height|margin|spacing)\]?))\b', re.IGNORECASE), "Motion Performance Violation: Animating layout property detected (width/height/top/left/margin/padding triggers layout reflow). Use compositor properties ('transform', 'opacity') with FLIP technique."),
    (re.compile(r'will-change:\s*all\b', re.IGNORECASE), "Motion Performance Violation: 'will-change: all' causes GPU layer explosion. Use 'will-change: transform, opacity' surgically on active interaction."),
    (re.compile(r'\b(?:unlock|elevate|empower|delve|showcase|testament|robust|game-changer|next-level|seamless|cutting-edge|revolutionary|pivotal moment|new era of|tapestry|beacon|undeniably|unwavering|paramount|cornerstone|foster|harness|holistic|paradigm|synergy|streamline)\b', re.IGNORECASE), "Copy Truth Violation: Empty AI hype vocabulary or Tier-1/2 AI tells detected. Use concrete, evidenced language."),
    (re.compile(r'["\'](?:Jane Doe|John Smith|Acme|Nexus|Pulse|Unleash|Supercharge)["\']', re.IGNORECASE), "Copy Truth Violation: Generic placeholder names or startup-cliché copy detected. Use concrete, domain-specific names."),
    (re.compile(r'(?:not\s+(?:only|just|merely)\s+[^,.\n]+,?\s+but\b|it\'s\s+not\s+[^,.\n]+,?\s+it\'s\b)', re.IGNORECASE), "Copy Truth Violation: Staged Not-X-but-Y contrast detected. State the positive claim directly."),
    (re.compile(r'\b(?:let\'s\s+dive\s+in|let\'s\s+explore|here\'s\s+what\s+you\s+need\s+to\s+know|at\s+its\s+core|let\s+that\s+sink\s+in|that\s+is\s+the\s+real\s+win|read\s+that\s+again|make\s+no\s+mistake)\b', re.IGNORECASE), "Copy Truth Violation: Staged throat-clearing opener or dramatic fragment closer detected."),
    (re.compile(r'\b(?:as\s+of\s+my\s+(?:last\s+update|knowledge\s+cutoff)|i\s+hope\s+this\s+helps)\b', re.IGNORECASE), "Copy Truth Violation: P0 Chatbot conversational leftover or cutoff disclaimer detected."),
]

def _load_canonical_jargon_pattern():
    lexicon_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "canons", "lexicons", "jargon_dict.json"))
    if os.path.exists(lexicon_path):
        try:
            with open(lexicon_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            words = list(data.get("replacements", {}).keys())
            if words:
                escaped = [re.escape(w) for w in words]
                return re.compile(r'\b(?:' + '|'.join(escaped) + r')\b', re.IGNORECASE)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            pass
    return None

_DYNAMIC_JARGON = _load_canonical_jargon_pattern()
if _DYNAMIC_JARGON:
    AESTHETIC_DEGENERACY_RULES.append(
        (_DYNAMIC_JARGON, "Copy Truth Violation: Corporate buzzword or AI tell detected from canonical jargon dictionary. Replace with direct plain English.")
    )

def scan_file_for_aesthetics(filepath: str, strict: bool = False) -> bool:
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    errors = []
    warnings = []

    # 1. Hardcoded generic framework colors
    generic_colors = re.findall(r'(Colors\.(?:red|blue|green|yellow|purple|orange|pink|teal|cyan|indigo|brown|lime|amber))(?!\.shade)', content)
    if generic_colors:
        errors.append(f"Hardcoded generic color found: {', '.join(set(generic_colors))}. Use theme data or semantic color tokens.")

    # 2. Inline styles with generic colors
    inline_styles = re.findall(r'style=\{\{\s*color:\s*[\'"](?:red|blue|green|yellow|purple)[\'"]', content)
    if inline_styles:
        errors.append("Inline CSS with generic colors found. Use design system variables or predefined tokens.")

    # 3. Excessive raw hex codes
    raw_hexes = re.findall(r'(0xFF[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{6})', content)
    if len(raw_hexes) > 8:
        warnings.append(f"High usage of raw hex codes ({len(raw_hexes)} found). Consider extracting to semantic tokens in DESIGN.md.")

    # 4. Generic gradient cliches
    for pat in GENERIC_GRADIENT_PATTERNS:
        if pat.search(content):
            warnings.append("Generic default hero gradient detected (indigo-purple/cyan-blue). Ensure palette is derived from authentic project DESIGN.md.")
            break

    # 5. Gratuitous AI ornamentation icons
    if SPARKLE_ICON_PATTERNS.search(content):
        warnings.append("Sparkle/Magic Wand icon detected. Verify icon represents an actual interactive domain function, not decorative filler.")

    # 6. Comment hygiene (tautological comments and ASCII banners)
    for pat in TAUTOLOGICAL_COMMENT_PATTERNS:
        if pat.search(content):
            warnings.append("Tautological comment detected. Remove comments that merely restate code syntax.")
            break

    for pat in ASCII_BANNER_PATTERNS:
        if pat.search(content):
            warnings.append("ASCII decorative box or banner detected. Keep code comments clean and minimal.")
            break

    # 7. Micro-interactions / animation check for UI components
    is_ui_component = bool(re.search(r'(Widget|Component|View|Screen|Button|Card|Navbar|Modal)', content, re.IGNORECASE))
    has_animation = bool(re.search(r'(AnimatedContainer|Tween|AnimationController|Duration|AnimatedOpacity|motion|framer-motion|transition-all|transition-colors|transition-opacity|animate-)', content, re.IGNORECASE))
    if is_ui_component and not has_animation:
        warnings.append("No micro-interactions or animation primitives detected in UI component. Verify responsive tactile feedback.")

    # 8. Italicized display heading emphasis (AI trope)
    if ITALIC_HEADING_PATTERNS.search(content):
        warnings.append("Italicized emphasis word detected inside display heading. Keep display headings upright roman; carry emphasis via weight or color tokens.")

    # 9. Re-drawn fake browser or phone chrome
    if FAKE_CHROME_PATTERNS.search(content):
        warnings.append("Simulated browser/device chrome detected (traffic-light dots/fake URL bar). Allow real OS/browser to render natural chrome.")

    # 10. Oversized card radii or arbitrary non-scale spacing
    if re.search(r'(?:rounded-(?:3xl|\[(?:[3-9]\d|\d{3,})px\])|border-radius:\s*(?:[3-9]\d|\d{3,})px)', content, re.IGNORECASE):
        warnings.append("Oversized container radius detected (>=30px). Enforce restrained 8-12px radius on cards to prevent AI pill-shape slop.")

    # 11. Visual Craft & Restraint Check (Animation, Spacing, Typography Tropes)
    for pat, msg in AESTHETIC_DEGENERACY_RULES:
        if pat.search(content):
            warnings.append(msg)

    # 12. Emoji icon tell check
    if EMOJI_ICON_TELL_PATTERNS.search(content):
        warnings.append("Emoji glyph icon detected in markup (✨/🚀/⚡/🔥/🎯/✅). Use purposeful SVG icon tokens or lead with typography.")

    # 13. 8pt Modular Spacing Grid Check (Arbitrary Spacing Detection)
    for match in RE_ARBITRARY_SPACING.finditer(content):
        prop, val_str = match.group(1), match.group(2)
        val = int(val_str)
        if val not in ALLOWED_8PT_STEPS:
            warnings.append(f"Arbitrary spacing '{prop}: {val}px' detected. Enforce 8pt modular grid (4/8/12/16/24/32/48/64px).")
            break

    # 14. Accessibility: Icon-only button without accessible name check
    icon_only_buttons = re.findall(r'<button\b(?![^>]*\baria-label)(?![^>]*\baria-labelledby)(?![^>]*\btitle)[^>]*>\s*<(?:[A-Z]\w*(?:Icon|Svg)|svg)\b[^>]*>(?:(?!</button>).)*?</button>', content, re.IGNORECASE | re.DOTALL)
    if icon_only_buttons:
        warnings.append(f"Accessible Name Violation: Icon-only button detected without accessible name ({len(icon_only_buttons)} instance(s)). Add 'aria-label', 'aria-labelledby', or screen-reader text.")


    if errors:
        print(f"❌ [AESTHETIC VIOLATION] {os.path.basename(filepath)}")
        for e in errors:
            print(f"   - {e}")
        return False
    else:
        print(f"✅ [AESTHETIC PASS] {os.path.basename(filepath)}")
        for w in warnings:
            print(f"   ⚠️ {w}")
        return len(warnings) == 0 if strict else True

BINARY_REVERSAL_PATTERNS = [
    re.compile(r"\bnot\s+because\s+[^,.\n]+,\s+but\s+because\b", re.IGNORECASE),
    re.compile(r"\bisn't\s+(?:just\s+)?about\s+[^,.\n]+,\s+it's\s+about\b", re.IGNORECASE),
    re.compile(r"\bthe\s+(?:problem|answer|question)\s+isn't\s+[^,.\n]+\.\s+it's\b", re.IGNORECASE),
    re.compile(r"\bstops\s+being\s+[^,.\n]+\s+and\s+starts\s+being\b", re.IGNORECASE),
]

FALSE_AGENCY_PATTERNS = [
    re.compile(r"\bthe\s+(?:schema|function|module|bug|database)\s+(?:decided|wants|tries|attempts|hopes)\s+to\b", re.IGNORECASE),
]

def scan_markdown_for_slop(filepath: str, strict: bool = False) -> bool:
    """Mechanically enforces prose-authenticity.md on Markdown documentation (ignoring code blocks)."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.read()

    # Strip YAML frontmatter and fenced/inline code blocks (100% immutable per prose-authenticity.md §4)
    prose = re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", raw, flags=re.DOTALL)
    prose = re.sub(r"```.*?```", "", prose, flags=re.DOTALL)
    prose = re.sub(r"`[^`\n]+`", "", prose)

    warnings = []
    for pat in BINARY_REVERSAL_PATTERNS:
        m = pat.search(prose)
        if m:
            warnings.append(f"Binary Contrast Reversal detected ('{m.group(0)}'). State the positive assertion directly.")
            break

    for pat in FALSE_AGENCY_PATTERNS:
        m = pat.search(prose)
        if m:
            warnings.append(f"False Agency detected ('{m.group(0)}'). Inanimate code cannot want/try/decide.")
            break

    em_dash_count = prose.count("\u2014")
    if em_dash_count > 4:
        warnings.append(f"Em-dash overuse detected ({em_dash_count} instances). Use colons, commas, or periods.")

    if _DYNAMIC_JARGON:
        jargon_hits = set(m.group(0).lower() for m in _DYNAMIC_JARGON.finditer(prose))
        if jargon_hits:
            warnings.append(f"AI Tell / Corporate Jargon detected: {', '.join(sorted(jargon_hits))}.")

    if warnings:
        print(f"⚠️ [PROSE SLOP WARN] {os.path.basename(filepath)}")
        for w in warnings:
            print(f"   - {w}")
        return False if strict else True
    else:
        print(f"✅ [PROSE PASS] {os.path.basename(filepath)}")
        return True

def run_audit(target_dir: str = ".", strict: bool = False) -> int:
    print(f"🎨 Initiating Aesthetic & Craft Audit in '{os.path.abspath(target_dir)}'...")
    ui_files = []
    md_files = []

    if os.path.isfile(target_dir):
        if target_dir.endswith((".dart", ".tsx", ".jsx", ".css", ".html", ".vue")):
            ui_files.append(target_dir)
        elif target_dir.endswith(".md"):
            md_files.append(target_dir)
    else:
        for root, _, files in os.walk(target_dir):
            if any(ignored in root for ignored in [".git", "node_modules", "build", ".dart_tool", "scratch"]):
                continue
            if ".agents" in root and target_dir != ".agents" and not target_dir.startswith(".agents"):
                continue
            for file in files:
                if file.endswith((".dart", ".tsx", ".jsx", ".css", ".html", ".vue")):
                    ui_files.append(os.path.join(root, file))
                elif file.endswith(".md"):
                    md_files.append(os.path.join(root, file))

    if not ui_files and not md_files:
        print("ℹ️ No UI or Markdown files found to scan in the target directory.")
        return 0

    failed = 0
    for f in ui_files:
        if not scan_file_for_aesthetics(f, strict=strict):
            failed += 1

    for f in md_files:
        if not scan_markdown_for_slop(f, strict=strict):
            failed += 1

    if failed > 0:
        print(f"\n❌ Aesthetic Audit Failed. {failed} files violated foundational design constraints.")
        return 1
    else:
        print("\n✨ Aesthetic Audit Passed. All scanned components comply with foundational design constraints.")
        return 0

def main():
    parser = argparse.ArgumentParser(description="Audit codebase for aesthetics, craft constraints, and contrast.")
    parser.add_argument("--dir", default=None, help="Directory to scan (default is current directory)")
    parser.add_argument("--strict", action="store_true", help="Enforce strict blocking mode: treat warnings as failures")
    parser.add_argument("--contrast", nargs=2, metavar=("FG", "BG"), help="Audit WCAG 2.x contrast ratio between two hex colors")
    parser.add_argument("colors", nargs="*", help="Positional colors for contrast check (e.g. #000000 #FFFFFF)")
    args = parser.parse_args()

    if args.contrast:
        success = audit_contrast_cli(args.contrast[0], args.contrast[1])
        sys.exit(0 if success else 1)

    if args.colors and len(args.colors) == 2:
        success = audit_contrast_cli(args.colors[0], args.colors[1])
        sys.exit(0 if success else 1)

    target = args.dir if args.dir is not None else "."
    sys.exit(run_audit(target, strict=args.strict))

if __name__ == "__main__":
    main()