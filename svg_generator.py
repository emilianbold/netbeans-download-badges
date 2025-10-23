"""SVG generator utilities for sparklines and badges"""
import config
from datetime import datetime

def generate_sparkline(history, width=None, height=None, color=None):
    """
    Generate an SVG sparkline from download history

    Works with daily data. If data is missing for certain days, holds the last
    known value and renders it with a dotted line.

    Args:
        history: List of dicts with 'timestamp' and 'count' keys (sorted by timestamp ASC)
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

    # Filter for one value per day (keep last entry per day)
    # Input is already sorted, so we maintain that order
    # Download counts are monotonic, so last entry = highest count
    daily_data = []  # List of (date, value) tuples
    prev_date = None

    for record in history:
        dt = datetime.fromisoformat(record['timestamp'])
        date = dt.date()

        if date == prev_date:
            # Same day - replace with latest value
            daily_data[-1] = (date, record['count'])
        else:
            # New day
            daily_data.append((date, record['count']))
            prev_date = date

    if not daily_data:
        return generate_empty_sparkline(width, height)

    # Get value range for normalization
    values = [v for _, v in daily_data]
    min_val = min(values)
    max_val = max(values)

    # Calculate date range
    min_date = daily_data[0][0]
    max_date = daily_data[-1][0]
    date_range_days = (max_date - min_date).days

    # Helper functions for coordinate conversion
    def date_to_x(date):
        if date_range_days == 0:
            return width / 2
        days_from_start = (date - min_date).days
        return (days_from_start / date_range_days) * width

    def value_to_y(value):
        if max_val == min_val:
            return height / 2
        padding = height * 0.1
        usable_height = height - 2 * padding
        normalized = (value - min_val) / (max_val - min_val)
        return height - padding - (normalized * usable_height)

    # Build segments: solid for real data, dotted for held values
    solid_segments = []
    dotted_segments = []
    all_points = []  # For filled area

    current_solid_segment = []

    for i, (date, value) in enumerate(daily_data):
        x = date_to_x(date)
        y = value_to_y(value)
        point = (x, y)

        if i == 0:
            # First point
            current_solid_segment.append(point)
            all_points.append(point)
        else:
            prev_date, prev_value = daily_data[i - 1]
            gap_days = (date - prev_date).days

            if gap_days > 1:
                # Gap detected - hold previous value
                prev_x = date_to_x(prev_date)
                prev_y = value_to_y(prev_value)

                # End current solid segment
                if current_solid_segment:
                    solid_segments.append(current_solid_segment)
                    current_solid_segment = []

                # Create dotted segment holding previous value
                step_point = (x, prev_y)
                dotted_segments.append([(prev_x, prev_y), step_point])
                all_points.append(step_point)

                # Start new solid segment at current point
                current_solid_segment.append(point)
                all_points.append(point)
            else:
                # Consecutive days - continue solid segment
                current_solid_segment.append(point)
                all_points.append(point)

    # Add final solid segment if it exists
    if current_solid_segment:
        solid_segments.append(current_solid_segment)

    # Build SVG polylines
    polylines = []

    # Solid segments (real data)
    for segment in solid_segments:
        points_str = ' '.join(f'{x:.2f},{y:.2f}' for x, y in segment)
        polylines.append(
            f'<polyline points="{points_str}" fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />'
        )

    # Dotted segments (held values)
    for segment in dotted_segments:
        points_str = ' '.join(f'{x:.2f},{y:.2f}' for x, y in segment)
        polylines.append(
            f'<polyline points="{points_str}" fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-dasharray="4,4" stroke-linecap="round" stroke-linejoin="round" />'
        )

    # Create filled area under the line
    area_points = [(0, height)] + all_points + [(width, height)]
    area_path = ' '.join(f'{x:.2f},{y:.2f}' for x, y in area_points)

    # Join polylines with newlines
    polylines_str = '\n    '.join(polylines)

    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:{color};stop-opacity:0.3" />
            <stop offset="100%" style="stop-color:{color};stop-opacity:0.05" />
        </linearGradient>
    </defs>
    <polygon points="{area_path}" fill="url(#gradient)" />
    {polylines_str}
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
