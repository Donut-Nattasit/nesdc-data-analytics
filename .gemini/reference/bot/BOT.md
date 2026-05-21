# BOT Data Source Reference

This document centralizes knowledge and workflows related to the Bank of Thailand (BOT) API integration.

## Core Workflows

### 1. Discovery
- Use `get_category_list()` to navigate major economic categories.
- Use `get_series_list(category_code)` to find specific indicators.

### 2. Data Retrieval
- Fetch data using `src/api/bot_client.py`.
- **Automatic Chunking**: The `get_data()` method automatically handles the API's 10-year limit by fetching data in 5-year chunks.
- **Language**: Supports 'en' (default) and 'th' for series names.

## Implementation Details

- **Client**: `src/api/bot_client.py` contains the `BOTClient` class.
- **Authentication**: Uses the `BOT_API_TOKEN` defined in the `.env` file.
- **Base URL**: `https://gateway.api.bot.or.th`

## Security
- Store the token in `.env`: `BOT_API_TOKEN=your_token_here`.
- Never commit the token to version control.
