# CEIC Data Source Reference

This document centralizes knowledge, workflows, and technical quirks related to the CEIC database integration.

## Core Workflows

### 1. Search & Discovery
- Search with high `limit` (e.g., 100). 
- **Prioritization**: Prioritize series from the **"World Trend Plus"** database, particularly those under the **"Global Economic Monitor"** topic.
- **GEM Naming Convention**: Standardized GEM series usually follow the pattern: `[Metric]: [Sub-metric]: [Frequency]: [Country]` (e.g., `Consumer Price Index: YoY: Monthly: Thailand`).
- Evaluate and present the top 20 results that are most related to the user's query in a table: `| ID | Name | Frequency | Unit | Country | Database |`.

### 2. Data Retrieval
- Fetch data using `src/api/ceic_client.py`.
- **Prefer `with_historical_extension=True`**: This ensures the longest possible time series.
- **Limit Handling**: Handle `count=10000` for long series.
- **Metadata Audit**: Every fetching task MUST conclude with a detailed metadata summary for verification (ID, Name, Frequency, Unit, Source, Date Range).

## Technical Quirks & Lessons Learned

- **Metadata Subscripting**: Metadata objects returned by the SDK are not subscriptable. Use `getattr(metadata, 'attribute_name')` or `metadata.attribute_name`.
- **Historical Extension Limit**: `with_historical_extension=True` only works for **one series per request**. Batch requests (list of IDs) with this parameter will fail with status 400. Iterate and fetch one by one if multiple are needed.
- **Non-Continuous Series**: Some series might throw a `NON_CONTINUOUS_SERIES` error when historical extension is requested. Fall back to `with_historical_extension=False` in these cases.
- **Search Limit**: The API search limit is capped at 100 results per request.

## Implementation Details

- **Client**: `src/api/ceic_client.py` contains the `CeicSession` wrapper.
- **Authentication**: Uses the `CEIC_API_KEY` defined in the `.env` file.
