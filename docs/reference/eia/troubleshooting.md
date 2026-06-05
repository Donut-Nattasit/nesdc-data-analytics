# EIA Troubleshooting

This document records known errors, pitfalls, and solutions for the U.S. EIA API v2 integration.

## Known Errors

### 1. API v1 vs v2 Incompatibility
- **Problem**: Many older tutorials use v1 routes (e.g., `/series/`). v1 is deprecated and requires a different key/structure.
- **Solution**: Use only v2 routes (e.g., `/v2/steo/data/`). Our `EIAClient` is strictly v2.

### 2. Missing Data for Specific Facets
- **Problem**: Some series IDs might not be available for all frequencies or routes.
- **Solution**: Use `get_metadata(route)` to verify which facets (filters) and frequencies are supported for a specific data path.

### 3. "No data found" for STEO
- **Cause**: Series IDs in STEO are case-sensitive or require specific frequency parameters.
- **Solution**: Double-check the ID (e.g., `DCOILWTX`) and ensure the frequency (monthly, quarterly) matches the dataset.

## Limitations
- **API Key**: Ensure `EIA_API_KEY` is set.
- **Sorting**: Large requests may require explicit sorting by `period` to ensure chronological order in the resulting DataFrame.
