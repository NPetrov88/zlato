#!/usr/bin/env python
"""
Background removal script for ZLATO landing page images.
Uses rembg AI model to extract subjects with transparent backgrounds.

Usage:
    python scripts/remove_bg.py input.png output.png
    python scripts/remove_bg.py input.jpg output.png

Examples:
    # Process bottle image
    python scripts/remove_bg.py media/landing/bottle.png media/landing/bottle-transparent.png

    # Process multiple images
    for img in media/landing/*.jpg; do
        python scripts/remove_bg.py "$img" "${img%.jpg}-transparent.png"
    done
"""

import sys
from pathlib import Path
from rembg import remove
from PIL import Image

def remove_background(input_path: str, output_path: str):
    """Remove background from image and save with transparency."""
    print(f"Processing: {input_path}")

    # Open input image
    input_img = Image.open(input_path)

    # Remove background
    output_img = remove(input_img)

    # Save as PNG with transparency
    output_img.save(output_path, 'PNG')

    print(f"✓ Saved: {output_path}")
    print(f"  Size: {output_img.size}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python remove_bg.py <input_image> <output_image>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # Validate input exists
    if not Path(input_path).exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    remove_background(input_path, output_path)
