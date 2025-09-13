# Chart API Contract

The `POST /v1/data/charts` endpoint returns analytical chart data for the
requested chart type. Requests must include a JSON body matching the
`ChartRequest` schema:

```json
{
  "chart": "enps" | "nine_box",
  "params": {}
}
```

The response adheres to the `ChartResponse` schema:

| Field | Type | Description |
|-------|------|-------------|
| `chart` | string | Identifier of the chart returned. |
| `title` | string | Human readable title for the chart. |
| `series` | list of `ChartSeries` | Data series for the chart. |
| `legend` | list of string | Labels for the chart legend. |
| `bins` | object or null | Optional summary values (e.g. totals). |
| `insights_placeholder` | bool | Indicates whether insights are available. |

`ChartSeries` objects contain a `name` and a list of `points`.  Each
`SeriesPoint` includes `x` and `y` values and optional `meta` data:

```json
{
  "name": "count",
  "points": [
    { "x": "2025-04", "y": 18, "meta": null }
  ]
}
```

This contract is considered canonical for chart responses and is used by
the eNPS and 9-box chart implementations.
