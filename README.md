# NetBeans Plugin Download Counter

Track and display download counts for NetBeans plugins with embeddable badges and sparklines.

Simply use your plugin ID (visible in the URL like `plugins.netbeans.apache.org/catalogue/?id=118`) to generate download count badges and historical trend sparklines.

## Features

- **Badge Generation**: Display download counts using shields.io endpoint badges
- **Sparkline Charts**: Show download history trends as SVG sparklines
- **Simple Integration**: Just use your plugin ID - no configuration needed

## Usage Examples

### In Your GitHub README

```markdown
# My NetBeans Plugin

![Downloads](https://img.shields.io/endpoint?url=https://openbeans.org/plugin-counter/api/118)
![Download Trend](https://openbeans.org/plugin-counter/sparkline/118?days=30)

Description of your plugin...
```

### Show Different Time Ranges

```markdown
![Last 90 Days](https://openbeans.org/plugin-counter/sparkline/118?days=90)
![Last Year](https://openbeans.org/plugin-counter/sparkline/118?days=365)
```

## API Reference

**Base URL**: `https://openbeans.org/plugin-counter`

### Get Download Badge

**Endpoint**: `GET /api/<plugin_id>`

Returns JSON in shields.io endpoint format for displaying download counts.

**Example**:
```markdown
![Downloads](https://img.shields.io/endpoint?url=https://openbeans.org/plugin-counter/api/118)
```

### Get Sparkline

**Endpoint**: `GET /sparkline/<plugin_id>`

Returns an SVG sparkline showing download trends over time.

**Parameters**:
- `days` (optional): Number of days of history to display (default: 30, max: 365)

**Examples**:
```markdown
![Download History](https://openbeans.org/plugin-counter/sparkline/118)
![Last 90 Days](https://openbeans.org/plugin-counter/sparkline/118?days=90)
```

### Update Download Count

**Endpoint**: `POST /update/<plugin_id>`

Fetches and stores the latest download count from the NetBeans plugin portal. Updates are throttled to once per 24 hours per plugin.

**Request Body**: None required (empty JSON object `{}` is acceptable)

**Example**:
```bash
curl -X POST https://openbeans.org/plugin-counter/update/118 \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response** (Success):
```json
{
  "success": true,
  "plugin_id": "118",
  "count": 121,
  "timestamp": "2025-10-23T06:03:27.625305"
}
```

**Response** (Throttled):
```json
{
  "error": "Too many requests",
  "message": "Plugin was last updated at 2025-10-23T06:03:27.625305. Updates are throttled to once per 24 hours.",
  "last_fetched": "2025-10-23T06:03:27.625305"
}
```
