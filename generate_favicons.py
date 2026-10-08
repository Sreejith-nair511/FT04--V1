#!/usr/bin/env python3
"""
Generate CogniShield favicon PNG files from SVG template.

This script converts the SVG logo to PNG favicons at different sizes.

Requirements:
    pip install pillow cairosvg

Usage:
    python generate_favicons.py
"""

import os
import sys
from pathlib import Path

def generate_favicons():
    """Generate favicon PNG files from SVG"""
    
    try:
        # Try using cairosvg for better SVG rendering
        try:
            import cairosvg
            use_cairo = True
        except ImportError:
            print("cairosvg not installed, trying PIL/Pillow approach...")
            use_cairo = False
            from PIL import Image, ImageDraw
        
        public_dir = Path(__file__).parent / "public"
        svg_path = public_dir / "cognishield-logo.svg"
        
        if not svg_path.exists():
            print(f"Error: {svg_path} not found")
            sys.exit(1)
        
        print("🎨 Generating CogniShield favicons...")
        
        if use_cairo:
            print("Using cairosvg for high-quality rendering...")
            
            # Generate 32x32 favicon
            favicon_32 = public_dir / "cognishield-favicon.png"
            cairosvg.svg2png(
                url=str(svg_path),
                write_to=str(favicon_32),
                output_width=32,
                output_height=32
            )
            print(f"✅ Generated: {favicon_32.name} (32x32)")
            
            # Generate dark variant (same, already supports)
            favicon_32_dark = public_dir / "cognishield-favicon-dark.png"
            cairosvg.svg2png(
                url=str(svg_path),
                write_to=str(favicon_32_dark),
                output_width=32,
                output_height=32
            )
            print(f"✅ Generated: {favicon_32_dark.name} (32x32)")
            
            # Generate Apple icon (180x180)
            apple_icon = public_dir / "cognishield-apple-icon.png"
            cairosvg.svg2png(
                url=str(svg_path),
                write_to=str(apple_icon),
                output_width=180,
                output_height=180
            )
            print(f"✅ Generated: {apple_icon.name} (180x180)")
            
        else:
            print("Using PIL/Pillow (quality may vary)...")
            print("For best results, install cairosvg: pip install cairosvg")
            
            # Simple fallback using PIL
            # Read SVG and create placeholder PNG (basic approach)
            
            # Since PIL doesn't natively support SVG, we'll create a simple blue shield PNG
            from PIL import Image, ImageDraw
            
            def create_shield_png(size: int) -> Image.Image:
                """Create a simple shield PNG"""
                img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                
                # Shield dimensions
                margin = int(size * 0.15)
                shield_points = [
                    (size // 2, margin),  # top point
                    (size - margin, margin + int(size * 0.15)),  # top right
                    (size - margin, size // 2),  # right
                    (size // 2, size - margin),  # bottom
                    (margin, size // 2),  # left
                    (margin, margin + int(size * 0.15)),  # top left
                ]
                
                # Draw shield
                draw.polygon(shield_points, fill=(95, 127, 255, 255))  # Blue shield
                
                # Draw checkmark
                check_offset = size // 3
                draw.line(
                    [(size // 2 - check_offset, size // 2),
                     (size // 2 - int(check_offset * 0.3), size // 2 + int(check_offset * 0.4)),
                     (size // 2 + check_offset, size // 2 - int(check_offset * 0.4))],
                    fill=(255, 255, 255, 255),
                    width=max(2, size // 20)
                )
                
                return img
            
            # Generate 32x32
            img_32 = create_shield_png(32)
            favicon_32 = public_dir / "cognishield-favicon.png"
            img_32.save(favicon_32, 'PNG')
            print(f"✅ Generated: {favicon_32.name} (32x32)")
            
            # Generate 32x32 dark (same for now)
            favicon_32_dark = public_dir / "cognishield-favicon-dark.png"
            img_32.save(favicon_32_dark, 'PNG')
            print(f"✅ Generated: {favicon_32_dark.name} (32x32)")
            
            # Generate 180x180 Apple icon
            img_180 = create_shield_png(180)
            apple_icon = public_dir / "cognishield-apple-icon.png"
            img_180.save(apple_icon, 'PNG')
            print(f"✅ Generated: {apple_icon.name} (180x180)")
        
        print("\n✨ Favicon generation complete!")
        print(f"📁 Files saved to: {public_dir}/")
        print("\nFavicon files created:")
        print("  - cognishield-favicon.png (light mode, 32x32)")
        print("  - cognishield-favicon-dark.png (dark mode, 32x32)")
        print("  - cognishield-apple-icon.png (Apple touch icon, 180x180)")
        print("\n🎉 Ready to use! Favicons will appear after cache clear.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Install cairosvg: pip install cairosvg pillow")
        print("2. Or use online converter: https://cloudconvert.com/svg-to-png")
        print("3. Or manually create PNG files matching the specifications")
        sys.exit(1)


if __name__ == "__main__":
    generate_favicons()
