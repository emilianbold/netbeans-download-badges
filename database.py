"""Database module for download counter service"""
import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager
import config

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_database():
    """Initialize database schema"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Create plugins table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plugins (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL
            )
        ''')

        # Create downloads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                count INTEGER NOT NULL,
                FOREIGN KEY (plugin_id) REFERENCES plugins (id)
            )
        ''')

        # Create indexes for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_downloads_plugin_id
            ON downloads(plugin_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_downloads_timestamp
            ON downloads(timestamp)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_downloads_plugin_timestamp
            ON downloads(plugin_id, timestamp)
        ''')

def add_plugin_if_not_exists(plugin_id):
    """Add a plugin if it doesn't exist"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR IGNORE INTO plugins (id, created_at) VALUES (?, ?)',
            (plugin_id, datetime.now().isoformat())
        )

def add_download_record(plugin_id, count, timestamp=None):
    """Add a download count record for a plugin"""
    if timestamp is None:
        timestamp = datetime.now().isoformat()

    with get_db() as conn:
        cursor = conn.cursor()

        # Ensure plugin exists
        cursor.execute(
            'INSERT OR IGNORE INTO plugins (id, created_at) VALUES (?, ?)',
            (plugin_id, datetime.now().isoformat())
        )

        # Insert download record
        cursor.execute(
            'INSERT INTO downloads (plugin_id, timestamp, count) VALUES (?, ?, ?)',
            (plugin_id, timestamp, count)
        )

def get_latest_download_count(plugin_id):
    """Get the latest download count for a plugin"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT count FROM downloads WHERE plugin_id = ? ORDER BY timestamp DESC LIMIT 1',
            (plugin_id,)
        )
        result = cursor.fetchone()
        return result['count'] if result else None

def get_last_fetched(plugin_id):
    """Get the last fetched timestamp for a plugin by querying the downloads table"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT timestamp FROM downloads WHERE plugin_id = ? ORDER BY timestamp DESC LIMIT 1',
            (plugin_id,)
        )
        result = cursor.fetchone()
        return result['timestamp'] if result else None

def can_update(plugin_id):
    """Check if a plugin can be updated based on throttle settings"""
    last_fetched = get_last_fetched(plugin_id)

    if last_fetched is None:
        return True

    last_fetched_dt = datetime.fromisoformat(last_fetched)
    throttle_delta = timedelta(hours=config.THROTTLE_HOURS)

    return datetime.now() - last_fetched_dt >= throttle_delta

def is_stale(plugin_id, hours=24):
    """Check if plugin data is stale (older than specified hours)"""
    last_fetched = get_last_fetched(plugin_id)

    if last_fetched is None:
        return True

    last_fetched_dt = datetime.fromisoformat(last_fetched)
    stale_threshold = timedelta(hours=hours)

    return datetime.now() - last_fetched_dt >= stale_threshold

def get_download_history(plugin_id, days=30):
    """Get download history for a plugin for the last N days"""
    with get_db() as conn:
        cursor = conn.cursor()
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute(
            '''SELECT timestamp, count FROM downloads
               WHERE plugin_id = ? AND timestamp >= ?
               ORDER BY timestamp ASC''',
            (plugin_id, cutoff)
        )

        return [{'timestamp': row['timestamp'], 'count': row['count']}
                for row in cursor.fetchall()]

def get_plugin_info(plugin_id):
    """Get plugin information"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM plugins WHERE id = ?',
            (plugin_id,)
        )
        result = cursor.fetchone()
        return dict(result) if result else None
