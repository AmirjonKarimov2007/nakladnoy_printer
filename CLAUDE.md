# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Spiska Picker Pro Max** — Flask-based warehouse order picking web application for tracking and managing product collection from orders. Fetches order data from SmartUP API, provides barcode scanning (manual + camera), status tracking, and export capabilities.

## Quick Start

```bash
# Install dependencies
pip install flask requests pytz

# Run development server
python main.py
```

Access via `http://localhost:5000/?order_id=<deal_id>`

## Configuration

**Environment Variables** (currently hardcoded in `main.py`, should be moved to `.env`):
- `SMARTUP_AUTH_USERNAME`, `SMARTUP_AUTH_PASSWORD` — SmartUP API credentials
- `FILIAL_ID` — Branch identifier (default: `'5012602'`)
- `PROJECT_CODE` — Project code (default: `'trade'`)

**Security**: Credentials are currently hardcoded in `main.py:11`. Move to environment variables before production deployment.

## Architecture

```
nakladnoy_printer-web/
├── main.py              # Flask backend: SmartUP API integration, order normalization
├── templates/
│   └── order.html       # Jinja2 template: UI structure, product cards
└── static/
    ├── app.js           # Frontend logic: state management, scanning, analytics
    └── style.css        # CSS variables, glassmorphism theme, responsive
```

## Key Components

**Backend (`main.py`)**
- `get_selected_orders(deal_id)` — POST to SmartUP API, returns raw order data
- `normalize_order(order_data)` — Transforms API response into frontend format
- Routes: `/` (renders order.html), `/api/order` (JSON endpoint)
- Auth: HTTP Basic Auth (`SMARTUP_AUTH`), headers (`filial_id`, `project_code`)
- Image URLs: Generated from product_id via GitHub media CDN

**Frontend (`static/app.js`)**
- State persistence: `localStorage` with key `spiska_promax_{deal_id}`
- Status values: `pending`, `picked`, `not_found`, `partial`, `replaced`
- Modes: `normal`, `picker`, `scan`, `camera` (affects input focus, scanner behavior)
- Camera scanning: `html5-qrcode` library (loaded from CDN)
- Bulk actions: Check/Reset visible, CSV export, PDF print

**Styling (`static/style.css`)**
- CSS variables for theming (dark/light via `.light` class on body)
- Glassmorphism design: `backdrop-filter: blur(18px)`, radial gradients
- Status-specific card styles via `.status-{picked,not_found,partial,replaced}`

## Data Persistence

**localStorage Schema**:
- Key pattern: `spiska_promax_{deal_id}`
- Value: `{ barcode: { status: "pending"|"picked"|"not_found"|"partial"|"replaced", worker: string } }`
- Theme: `picker_theme` ("light" or "dark")
- Data persists per order and survives page refreshes

**Worker Management**: Worker list is hardcoded in `templates/order.html:54-60`. Modify directly to add/remove workers.

## Common Operations

```bash
# Run development server
python main.py

# Manual testing workflow:
# 1. Open http://localhost:5000/?order_id=<valid_deal_id>
# 2. Test barcode scanning with physical scanner or manual input
# 3. Verify status persistence after page refresh
# 4. Test CSV export and PDF print functionality
```

## External Dependencies

- **SmartUP API**: `https://smartup.online/b/trade/txs/tdeal/order$export` — Returns order data via POST with filial_id and deal_id
- **html5-qrcode**: CDN-loaded for camera barcode scanning (`https://unpkg.com/html5-qrcode`)
- **Product images**: `https://media.githubusercontent.com/media/AmirjonKarimov2007/rasmlar/main/{product_id}.jpg`
- **Fallback images**: `https://placehold.co/400x400/1a1a2e/a0a0b0?text=No+Image`

## Important Notes

- **Timezone**: Uses `Asia/Tashkent` timezone for date formatting (`main.py:15`)
- **API Timeout**: 30 second timeout for SmartUP API requests
- **SSL Verification**: Disabled for API calls (`verify=False`) — enable for production
- **Image Fallback**: Products without images show placeholder on error (`templates/order.html:173`)
- **No Test Framework**: Manual testing only — no automated tests configured
