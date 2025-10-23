"""SVG generator utilities for sparklines and badges"""
import config

def generate_sparkline(data_points, width=None, height=None, color=None):
    """
    Generate an SVG sparkline from a list of data points

    Args:
        data_points: List of numeric values
        width: SVG width (default from config)
        height: SVG height (default from config)
        color: Line color (default from config)

    Returns:
        SVG string
    """
    if not data_points:
        return generate_empty_sparkline(width, height)

    width = width or config.SPARKLINE_WIDTH
    height = height or config.SPARKLINE_HEIGHT
    color = color or config.SPARKLINE_COLOR

    # Normalize data to fit in the sparkline
    min_val = min(data_points)
    max_val = max(data_points)

    # Avoid division by zero
    if max_val == min_val:
        # All values are the same, draw a horizontal line in the middle
        y = height / 2
        points = [(i * width / (len(data_points) - 1 if len(data_points) > 1 else 1), y)
                  for i in range(len(data_points))]
    else:
        # Scale points to fit within the height
        padding = height * 0.1  # 10% padding
        usable_height = height - 2 * padding

        points = []
        for i, value in enumerate(data_points):
            x = i * width / (len(data_points) - 1) if len(data_points) > 1 else width / 2
            # Invert y because SVG coordinates start at top
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
