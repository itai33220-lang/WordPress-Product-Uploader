# WooCommerce Product Uploader

A local Flask web application that automates uploading products to a WooCommerce bike store (MyBikeStore). It uses Claude AI to generate Hebrew SEO content and Google Custom Search to find square product images from bike retail sites.

## Architecture

Two Python files + a Flask server that serves a single-page app:

- **[uploader.py](uploader.py)** — Flask server + embedded HTML/JS single-page app. Handles all routes, Claude API calls, WooCommerce REST API, and WordPress media uploads.
- **[image_search_square_only.py](image_search_square_only.py)** — Google Custom Search wrapper that fetches and filters for square (1:1 ratio) product images from a curated list of bike retailer sites.

## Running the App

```bash
source venv/bin/activate
python uploader.py
# Open http://localhost:5000 in browser
```

The setup overlay will prompt for credentials on first run. These are stored in browser `localStorage`.

## API Keys Required (configured in UI)

| Key | Purpose |
|-----|---------|
| WooCommerce Consumer Key + Secret | WooCommerce REST API (`/wp-json/wc/v3/`) |
| Anthropic API Key (`sk-ant-...`) | Claude `claude-3-haiku-20240307` for content generation |
| Google API Key + Search Engine ID | Google Custom Search for product images |

## Flask Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Serves the single-page app (HTML embedded in `HTML_TEMPLATE`) |
| `/api/generate` | POST | Generates SEO content + fetches images via Claude + Google |
| `/api/upload` | POST | Creates WooCommerce product + uploads image to WordPress media |
| `/api/process-product` | POST | Batch process a single product from CSV (no image) |
| `/temp_images/<filename>` | GET | Serves locally cached temp images |

## Content Generation Flow (`/api/generate`)

1. Call Claude to extract product specs (brand, size, type, search term) as JSON
2. Call `fetch_square_product_images()` — searches Google Images, filters for 1:1 ratio, converts to 500×500 JPEG
3. Generate SEO description via `generate_seo_description()` → passes through `convert_to_wordpress_blocks()` to produce Gutenberg block HTML
4. Generate SEO title (50-60 chars) and meta description (≤150 chars)
5. Return all content + up to 10 image options as base64 previews

## Product Upload Flow (`/api/upload`)

1. Resolve/create WooCommerce category IDs via `/wp-json/wc/v3/products/categories`
2. POST product to WooCommerce with Yoast SEO meta fields (`_yoast_wpseo_title`, `_yoast_wpseo_metadesc`, `_yoast_wpseo_focuskw`)
3. Download selected image from original retailer URL
4. Upload to WordPress Media Library via `/wp-json/wp/v2/media` using WordPress Application Password
5. PATCH product to attach the uploaded media ID

**Note:** WordPress Application Password credentials (`WP_USERNAME`, `WP_APP_PASSWORD`) are currently hardcoded at [uploader.py:1689-1690](uploader.py#L1689). These should be moved to the config/UI.

## Image Search Logic

- **International products**: searches `BIKE_RETAIL_SITES` (Shimano, SRAM, Continental, etc. + EU retailers)
- **Israeli products**: searches `ISRAELI_BIKE_SITES` (bikemarket.co.il, 2ride.co.il, etc.) with Hebrew search terms
- Square tolerance: ±5% aspect ratio (`is_square_image()` in [image_search_square_only.py:67](image_search_square_only.py#L67))
- All images are normalized to 500×500 JPEG with white background

## Content Format (Gutenberg Blocks)

`convert_to_wordpress_blocks()` at [uploader.py:1846](uploader.py#L1846) converts Claude's plain-text output to WordPress block HTML using these rules:
- Lines with 🚴🎯⭐💎🏆✨ → `<!-- wp:heading {"level":2} -->`
- Lines ending with `?` → H3
- Short lines (<60 chars) before long lines → H3
- Lines starting with `✔` → `<!-- wp:list -->`
- Lines with `🛒` → bold paragraph (CTA)
- Lines with `|` → italic paragraph (footer)
- Everything else → regular paragraph

## CSV Batch Upload

The CSV tab accepts files with columns: `שם המוצר, מחיר, קטגוריה, ביטויי מפתח` (pipe-separated keywords). Processing is done client-side by calling `/api/process-product` per row. CSV batch does NOT include image upload.

## Dependencies

```
Flask==3.0.0
Flask-CORS==4.0.0
requests==2.31.0
Pillow  # for image processing (in image_search_square_only.py)
```

## Language Notes

- UI is in Hebrew (RTL, `lang="he" dir="rtl"`)
- Claude prompts are in Hebrew, generating Hebrew content
- Brand names kept in English within Hebrew content
- Israeli product flag toggles between Hebrew and English image search terms
