"""SVG generator utilities for sparklines and badges"""
import config
from datetime import datetime

def generate_sparkline(history, width=None, height=None, color=None):
    """
    Generate an SVG sparkline from download history

    Args:
        history: List of dicts with 'timestamp' and 'count' keys
        width: SVG width (default from config)
        height: SVG height (default from config)
        color: Line color (default from config)

    Returns:
        SVG string
    """
    if not history:
        return generate_empty_sparkline(width, height)

    width = width or config.SPARKLINE_WIDTH
    height = height or config.SPARKLINE_HEIGHT
    color = color or config.SPARKLINE_COLOR

    # Extract values and timestamps
    data_points = [record['count'] for record in history]
    timestamps = [datetime.fromisoformat(record['timestamp']) for record in history]

    # Normalize data to fit in the sparkline
    min_val = min(data_points)
    max_val = max(data_points)

    # Calculate time range for proper X-axis positioning
    min_time = timestamps[0]
    max_time = timestamps[-1]
    time_range = (max_time - min_time).total_seconds()

    # Avoid division by zero
    if max_val == min_val:
        # All values are the same, draw a horizontal line in the middle
        y = height / 2
        if time_range == 0:
            # Single data point
            points = [(width / 2, y)]
        else:
            points = []
            for i, ts in enumerate(timestamps):
                x = ((ts - min_time).total_seconds() / time_range) * width
                points.append((x, y))
    else:
        # Scale points to fit within the height
        padding = height * 0.1  # 10% padding
        usable_height = height - 2 * padding

        points = []
        for value, ts in zip(data_points, timestamps):
            # Calculate X based on actual timestamp
            if time_range == 0:
                # Single data point
                x = width / 2
            else:
                x = ((ts - min_time).total_seconds() / time_range) * width

            # Calculate Y based on value
            normalized = (value - min_val) / (max_val - min_val)
            y = height - padding - (normalized * usable_height)
            points.append((x, y))

    # Create polyline path
    polyline_points = ' '.join(f'{x:.2f},{y:.2f}' for x, y in points)

    # Create filled area under the line
    area_points = [(0, height)] + points + [(width, height)]
    area_path = ' '.join(f'{x:.2f},{y:.2f}' for x, y in area_points)

    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:{color};stop-opacity:0.3" />
            <stop offset="100%" style="stop-color:{color};stop-opacity:0.05" />
        </linearGradient>
    </defs>
    <polygon points="{area_path}" fill="url(#gradient)" />
    <polyline points="{polyline_points}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
</svg>'''

    return svg

def generate_empty_sparkline(width=None, height=None):
    """Generate an empty sparkline SVG"""
    width = width or config.SPARKLINE_WIDTH
    height = height or config.SPARKLINE_HEIGHT

    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle"
          font-family="Verdana,sans-serif" font-size="12" fill="#999">No data</text>
</svg>'''

    return svg

def format_number(num):
    """Format number with k/M suffix for large numbers"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}k"
    else:
        return str(num)
