# CogniShield Favicon Setup

The favicon has been updated to use CogniShield branding instead of v0 defaults.

## Icon Files Required

Update your public folder with these icon files:

1. **cognishield-logo.svg** ✅ - Already created
2. **cognishield-favicon.png** - 32x32px light theme
3. **cognishield-favicon-dark.png** - 32x32px dark theme  
4. **cognishield-apple-icon.png** - 180x180px for Apple devices

## Option 1: Generate from SVG (Recommended)

### Using Python PIL

```bash
pip install pillow

# Run this script to generate PNGs from the SVG
python generate_favicons.py
```

### Using Online Tool

1. Visit: https://cloudconvert.com/svg-to-png
2. Upload: `public/cognishield-logo.svg`
3. Settings:
   - Format: PNG
   - Width: 32px (for favicon)
   - Height: 32px
4. Download and save as `cognishield-favicon.png`
5. Repeat for 180x180 → `cognishield-apple-icon.png`

### Using ImageMagick

```bash
# Install ImageMagick
brew install imagemagick  # macOS
# or apt-get install imagemagick  # Linux
# or download from https://imagemagick.org/  # Windows

# Generate favicon (32x32)
convert -density 150 -background none cognishield-logo.svg -resize 32x32 cognishield-favicon.png

# Generate dark favicon (same, already handles it)
cp cognishield-favicon.png cognishield-favicon-dark.png

# Generate Apple icon (180x180)
convert -density 150 -background none cognishield-logo.svg -resize 180x180 cognishield-apple-icon.png
```

### Using Figma or Adobe XD

1. Create 32x32 artboard
2. Import or recreate the CogniShield shield logo
3. Export as PNG @ 2x resolution
4. Save as `cognishield-favicon.png`
5. Repeat for 180x180

## Option 2: Use Existing Icons as Base

If you have design tools available:

1. Take the existing `icon-light-32x32.png` and `icon-dark-32x32.png`
2. Rename to:
   - `icon-light-32x32.png` → `cognishield-favicon.png`
   - `icon-dark-32x32.png` → `cognishield-favicon-dark.png`
3. Create `cognishield-apple-icon.png` by scaling up to 180x180

## Quick Fix (Temporary)

If you need the app working immediately:

```bash
# Copy existing icons as fallback
cp public/icon-light-32x32.png public/cognishield-favicon.png
cp public/icon-dark-32x32.png public/cognishield-favicon-dark.png
cp public/apple-icon.png public/cognishield-apple-icon.png
```

This will work but uses v0 icons until proper CogniShield branded icons are ready.

## What Changed

**layout.tsx** now references:
- `/cognishield-favicon.png` - Light mode (32x32)
- `/cognishield-favicon-dark.png` - Dark mode (32x32)
- `/cognishield-logo.svg` - Vector logo
- `/cognishield-apple-icon.png` - Apple touch icon (180x180)

Instead of v0 defaults:
- ~~`/icon-light-32x32.png`~~
- ~~`/icon-dark-32x32.png`~~
- ~~`/apple-icon.png`~~

## Testing

1. Clear browser cache (Ctrl+Shift+Del)
2. Hard refresh (Ctrl+Shift+R)
3. Check tab icon changes to CogniShield logo
4. Check Apple devices recognize icon

## Design Notes

The CogniShield logo features:
- Blue shield gradient (#5f7fe8 → #6f8fff)
- White checkmark symbolizing security/verification
- Subtle circuit pattern representing AI technology
- Scalable SVG base with high-quality PNG exports

## Generated Files Size

- `cognishield-favicon.png`: ~1-2 KB
- `cognishield-favicon-dark.png`: ~1-2 KB
- `cognishield-apple-icon.png`: ~3-5 KB
- Total: ~5-9 KB

## Deployment

Ensure all icon files are in `public/` folder before deploying:

```bash
public/
├── cognishield-logo.svg          ✅
├── cognishield-favicon.png       (generate)
├── cognishield-favicon-dark.png  (generate)
├── cognishield-apple-icon.png    (generate)
├── icon.svg                      (old v0)
└── ... other files ...
```

## Support

- SVG was created with modernized CogniShield branding
- Logo is vector-based for crisp quality at any size
- PNG generation recommended using ImageMagick or online converter
- Contact design team for custom brand variations
