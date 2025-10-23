"""Flask application for download counter service"""
from flask import Flask, jsonify, request, Response
from datetime import datetime
import logging
import database
import scraper
import svg_generator
import config

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database on startup
database.init_database()

@app.route('/')
def index():
    """Home page with API documentation"""
    return '''
    <html>
    <head><title>Download Counter Service</title></head>
    <body>
        <h1>Download Counter Service</h1>
        <h2>Available Endpoints:</h2>
        <ul>
            <li><strong>GET /api/&lt;plugin_id&gt;</strong> - Get download count as JSON (for shields.io endpoint badge)</li>
            <li><strong>GET /sparkline/&lt;plugin_id&gt;</strong> - Get sparkline SVG image (optional: ?days=30)</li>
            <li><strong>POST /update/&lt;plugin_id&gt;</strong> - Update download count (throttled to once per 24h)</li>
        </ul>
        <h2>Usage Examples:</h2>
        <h3>Badge (via shields.io):</h3>
        <pre>![Downloads](https://img.shields.io/endpoint?url=https://openbeans.org/plugin-counter/api/118)</pre>
        <img src="https://img.shields.io/endpoint?url=https://img.shields.io/badge/downloads-121-blue" alt="Example badge">

        <h3>Sparkline:</h3>
        <pre>![Download History](https://openbeans.org/plugin-counter/sparkline/118)</pre>
    </body>
    </html>
    '''

@app.route('/api/<plugin_id>')
def api_endpoint(plugin_id):
    """
    Return download count in shields.io endpoint badge format
    See: https://shields.io/endpoint
    """
    try:
        count = database.get_latest_download_count(plugin_id)

        if count is None:
            # No data available yet
            return jsonify({
                'schemaVersion': 1,
                'label': config.DEFAULT_BADGE_LABEL,
                'message': 'no data',
                'color': 'lightgrey'
            })

        # Format the number nicely
        formatted_count = svg_generator.format_number(count)

        return jsonify({
            'schemaVersion': 1,
            'label': config.DEFAULT_BADGE_LABEL,
            'message': formatted_count,
            'color': config.DEFAULT_BADGE_COLOR.lstrip('#')
        })

    except Exception as e:
        logger.error(f"Error in /api/{plugin_id}: {e}")
        return jsonify({
            'schemaVersion': 1,
            'label': config.DEFAULT_BADGE_LABEL,
            'message': 'error',
            'color': 'red'
        }), 500

@app.route('/sparkline/<plugin_id>')
def sparkline_endpoint(plugin_id):
    """Return sparkline SVG for download history"""
    try:
        # Get days parameter from query string
        days = request.args.get('days', config.DEFAULT_SPARKLINE_DAYS, type=int)

        # Limit days to reasonable range
        days = max(1, min(days, 365))

        # Get download history
        history = database.get_download_history(plugin_id, days)

        if not history:
            svg = svg_generator.generate_empty_sparkline()
        else:
            # Extract counts
            counts = [record['count'] for record in history]
            svg = svg_generator.generate_sparkline(counts)

        return Response(svg, mimetype='image/svg+xml')

    except Exception as e:
        logger.error(f"Error in /sparkline/{plugin_id}: {e}")
        # Return error SVG
        svg = svg_generator.generate_empty_sparkline()
        return Response(svg, mimetype='image/svg+xml'), 500

@app.route('/update/<plugin_id>', methods=['POST'])
def update_endpoint(plugin_id):
    """
    Update download count for a NetBeans plugin (throttled)
    Expects JSON body with optional 'name'
    """
    try:
        # Check if update is allowed (throttling)
        if not database.can_update(plugin_id):
            last_fetched = database.get_last_fetched(plugin_id)
            return jsonify({
                'error': 'Too many requests',
                'message': f'Plugin was last updated at {last_fetched}. Updates are throttled to once per {config.THROTTLE_HOURS} hours.',
                'last_fetched': last_fetched
            }), 429

        # Get request data
        data = request.get_json() or {}
        name = data.get('name')

        # Add/update plugin in database (always use 'netbeans' as source)
        database.add_or_update_plugin(plugin_id, 'netbeans', name)

        # Fetch download count from NetBeans plugin portal
        logger.info(f"Fetching download count for NetBeans plugin {plugin_id}")
        count = scraper.fetch_download_count('netbeans', plugin_id)

        # Store in database
        timestamp = datetime.now().isoformat()
        database.add_download_record(plugin_id, count, timestamp)

        logger.info(f"Successfully updated plugin {plugin_id}: {count} downloads")

        return jsonify({
            'success': True,
            'plugin_id': plugin_id,
            'count': count,
            'timestamp': timestamp
        })

    except scraper.ScraperError as e:
        logger.error(f"Scraper error for plugin {plugin_id}: {e}")
        return jsonify({
            'error': 'Scraper error',
            'message': str(e)
        }), 500

    except Exception as e:
        logger.error(f"Error in /update/{plugin_id}: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
