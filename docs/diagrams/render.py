#!/usr/bin/env python3
"""Rasterize docs/diagrams/*.html into docs/assets/*.png at 2x with headless Chrome."""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ASSETS = HERE.parent / "assets"
CHROME = next((c for c in [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome", "/usr/bin/chromium",
] if Path(c).exists()), None)

if not CHROME:
    sys.exit("Chrome/Chromium not found")

ASSETS.mkdir(exist_ok=True)
for html in sorted(HERE.glob("*.html")):
    w, h = map(int, re.search(r'viewBox="0 0 (\d+) (\d+)"', html.read_text()).groups())
    out = ASSETS / f"{html.stem}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=2", f"--window-size={w},{h}",
                    "--virtual-time-budget=5000", f"--screenshot={out}", html.resolve().as_uri()],
                   check=True, capture_output=True)
    print("rendered", out.relative_to(HERE.parent.parent))
