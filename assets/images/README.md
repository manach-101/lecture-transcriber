# GUI image assets

```text
cat_hero.png     the original mockup/reference image (kept for reference)
cat_hero_bg.png  the actual GUI background — a crop of cat_hero.png with
                  the marketing sticky notes/captions removed, showing only
                  the raw cat-at-laptop photo
```

The GUI (`src/gui/hero_background.py`) loads `assets/images/cat_hero_bg.png`
as the full-window background. If that file is not present, the GUI falls
back to a plain dark gradient background automatically — no code changes
needed.

To use a different photo, replace `cat_hero_bg.png` directly (or crop a new
mockup and save the clean result under that name). Recommended: a landscape
image at least 1600px wide, free of overlaid text, so it scales cleanly on
larger displays.
