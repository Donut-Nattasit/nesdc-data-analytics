# CEIC Troubleshooting

This document records known errors, pitfalls, and solutions for the CEIC API integration.

## Known Errors

### 1. `NON_CONTINUOUS_SERIES`
- **Cause**: Occurs when requesting `with_historical_extension=True` for a series that does not support it (e.g., discontinued series or specific restricted datasets).
- **Solution**: Catch the exception and fall back to `with_historical_extension=False`.

### 2. Status 400 (Bad Request) on Batch Fetching
- **Cause**: Using `with_historical_extension=True` while passing a list of multiple series IDs. The API only supports this parameter for single-series requests.
- **Solution**: Iterate through the series IDs and fetch them one by one.

### 3. Metadata Not Subscriptable
- **Cause**: Attempting to access metadata like a dictionary (e.g., `item.metadata['name']`). CEIC SDK returns objects.
- **Solution**: Use dot notation (`item.metadata.name`) or `getattr(item.metadata, 'name', 'N/A')`.

## Limitations
- **Search Limit**: Maximum of 100 results per search request.
- **Data Volume**: Use `count=10000` to ensure long historical series are fully retrieved.
