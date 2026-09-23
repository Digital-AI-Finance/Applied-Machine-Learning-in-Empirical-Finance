"""Generate SVG favicon: neural network visualization.

Based on Dennis's LinkedIn banner: blue glowing nodes on dark navy background.
Architecture: 3 input -> 4 hidden -> 2 hidden -> 1 output.
"""

from pathlib import Path

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "assets" / "images" / "favicon.svg"


def generate_favicon_svg() -> None:
    """Generate SVG favicon with simplified neural network."""
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <defs>
    <radialGradient id="g" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#60a5fa" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#60a5fa" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="32" height="32" rx="6" fill="#0f172a"/>

  <!-- Connections: layer 1 (3) -> layer 2 (4) -->
  <line x1="5" y1="8" x2="13" y2="5" stroke="#60a5fa" stroke-opacity="0.25" stroke-width="0.6"/>
  <line x1="5" y1="8" x2="13" y2="12" stroke="#60a5fa" stroke-opacity="0.25" stroke-width="0.6"/>
  <line x1="5" y1="8" x2="13" y2="20" stroke="#60a5fa" stroke-opacity="0.15" stroke-width="0.5"/>
  <line x1="5" y1="16" x2="13" y2="5" stroke="#60a5fa" stroke-opacity="0.15" stroke-width="0.5"/>
  <line x1="5" y1="16" x2="13" y2="12" stroke="#60a5fa" stroke-opacity="0.25" stroke-width="0.6"/>
  <line x1="5" y1="16" x2="13" y2="20" stroke="#60a5fa" stroke-opacity="0.25" stroke-width="0.6"/>
  <line x1="5" y1="16" x2="13" y2="27" stroke="#60a5fa" stroke-opacity="0.15" stroke-width="0.5"/>
  <line x1="5" y1="24" x2="13" y2="12" stroke="#60a5fa" stroke-opacity="0.15" stroke-width="0.5"/>
  <line x1="5" y1="24" x2="13" y2="20" stroke="#60a5fa" stroke-opacity="0.25" stroke-width="0.6"/>
  <line x1="5" y1="24" x2="13" y2="27" stroke="#60a5fa" stroke-opacity="0.25" stroke-width="0.6"/>

  <!-- Connections: layer 2 (4) -> layer 3 (2) -->
  <line x1="13" y1="5" x2="21" y2="11" stroke="#60a5fa" stroke-opacity="0.25" stroke-width="0.6"/>
  <line x1="13" y1="5" x2="21" y2="21" stroke="#60a5fa" stroke-opacity="0.15" stroke-width="0.5"/>
  <line x1="13" y1="12" x2="21" y2="11" stroke="#60a5fa" stroke-opacity="0.25" stroke-width="0.6"/>
  <line x1="13" y1="12" x2="21" y2="21" stroke="#60a5fa" stroke-opacity="0.2" stroke-width="0.5"/>
  <line x1="13" y1="20" x2="21" y2="11" stroke="#60a5fa" stroke-opacity="0.2" stroke-width="0.5"/>
  <line x1="13" y1="20" x2="21" y2="21" stroke="#60a5fa" stroke-opacity="0.25" stroke-width="0.6"/>
  <line x1="13" y1="27" x2="21" y2="11" stroke="#60a5fa" stroke-opacity="0.15" stroke-width="0.5"/>
  <line x1="13" y1="27" x2="21" y2="21" stroke="#60a5fa" stroke-opacity="0.25" stroke-width="0.6"/>

  <!-- Connections: layer 3 (2) -> layer 4 (1) -->
  <line x1="21" y1="11" x2="28" y2="16" stroke="#60a5fa" stroke-opacity="0.3" stroke-width="0.7"/>
  <line x1="21" y1="21" x2="28" y2="16" stroke="#60a5fa" stroke-opacity="0.3" stroke-width="0.7"/>

  <!-- Nodes layer 1: input (3) -->
  <circle cx="5" cy="8" r="2" fill="#60a5fa"/>
  <circle cx="5" cy="8" r="0.9" fill="#b4d2ff"/>
  <circle cx="5" cy="16" r="2" fill="#60a5fa"/>
  <circle cx="5" cy="16" r="0.9" fill="#b4d2ff"/>
  <circle cx="5" cy="24" r="2" fill="#60a5fa"/>
  <circle cx="5" cy="24" r="0.9" fill="#b4d2ff"/>

  <!-- Nodes layer 2: hidden (4) -->
  <circle cx="13" cy="5" r="2" fill="#60a5fa"/>
  <circle cx="13" cy="5" r="0.9" fill="#b4d2ff"/>
  <circle cx="13" cy="12" r="2" fill="#60a5fa"/>
  <circle cx="13" cy="12" r="0.9" fill="#b4d2ff"/>
  <circle cx="13" cy="20" r="2" fill="#60a5fa"/>
  <circle cx="13" cy="20" r="0.9" fill="#b4d2ff"/>
  <circle cx="13" cy="27" r="2" fill="#60a5fa"/>
  <circle cx="13" cy="27" r="0.9" fill="#b4d2ff"/>

  <!-- Nodes layer 3: hidden (2) -->
  <circle cx="21" cy="11" r="2" fill="#60a5fa"/>
  <circle cx="21" cy="11" r="0.9" fill="#b4d2ff"/>
  <circle cx="21" cy="21" r="2" fill="#60a5fa"/>
  <circle cx="21" cy="21" r="0.9" fill="#b4d2ff"/>

  <!-- Nodes layer 4: output (1) -->
  <circle cx="28" cy="16" r="2.2" fill="#60a5fa"/>
  <circle cx="28" cy="16" r="1" fill="#b4d2ff"/>
</svg>"""

    OUTPUT_PATH.write_text(svg)
    print(f"Favicon saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_favicon_svg()
