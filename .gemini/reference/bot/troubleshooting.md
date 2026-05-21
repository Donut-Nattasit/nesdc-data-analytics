# BOT Troubleshooting

This document records known errors, pitfalls, and solutions for the Bank of Thailand (BOT) API integration.

## Known Errors

### 1. 10-Year Data Limit
- **Problem**: The BOT API typically limits data retrieval to a 10-year window per request.
- **Solution**: The `BOTClient.get_data()` method implements a chunking strategy (fetching in 5-year intervals) to bypass this limit and retrieve full history.

### 2. Authorization Errors
- **Cause**: Missing or invalid `BOT_API_TOKEN` in the `.env` file or headers.
- **Solution**: Ensure the token is valid and the header key is exactly `Authorization` (or `App-Key` depending on the specific API version, though our client uses `Authorization`).

## Limitations
- **Throttling**: Be mindful of rate limits if fetching a large number of series sequentially.
- **Date Format**: Start period must be in `YYYY-MM-DD` format.
