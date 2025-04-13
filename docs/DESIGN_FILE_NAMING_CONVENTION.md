# Design File Naming Convention

To ensure consistency, scalability, and automation, all design files must follow this naming convention:

```
[Theme]-[Concept]-[Variant]-[Version]-[Date].ext
```

**Fields:**
- **Theme:** Main design theme (e.g., CatMeme, ArtParody, Artistic)
- **Concept:** Specific design concept (e.g., BusinessCat, StarryNightCats)
- **Variant:** Intended background or text style. Allowed values:
  - `Dark` (for dark shirts/backgrounds)
  - `White` (for white shirts/backgrounds)
  - `LightText` (for designs with light text)
  - `DarkText` (for designs with dark text)
- **Version:** Version number (e.g., v1, v2, v3)
- **Date:** Creation date in YYYYMMDD format (e.g., 20250412)
- **ext:** File extension (png, jpg, jpeg)

**Examples:**
- `CatMeme-BusinessCat-Dark-v2-20250322.png`
- `MonetBlackCat-Classic-White-v1-20250412.jpg`
- `ArtParody-StarryNightCats-LightText-v3-20250410.jpeg`

## Usage

- All files in the "Ready For Publish" folder must follow this convention.
- The included script `validate_design_filenames.py` will scan your folder and flag any files that do not conform.
- The parser will extract all fields for use in automation and Airtable sync.

## Why This Matters

- **Automation:** Enables scripts to extract metadata and automate publishing, tracking, and analytics.
- **Clarity:** Makes it easy to identify design attributes at a glance.
- **Scalability:** Supports large libraries and future workflow enhancements.

## Extending the Convention

If you need to encode more metadata (e.g., product type, artist initials), add new fields before the version or date, and update the parser/validator accordingly.

---

_Last updated: 2025-04-12_
