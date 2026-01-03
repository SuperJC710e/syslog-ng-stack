#!/usr/bin/env python3
"""
Syslog Viewer - Web interface for viewing syslog messages
Reads syslog messages from shared volume and displays them via a web interface
"""

from datetime import datetime
from collections import deque
from flask import Flask, render_template, jsonify, request
import argparse
import json
from pathlib import Path
import logging
import time

# Log file path
LOG_DIR = Path('/app/logs')
LOG_FILE = LOG_DIR / 'syslog.jsonl'

# Store logs in memory (keep last 10000 entries)
log_buffer = deque(maxlen=10000)
last_file_position = 0

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_logs_from_file():
    """Load logs from file, starting from last read position"""
    global last_file_position

    if not LOG_FILE.exists():
        return 0

    try:
        new_entries = 0
        with open(LOG_FILE, 'r') as f:
            # Seek to last position
            f.seek(last_file_position)

            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    log_buffer.append(log_entry)
                    new_entries += 1
                except json.JSONDecodeError:
                    continue

            # Update position
            last_file_position = f.tell()

        return new_entries

    except Exception as e:
        logger.error(f"Error loading logs from file: {e}")
        return 0


def initial_load():
    """Load all existing logs on startup"""
    global last_file_position

    if not LOG_FILE.exists():
        logger.warning(f"Log file does not exist yet: {LOG_FILE}")
        return

    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    log_buffer.append(log_entry)
                except json.JSONDecodeError:
                    continue
            last_file_position = f.tell()

        logger.info(f"Loaded {len(log_buffer)} existing log entries")

    except Exception as e:
        logger.error(f"Error during initial load: {e}")


# Flask web interface
app = Flask(__name__)

# Disable Flask's default request logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')


@app.route('/api/logs')
def get_logs():
    """
    Get logs with optional filtering
    Query params:
    - limit: max number of logs to return (default: 1000)
    - severity: filter by severity level
    - source: filter by source IP
    - search: search in message text
    """
    # Load any new logs
    load_logs_from_file()

    logs = list(log_buffer)

    # Apply filters
    severity_filter = request.args.get('severity')
    source_filter = request.args.get('source')
    search_filter = request.args.get('search')

    if severity_filter:
        logs = [log for log in logs if log.get('severity') == severity_filter]

    if source_filter:
        logs = [log for log in logs if log.get('source') == source_filter]

    if search_filter:
        search_lower = search_filter.lower()
        logs = [log for log in logs if search_lower in log.get('message', '').lower()]

    # Apply limit
    limit = int(request.args.get('limit', 1000))
    logs = logs[-limit:]

    return jsonify(logs)


@app.route('/api/stats')
def get_stats():
    """Get statistics about collected logs"""
    load_logs_from_file()

    logs = list(log_buffer)

    if not logs:
        return jsonify({
            'total': 0,
            'sources': [],
            'severities': {},
            'facilities': {},
            'protocols': {}
        })

    sources = list(set(log.get('source') for log in logs if log.get('source')))

    severity_counts = {}
    facility_counts = {}
    protocol_counts = {}

    for log in logs:
        severity = log.get('severity', 'unknown')
        facility = log.get('facility', 'unknown')
        protocol = log.get('protocol', 'unknown')

        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        facility_counts[facility] = facility_counts.get(facility, 0) + 1
        protocol_counts[protocol] = protocol_counts.get(protocol, 0) + 1

    return jsonify({
        'total': len(logs),
        'sources': sorted(sources),
        'severities': severity_counts,
        'facilities': facility_counts,
        'protocols': protocol_counts
    })


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Syslog Viewer - Web Interface')
    parser.add_argument('--port', type=int, default=8080,
                        help='Web interface port (default: 8080)')
    parser.add_argument('--host', default='0.0.0.0',
                        help='Host to bind to (default: 0.0.0.0)')
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Syslog Viewer Starting")
    logger.info("=" * 60)
    logger.info(f"Log file: {LOG_FILE}")

    # Wait for log directory to be available
    retry_count = 0
    while not LOG_DIR.exists() and retry_count < 10:
        logger.warning(f"Waiting for log directory... ({retry_count + 1}/10)")
        time.sleep(2)
        retry_count += 1

    if not LOG_DIR.exists():
        logger.error(f"Log directory not found: {LOG_DIR}")
        logger.warning("Proceeding anyway - will watch for log file creation")

    # Load existing logs
    initial_load()

    # Start web interface with Waitress (production-ready WSGI server)
    logger.info(f"✓ Web interface available at http://{args.host}:{args.port}")
    logger.info("Using Waitress production WSGI server")

    from waitress import serve
    serve(app, host=args.host, port=args.port, threads=4)
