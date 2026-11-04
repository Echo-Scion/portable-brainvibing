#!/usr/bin/env python3
"""Design Token Harvester & Catalog Flattener.

Extracts design tokens (colors, typography, spacing) from source code
(Flutter, React/CSS, Tailwind, Python) using stdlib regex parsing, infers
archetypes heuristically or via AI prompts, and flattens DESIGN.md catalogs.

Zero external dependencies (Python 3.10+ standard library floor).
"""

import json
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

EXCLUDED_HARVEST_DIRS = {
    ".git", ".orion", ".scratch", "scratch", ".venv", "venv",
    "node_modules", "build", ".dart_tool", "__pycache__", ".idea", ".vscode"
}

HEX_COLOR_RE = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}\b|0x[0-9a-fA-F]{8}\b|Color\(\s*0x[0-9a-fA-F]{8}\s*\)")
CSS_VAR_RE = re.compile(r"--([a-zA-Z0-9_\-]+)\s*:\s*([^;\}]+)")
FONT_FAMILY_RE = re.compile(r"(?:fontFamily|font-family)\s*[:=]\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)


def hex_to_rgb(hex_str: str) -> Optional[Tuple[int, int, int]]:
    """Converts hex string (#RGB, #RRGGBB, 0xFFRRGGBB) to (r, g, b) tuple."""
    if not hex_str:
        return None
    clean = hex_str.strip().lower()
    if clean.startswith("0x"):
        clean = clean[2:]
        if len(clean) == 8:  # AARRGGBB
            clean = clean[2:]
    elif clean.startswith("#"):
        clean = clean[1:]

    if len(clean) == 3:
        clean = "".join(c * 2 for c in clean)

    if len(clean) == 6:
        try:
            r = int(clean[0:2], 16)
            g = int(clean[2:4], 16)
            b = int(clean[4:6], 16)
            return (r, g, b)
        except ValueError:
            return None
    return None


def calculate_luminance_and_sat(r: int, g: int, b: int) -> Tuple[float, float]:
    """Calculates relative luminance (0.0=black, 1.0=white) and HSL saturation (0.0-1.0)."""
    # Relative luminance per WCAG 2.1
    rs = r / 255.0
    gs = g / 255.0
    bs = b / 255.0

    r_lin = rs / 12.92 if rs <= 0.04045 else math.pow((rs + 0.055) / 1.055, 2.4)
    g_lin = gs / 12.92 if gs <= 0.04045 else math.pow((gs + 0.055) / 1.055, 2.4)
    b_lin = bs / 12.92 if bs <= 0.04045 else math.pow((bs + 0.055) / 1.055, 2.4)

    lum = 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

    # HSL Saturation
    c_max = max(rs, gs, bs)
    c_min = min(rs, gs, bs)
    delta = c_max - c_min
    l_hsl = (c_max + c_min) / 2.0

    if delta == 0:
        sat = 0.0
    else:
        sat = delta / (1.0 - abs(2.0 * l_hsl - 1.0))

    return lum, sat


def harvest_tokens(target_dir: str) -> Dict[str, Any]:
    """Harvests design tokens (colors, fonts) from source code in target_dir."""
    target_path = Path(target_dir).resolve()
    colors_found: List[str] = []
    fonts_found: List[str] = []

    if not target_path.exists():
        return _default_tokens()

    # Walk directory to harvest hex colors & fonts
    files_scanned = 0
    max_files = 200

    for root, dirs, files in os.walk(target_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_HARVEST_DIRS and not d.startswith(".")]
        for f in files:
            if files_scanned >= max_files:
                break
            ext = os.path.splitext(f)[1].lower()
            if ext in (".dart", ".css", ".scss", ".ts", ".tsx", ".js", ".jsx", ".py", ".html", ".yaml", ".yml", ".json"):
                fpath = os.path.join(root, f)
                files_scanned += 1
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                        content = fh.read(50000)  # read up to 50KB per file

                    # Match hex colors
                    for m in HEX_COLOR_RE.finditer(content):
                        raw = m.group(0)
                        if raw.startswith("Color(") or raw.startswith("0x"):
                            match_hex = re.search(r"0x[0-9a-fA-F]{8}", raw)
                            if match_hex:
                                val = match_hex.group(0)[2:]
                                if len(val) == 8:
                                    colors_found.append(f"#{val[2:]}")
                        elif raw.startswith("#"):
                            colors_found.append(raw)

                    # Match font families
                    for font_match in FONT_FAMILY_RE.finditer(content):
                        font_name = font_match.group(1).strip()
                        if font_name and len(font_name) < 40 and font_name not in fonts_found:
                            fonts_found.append(font_name)

                except OSError:
                    pass

    # Deduplicate and rank colors
    unique_colors = list(dict.fromkeys(colors_found))
    canvas_hex = "#0D0F12"
    surface_hex = "#16191E"
    border_hex = "#2A2E37"
    text_primary = "#F3F4F6"
    text_muted = "#9CA3AF"
    accent_hex = "#F59E0B"

    if unique_colors:
        # Group by luminance to find background vs accent
        dark_colors = []
        light_colors = []
        accent_candidates = []

        for c in unique_colors:
            rgb = hex_to_rgb(c)
            if rgb:
                lum, sat = calculate_luminance_and_sat(*rgb)
                if lum < 0.2:
                    dark_colors.append((c, lum))
                elif lum > 0.8:
                    light_colors.append((c, lum))

                if sat > 0.3 and 0.15 < lum < 0.85:
                    accent_candidates.append((c, sat))

        if dark_colors:
            dark_colors.sort(key=lambda x: x[1])  # darkest first
            canvas_hex = dark_colors[0][0]
            if len(dark_colors) > 1:
                surface_hex = dark_colors[1][0]
            else:
                surface_hex = canvas_hex

        if light_colors:
            light_colors.sort(key=lambda x: x[1], reverse=True)  # lightest first
            text_primary = light_colors[0][0]

        if accent_candidates:
            accent_candidates.sort(key=lambda x: x[1], reverse=True)  # most saturated first
            accent_hex = accent_candidates[0][0]

    display_font = fonts_found[0] if fonts_found else "Space Grotesk"
    body_font = fonts_found[1] if len(fonts_found) > 1 else "Inter"
    mono_font = next((f for f in fonts_found if "mono" in f.lower() or "code" in f.lower()), "JetBrains Mono")

    harvested = {
        "canvas_hex": canvas_hex,
        "surface_hex": surface_hex,
        "border_hex": border_hex,
        "text_primary": text_primary,
        "text_muted": text_muted,
        "accent_hex": accent_hex,
        "bg_oklch_or_hex": canvas_hex,
        "text_oklch_or_hex": text_primary,
        "primary_oklch_or_hex": accent_hex,
        "secondary_oklch_or_hex": surface_hex,
        "accent_oklch_or_hex": accent_hex,
        "display_font": display_font,
        "body_font": body_font,
        "mono_font": mono_font,
        "raw_colors_found": unique_colors[:10],
        "raw_fonts_found": fonts_found[:5],
    }

    harvested["detected_archetype"] = infer_archetype_heuristic(harvested)
    return harvested


def _default_tokens() -> Dict[str, Any]:
    return {
        "canvas_hex": "#0D0F12",
        "surface_hex": "#16191E",
        "border_hex": "#2A2E37",
        "text_primary": "#F3F4F6",
        "text_muted": "#9CA3AF",
        "accent_hex": "#F59E0B",
        "bg_oklch_or_hex": "#0D0F12",
        "text_oklch_or_hex": "#F3F4F6",
        "primary_oklch_or_hex": "#F59E0B",
        "secondary_oklch_or_hex": "#16191E",
        "accent_oklch_or_hex": "#F59E0B",
        "display_font": "Space Grotesk",
        "body_font": "Inter",
        "mono_font": "JetBrains Mono",
        "detected_archetype": "dark-industrial",
        "raw_colors_found": [],
        "raw_fonts_found": [],
    }


def infer_archetype_heuristic(tokens: Dict[str, Any]) -> str:
    """Infers the closest matching design archetype (from 12 choices) based on tokens."""
    canvas = tokens.get("canvas_hex", "#0D0F12")
    accent = tokens.get("accent_hex", "#F59E0B")
    fonts = tokens.get("raw_fonts_found", [])

    rgb_canvas = hex_to_rgb(canvas) or (13, 15, 18)
    lum_canvas, _ = calculate_luminance_and_sat(*rgb_canvas)

    rgb_accent = hex_to_rgb(accent) or (245, 158, 11)
    r_a, g_a, b_a = rgb_accent

    # Check font indicators
    font_str = " ".join(fonts).lower()
    is_serif = any(s in font_str for s in ("serif", "newsreader", "playfair", "fraunces", "cormorant"))
    is_mono = any(m in font_str for m in ("mono", "jetbrains", "space mono", "code", "courier"))

    # Dark themes
    if lum_canvas < 0.2:
        if r_a > 200 and g_a > 120 and b_a < 50:  # Amber/Yellow
            return "dark-industrial"
        elif g_a > 150 and b_a > 150 and r_a < 100:  # Cyan/Teal
            return "density-cockpit"
        elif g_a > 150 and r_a < 100 and b_a < 150:  # Emerald/Green
            return "cyber-terminal"
        elif b_a > 150 and r_a > 100:  # Iris/Purple
            return "tactile-ambient"
        else:
            return "dark-industrial"

    # Light / Paper themes
    else:
        if is_serif:
            return "swiss-editorial"
        elif is_mono:
            return "academic-mono"
        elif g_a > 120 and r_a < 100 and b_a < 100:  # Green/Forest
            return "solar-minimal"
        else:
            return "modern-minimal"


def build_ai_infer_prompt(tokens: Dict[str, Any], project_summary: str = "") -> str:
    """Builds a prompt payload for an LLM agent to review harvested tokens and choose an archetype."""
    return f"""You are a Senior UI Design Architect reviewing a codebase to infer its visual design archetype.

Harvested Token Evidence:
- Canvas/Background: {tokens.get('canvas_hex')}
- Surface: {tokens.get('surface_hex')}
- Accent Color: {tokens.get('accent_hex')}
- Fonts Found: {', '.join(tokens.get('raw_fonts_found', [])) or 'Standard Sans'}
- Project Summary: {project_summary or 'General Application'}

Choose exactly ONE archetype from these 12 canonical options:
1. swiss-editorial
2. dark-industrial
3. density-cockpit
4. neo-brutalist
5. tactile-ambient
6. modern-minimal
7. retro-futuristic
8. academic-mono
9. warm-editorial
10. cyber-terminal
11. luxury-atelier
12. solar-minimal

Return JSON strictly in this format:
```json
{{
  "archetype": "<archetype-id>",
  "rationale": "<1-sentence reason based on colors and fonts>"
}}
```"""


def flatten_catalogs(template_text: str, archetype: str, palette: str = "", stack: str = "") -> str:
    """Prunes non-matching rows from Section 1 (Archetype), Section 11 (Palette), Section 12 (Stack)."""
    norm_archetype = (archetype or "dark-industrial").lower().strip().replace(" ", "-")
    norm_palette = (palette or "").lower().strip().replace(" ", "-")
    norm_stack = (stack or "").lower().strip().replace(" ", "-")

    lines = template_text.splitlines()
    pruned_lines = []

    for line in lines:
        # Check Section 1 archetype row tag
        m_arch = re.search(r"<!--\s*row:archetype=([\w\-]+)\s*-->", line)
        if m_arch:
            row_arch = m_arch.group(1).lower()
            if row_arch != norm_archetype:
                continue  # Prune non-matching archetype row

        # Check Section 11 palette row tag
        m_pal = re.search(r"<!--\s*row:palette=([\w\-]+)\s*-->", line)
        if m_pal:
            row_pal = m_pal.group(1).lower()
            if norm_palette and row_pal != norm_palette:
                continue  # Prune non-matching palette row

        # Check Section 12 stack row tag
        m_stk = re.search(r"<!--\s*row:stack=([\w\-]+)\s*-->", line)
        if m_stk:
            row_stk = m_stk.group(1).lower()
            if norm_stack and row_stk != norm_stack:
                continue  # Prune non-matching stack row

        pruned_lines.append(line)

    result = "\n".join(pruned_lines)
    # Set Selected Archetype field in Section 1
    result = re.sub(r"-\s*\*\*Selected Archetype\*\*:\s*`.*?`", f"- **Selected Archetype**: `{norm_archetype}`", result)
    return result
