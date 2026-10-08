# MPFM Pension Fund Price Scraper

This is an automated scraper for historical fund prices built with playwright. By using [Macau Pension Fund Management (MPFM)](https://www.mpfm.com.mo) as the target. Includes data validation and a consolidation pipeline that merges per-day CSVs into a single analysis-ready table.

> **Disclaimer**
> - This project is for **educational purpose only** and **personal use**. It is not affiliated with, endorsed, or sponsored by MPFM.
> - The scraped data belongs to its respective owner. Do not redistribute the data commercially.
> - You are responsible for complying with the source website's terms of use.
> - **Never commit your credentials or scraped data** — this repo intentionally excludes `.env` and all CSV files via `.gitignore`.
## Project Structure

├── tests/getMpfmPrice.spec.js   # Playwright scraper
├── checkDataFiles.py            # for check number of row + missing dates
├── create_fund_dataframe.py     # compile daily CSV into a full data table
├── playwright.config.js
└── .env                         # for setting user and password

## Setup

### 1. Install dependencies
### 2. Configure credentials via environment variables
   a. Install dotenv
   b. Create a .env file in the project root
      MPFM_USER=your_login_id
      MPFM_PASS=your_password
   c. Load and use them in the test script
      require('dotenv').config();
      const USER = process.env.MPFM_USER;
      const PASS = process.env.MPFM_PASS;
   d. Alternative: pass them inline (macOS/Linux/Windows PowerShell)
   e. Verify .env is gitignored
      git status / git check-ignore .env
### 3. Verify data folders are excluded

## Usage

### 1. Scrape
    npx playwright test getMpfmPrice --workers=1
    # e.g. to scrapy data in year 2024
    START_DATE=2024-01-01 END_DATE=2024-12-31 npx playwright test getMpfmPrice

### 2. Validate
    python checkDataFiles.py

### 3. Build table
    python create_fund_dataframe.py

## Technical Notes
- **Login flow**: the site's login opens a `window.open` popup — handled via Playwright's `waitForEvent('popup')`.
- **Sync waits**: after each query, the script polls until the as-of date (截至, "as of") in the `#unitPrice` panel changes, instead of relying on fixed `waitForTimeout` delays. This avoids race conditions where stale table data is read mid-render.
- **Multiple tables, same id**: the page contains several `table#balance_table` elements (holdings, contributions, prices). The price table is isolated by filtering out the ones containing 累計供款 ("cumulative contributions") and 成份基金 ("constituent funds").
- **Encoding**: all CSVs are written as UTF-8 **with BOM** so Excel renders Chinese fund names correctly.
- **Timeouts**: `test.setTimeout(0)` is set in the spec, as full-range scrapes run for a long time. Run year-by-year to keep runs resumable.
- **Resume logic**: existing files with ≥8 rows are skipped, so re-running after a crash only fetches missing dates.