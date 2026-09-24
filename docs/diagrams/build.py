#!/usr/bin/env python3
"""Generate README diagrams (light + dark) as self-contained HTML, following the diagram-design system.

Usage:
    python3 docs/diagrams/build.py            # writes docs/diagrams/*.html
    python3 docs/diagrams/render.py           # rasterizes them into docs/assets/*.png
"""
import re
from pathlib import Path

OUT = Path(__file__).parent

PALETTES = {
    "light": dict(
        paper="#f5f5f5", node="#ffffff", ink="#2d3142", muted="#4f5d75", soft="#7a8399",
        rule="rgba(45,49,66,0.12)", accent="#eb6c36", accent_tint="rgba(235,108,54,0.08)",
        store="rgba(45,49,66,0.05)", ext="rgba(45,49,66,0.03)", ext_stroke="rgba(45,49,66,0.30)",
        tag_opus="rgba(46,90,168,0.85)", zone="rgba(45,49,66,0.02)", zone_stroke="rgba(45,49,66,0.25)",
    ),
    "dark": dict(
        paper="#2d3142", node="#393e53", ink="#f5f5f5", muted="#bfc0c0", soft="#8e98ac",
        rule="rgba(245,245,245,0.12)", accent="#f08a59", accent_tint="rgba(240,138,89,0.10)",
        store="rgba(245,245,245,0.05)", ext="rgba(245,245,245,0.03)", ext_stroke="rgba(245,245,245,0.30)",
        tag_opus="rgba(106,149,216,0.95)", zone="rgba(245,245,245,0.02)", zone_stroke="rgba(245,245,245,0.25)",
    ),
}

SANS = "'Geist', system-ui, sans-serif"
MONO = "'Geist Mono', ui-monospace, monospace"
SERIF = "'Instrument Serif', Georgia, serif"


class Svg:
    def __init__(self, p):
        self.p = p
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    # ---- primitives -------------------------------------------------------
    def line(self, x1, y1, x2, y2, accent=False, dashed=False, marker=True):
        c = self.p["accent"] if accent else self.p["muted"]
        m = f' marker-end="url(#{"arrow-accent" if accent else "arrow"})"' if marker else ""
        d = ' stroke-dasharray="5,4"' if dashed else ""
        w = 1.4 if accent else 1.2
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"{d}{m}/>')

    def path(self, d, accent=False, dashed=False, marker=True):
        c = self.p["accent"] if accent else self.p["muted"]
        m = f' marker-end="url(#{"arrow-accent" if accent else "arrow"})"' if marker else ""
        da = ' stroke-dasharray="5,4"' if dashed else ""
        w = 1.4 if accent else 1.2
        self.add(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}"{da}{m}/>')

    def label(self, cx, y, text, accent=False, width=None):
        """Arrow label: mask rect whose bottom edge sits at y (keep >= 6px above the stroke)."""
        w = width or (len(text) * 6 + 12)
        w = w + (-w % 4)
        c = self.p["accent"] if accent else self.p["soft"]
        self.add(f'<rect x="{cx - w // 2}" y="{y - 12}" width="{w}" height="12" rx="2" fill="{self.p["paper"]}"/>')
        self.add(f'<text x="{cx}" y="{y - 3}" fill="{c}" font-size="8" font-family="{MONO}" '
                 f'text-anchor="middle" letter-spacing="0.08em">{text}</text>')

    def tag(self, x, y, text, color):
        w = len(text) * 6 + 12
        w = w + (-w % 4)
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="12" rx="2" fill="transparent" '
                 f'stroke="{color}" stroke-opacity="0.55" stroke-width="0.8"/>')
        self.add(f'<text x="{x + w / 2}" y="{y + 9}" fill="{color}" font-size="7" font-family="{MONO}" '
                 f'text-anchor="middle" letter-spacing="0.08em">{text}</text>')

    def node(self, x, y, w, h, name, sub=None, tag=None, kind="step", rx=6, sub2=None):
        p = self.p
        fill, stroke, dash = {
            "step": (p["node"], p["ink"], ""),
            "opus": (p["node"], p["tag_opus"], ""),
            "focal": (p["accent_tint"], p["accent"], ""),
            "store": (p["store"], p["muted"], ""),
            "ext": (p["ext"], p["ext_stroke"], ""),
            "stop": (p["ext"], p["ext_stroke"], ' stroke-dasharray="4,3"'),
        }[kind]
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{p["paper"]}"/>')
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1"{dash}/>')
        cx = x + w / 2
        has_tag = tag is not None
        if has_tag:
            tcol = p["tag_opus"] if tag[1] == "opus" else (p["accent"] if tag[1] == "accent" else p["soft"])
            self.tag(x + 8, y + 6, tag[0], tcol)
        lines = [s for s in (sub, sub2) if s]
        block = 14 + 13 * len(lines)
        top = y + h / 2 - block / 2 + (5 if has_tag else 0)
        self.add(f'<text x="{cx}" y="{top + 11}" fill="{p["ink"]}" font-size="12" font-weight="600" '
                 f'font-family="{SANS}" text-anchor="middle">{name}</text>')
        for i, s in enumerate(lines):
            self.add(f'<text x="{cx}" y="{top + 26 + 13 * i}" fill="{p["muted"]}" font-size="9" '
                     f'font-family="{MONO}" text-anchor="middle">{s}</text>')

    def diamond(self, cx, cy, hw, hh, l1, l2):
        p = self.p
        pts = f"{cx},{cy - hh} {cx + hw},{cy} {cx},{cy + hh} {cx - hw},{cy}"
        self.add(f'<polygon points="{pts}" fill="{p["paper"]}"/>')
        self.add(f'<polygon points="{pts}" fill="{p["node"]}" stroke="{p["ink"]}" stroke-width="1"/>')
        self.add(f'<text x="{cx}" y="{cy - 3}" fill="{p["ink"]}" font-size="11" font-weight="600" font-family="{SANS}" text-anchor="middle">{l1}</text>')
        self.add(f'<text x="{cx}" y="{cy + 12}" fill="{p["muted"]}" font-size="9" font-family="{MONO}" text-anchor="middle">{l2}</text>')

    def zone(self, x, y, w, h, text, accent=False):
        p = self.p
        stroke = p["accent"] if accent else p["zone_stroke"]
        op = ' stroke-opacity="0.6"' if accent else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{p["zone"]}" stroke="{stroke}"{op} '
                 f'stroke-width="1" stroke-dasharray="4,4"/>')
        col = p["accent"] if accent else p["soft"]
        self.add(f'<text x="{x + 16}" y="{y + 20}" fill="{col}" font-size="8" font-family="{MONO}" letter-spacing="0.14em">{text}</text>')

    def aside(self, x, y, lines, anchor="start"):
        for i, s in enumerate(lines):
            self.add(f'<text x="{x}" y="{y + 20 * i}" fill="{self.p["ink"]}" font-size="15" font-style="italic" '
                     f'font-family="{SERIF}" text-anchor="{anchor}">{s}</text>')

    def legend(self, y, width, items):
        p = self.p
        self.add(f'<line x1="32" y1="{y}" x2="{width - 32}" y2="{y}" stroke="{p["rule"]}" stroke-width="0.8"/>')
        self.add(f'<text x="32" y="{y + 24}" fill="{p["muted"]}" font-size="8" font-family="{MONO}" letter-spacing="0.18em">LEGEND</text>')
        x = 108
        for kind, text in items:
            iy = y + 16
            if kind == "opus":
                self.tag(x, iy, "OPUS", p["tag_opus"])
                x += 48
            elif kind == "sonnet":
                self.tag(x, iy, "SONNET", p["soft"])
                x += 60
            elif kind == "accent-arrow":
                self.line(x, iy + 6, x + 28, iy + 6, accent=True)
                x += 36
            elif kind == "arrow":
                self.line(x, iy + 6, x + 28, iy + 6)
                x += 36
            elif kind == "dashed":
                self.line(x, iy + 6, x + 28, iy + 6, dashed=True)
                x += 36
            elif kind == "focal":
                self.add(f'<rect x="{x}" y="{iy}" width="24" height="12" rx="6" fill="{p["accent_tint"]}" stroke="{p["accent"]}"/>')
                x += 32
            elif kind == "zone":
                self.add(f'<rect x="{x}" y="{iy}" width="24" height="12" rx="2" fill="none" stroke="{p["zone_stroke"]}" stroke-dasharray="3,3"/>')
                x += 32
            self.add(f'<text x="{x}" y="{iy + 9}" fill="{p["muted"]}" font-size="9" font-family="{SANS}">{text}</text>')
            x += len(text) * 5 + 40

    def render(self, slug, w, h, title, desc):
        p = self.p
        defs = (
            f'<marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">'
            f'<polygon points="0 0, 8 3, 0 6" fill="{p["muted"]}"/></marker>'
            f'<marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">'
            f'<polygon points="0 0, 8 3, 0 6" fill="{p["accent"]}"/></marker>'
        )
        body = "\n    ".join(self.parts)
        return (
            f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-labelledby="{slug}-title {slug}-desc">\n'
            f'    <title id="{slug}-title">{title}</title>\n'
            f'    <desc id="{slug}-desc">{desc}</desc>\n'
            f'    <defs>{defs}</defs>\n'
            f'    <rect width="100%" height="100%" fill="{p["paper"]}"/>\n'
            f'    {body}\n</svg>'
        )


# ---------------------------------------------------------------------------
# 1. /ship pipeline
# ---------------------------------------------------------------------------
def pipeline(p, slug):
    s = Svg(p)
    W, H = 1240, 540
    # zone first (painted under everything)
    s.zone(224, 88, 240, 272, "A/R BATCH · ONE TOOL CALL")

    # arrows
    s.line(180, 228, 240, 228)                                    # preflight -> reviewer-code
    s.path("M 444,156 H 472 Q 480,156 480,164 V 206 Q 480,214 488,214 H 520")   # auditor -> fix
    s.line(444, 228, 520, 228)                                    # code -> fix
    s.path("M 444,300 H 472 Q 480,300 480,292 V 250 Q 480,242 488,242 H 520")   # ux -> fix
    s.line(680, 228, 716, 228)                                    # fix -> gate
    s.line(864, 228, 916, 228)                                    # gate -> docs
    s.label(890, 220, "PASS")
    s.line(1040, 228, 1076, 228)                                  # docs -> PR
    s.line(792, 176, 792, 124)                                    # gate -> stop (up)
    s.label(840, 156, "ROUND 4 FAILS", width=88)
    # the loop: same reviewer, rounds 2-3
    s.path("M 792,280 V 400 Q 792,408 784,408 H 352 Q 344,408 344,400 V 364", accent=True)
    s.label(568, 400, "FAIL · FIX · COMMIT · SENDMESSAGE", accent=True, width=204)

    # nodes
    s.node(40, 200, 140, 56, "Pre-flight", "lint · typecheck", rx=28, kind="ext")
    s.node(244, 128, 200, 56, "auditor", "lens: audit", tag=("OPUS", "opus"), kind="opus")
    s.node(244, 200, 200, 56, "reviewer-code", "lens: code", tag=("OPUS", "opus"), kind="opus")
    s.node(244, 272, 200, 56, "reviewer-ux", "lens: ux · if frontend", tag=("OPUS", "opus"), kind="opus")
    s.node(520, 196, 160, 64, "Fix + commit", "union findings", tag=("SONNET", "soft"))
    s.diamond(792, 228, 76, 52, "Gates pass?", "code ≥9.5 · UX 10")
    s.node(916, 200, 124, 56, "Phase D", "docs sync + gate", tag=("SONNET", "soft"))
    s.node(1076, 200, 132, 56, "Pull request", "Phase S · /push", rx=28, kind="focal")
    s.node(732, 72, 120, 48, "Stop + report", "never loops forever", rx=24, kind="stop")

    s.aside(352, 440, ["Rounds 2–3 continue the same Opus reviewers: no cold start, one stable bar.",
                       "Round 4 brings one fresh reviewer as escalation, then the pipeline stops."])
    s.legend(484, W, [("opus", "read-only reviewer agent"), ("sonnet", "main session writes"),
                      ("accent-arrow", "same reviewer, next round"), ("focal", "deliverable")])
    return W, s.render(slug, W, H, "How /ship works",
                    "Flowchart of the /ship pipeline: pre-flight, a parallel batch of three Opus reviewers, "
                    "a fix-and-commit step, a gate that loops back to the same reviewers until it passes, then docs and a pull request.")


# ---------------------------------------------------------------------------
# 2. Reviewer continuity
# ---------------------------------------------------------------------------
def continuity(p, slug):
    s = Svg(p)
    W, H = 1240, 460
    s.zone(32, 64, 704, 160, "ROUNDS 1–3 · ONE OPUS REVIEWER · CONTEXT KEPT", accent=True)

    s.line(240, 148, 292, 148, accent=True)
    s.label(266, 140, "FIX", accent=True, width=32)
    s.line(476, 148, 528, 148, accent=True)
    s.label(502, 140, "FIX", accent=True, width=32)
    s.line(712, 148, 784, 148)
    s.label(760, 140, "FAIL", width=40)
    s.line(968, 148, 1016, 148)
    s.label(992, 140, "FAIL", width=40)
    # evidence links
    s.line(384, 184, 384, 264, dashed=True, marker=False)
    s.line(620, 184, 620, 264, dashed=True, marker=False)

    s.node(56, 112, 184, 72, "Spawn reviewer", "Agent · name: reviewer-code", tag=("ROUND 1", "opus"), kind="opus")
    s.node(292, 112, 184, 72, "Re-review", "SendMessage · same agent", tag=("ROUND 2", "opus"), kind="opus")
    s.node(528, 112, 184, 72, "Re-review", "SendMessage · same agent", tag=("ROUND 3", "opus"), kind="opus")
    s.node(784, 112, 184, 72, "Fresh reviewer", "escalation · table + SHA", tag=("ROUND 4", "opus"), kind="opus")
    s.node(1016, 124, 184, 48, "Stop + report", "remaining findings", rx=24, kind="stop")

    # evidence card
    s.add(f'<rect x="292" y="264" width="420" height="120" rx="6" fill="{p["paper"]}"/>')
    s.add(f'<rect x="292" y="264" width="420" height="120" rx="6" fill="{p["store"]}" stroke="{p["muted"]}" stroke-width="1"/>')
    s.add(f'<text x="312" y="288" fill="{p["soft"]}" font-size="8" font-family="{MONO}" letter-spacing="0.14em">EVIDENCE RULE · EVERY CONTINUED ROUND</text>')
    rows = [("1", "Quote the post-fix line for each resolved finding"),
            ("2", "Re-read every changed file, list line counts"),
            ("3", "Name one regression check that was not a finding"),
            ("4", "Re-score from scratch, never carry it forward")]
    for i, (n, t) in enumerate(rows):
        y = 316 + 18 * i
        s.add(f'<text x="316" y="{y}" fill="{p["accent"]}" font-size="9" font-family="{MONO}">{n}</text>')
        s.add(f'<text x="332" y="{y}" fill="{p["ink"]}" font-size="12" font-family="{SANS}">{t}</text>')

    s.aside(56, 280, ["A fresh reviewer every", "round cold-starts and", "samples new nits, so", "the score oscillates."])
    s.aside(784, 280, ["Same reviewer = faster", "re-checks and one stable", "bar. Any round that passes", "the gate exits early."])
    s.legend(412, W, [("opus", "code-reviewer agent"), ("accent-arrow", "continued via SendMessage"),
                      ("arrow", "escalate / stop"), ("dashed", "rule applies")])
    return W, s.render(slug, W, H, "Reviewer continuity",
                    "Rounds one to three reuse one Opus reviewer through SendMessage under an evidence rule; "
                    "round four spawns a fresh reviewer as escalation, and a still-failing gate stops and reports.")


# ---------------------------------------------------------------------------
# 3. Who does what
# ---------------------------------------------------------------------------
def roles(p, slug):
    s = Svg(p)
    W, H = 1240, 400
    s.zone(684, 24, 304, 304, "CODE-REVIEWER AGENT · READ-ONLY")

    s.line(160, 136, 224, 136)
    s.line(464, 128, 700, 128, accent=True)
    s.label(582, 120, "SPAWN · SENDMESSAGE", accent=True, width=128)
    s.line(700, 184, 468, 184, dashed=True)
    s.label(584, 176, "FINDINGS FILE", width=92)
    s.line(344, 200, 344, 264)

    s.node(40, 112, 120, 48, "You", "/ship", rx=24, kind="ext")
    s.node(224, 88, 240, 112, "Main session", "orchestrates · fixes", tag=("SONNET", "soft"),
           sub2="lint · commits · push")
    for i, (name, lens) in enumerate([("auditor", "lens: audit"), ("reviewer-code", "lens: code"),
                                      ("reviewer-ux", "lens: ux"), ("reviewer-docs", "lens: docs")]):
        s.node(708, 56 + 64 * i, 256, 52, name, lens, tag=("OPUS", "opus"), kind="opus")
    s.node(264, 264, 160, 48, "Pull request", "human reviews", rx=24, kind="focal")

    s.aside(1012, 116, ["Reviewers never write.", "The session that fixes", "is never the one", "that grades."])
    s.legend(352, W, [("opus", "judges (read-only)"), ("sonnet", "builds (writes)"),
                      ("accent-arrow", "work handed out"), ("dashed", "verdict returned")])
    return W, s.render(slug, W, H, "Opus judges, Sonnet builds",
                    "The Sonnet main session spawns and continues read-only Opus reviewer agents, "
                    "reads their verdicts from a findings file, applies fixes, and opens the pull request.")


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: {paper}; }}
    svg {{ display: block; width: {w}px; }}
  </style>
</head>
<body>
{svg}
</body>
</html>
"""

if __name__ == "__main__":
    for name, fn in [("ship-pipeline", pipeline), ("reviewer-continuity", continuity), ("roles", roles)]:
        for theme, pal in PALETTES.items():
            slug = name if theme == "light" else f"{name}-dark"
            width, svg = fn(pal, slug)
            title = re.search(r"<title[^>]*>([^<]*)</title>", svg).group(1)
            (OUT / f"{slug}.html").write_text(HTML.format(title=title, paper=pal["paper"], w=width, svg=svg))
            print("wrote", slug)
