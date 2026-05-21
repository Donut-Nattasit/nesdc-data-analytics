# PortWatch API Reference

The IMF PortWatch platform provides real-time monitoring of maritime trade and port activity.

## Key Concepts

- **OGC API - Records**: The search API follows this standard, using GeoJSON for spatial data.
- **Collections**: Data is organized into collections. Common ones include:
    - `port-activity`: Daily calls, vessel counts, and capacity.
    - `trade-disruption`: Estimates of trade volume impacts.
- **Items**: Individual records within a collection.
- **Aggregations**: Summarized data (e.g., total calls by country).

## Usage via PortWatchClient

```python
from src.api.portwatch_client import PortWatchClient

client = PortWatchClient()

# List collections
collections = client.get_collections()
for c in collections:
    print(f"ID: {c['id']}, Title: {c['title']}")

# Fetch items (last 30 days)
# Note: datetime format is 'start/end'
df = client.get_items('port-activity', datetime='2024-04-15/2024-05-15', limit=100)
print(df.head())
```

## Common Filters

When using `get_items`, you can pass filters as a dictionary:

- `port_code`: UN/LOCODE of the port.
- `country_code`: ISO 2-letter country code.
- `vessel_type`: Filtering by ship category.

## Troubleshooting

- **Rate Limiting**: The API is public but may throttle high-frequency requests.
- **GeoJSON Extraction**: The client automatically extracts `properties` from the GeoJSON response into a Pandas DataFrame.
- **Pagination**: Use `get_all_items` for large datasets (defaults to 1000 records max).
