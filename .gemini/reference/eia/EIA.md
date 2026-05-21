# EIA Data Source Reference

This document centralizes knowledge and workflows related to the U.S. Energy Information Administration (EIA) API v2 integration.

## Core Workflows

### 1. Discovery
- Use `get_metadata(route)` to explore sub-routes and facets.
- Use `get_series_details(series_id)` for specific series metadata.

### 2. Data Retrieval
- Fetch data using `src/api/eia_client.py`.
- **STEO Data**: Use `get_data_steo()` for Short-Term Energy Outlook data.
- **Generic Fetch**: Use `get_data()` for other v2 routes, providing route, facets, and frequency.

## Implementation Details

- **Client**: `src/api/eia_client.py` contains the `EIAClient` class.
- **Authentication**: Uses the `EIA_API_KEY` defined in the `.env` file.
- **API Version**: Uses **API v2**.

## Security
- Store the key in `.env`: `EIA_API_KEY=your_key_here`.
- Never commit the key to version control.
