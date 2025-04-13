"""
Healthcheck server for POD Automation System.
Provides a simple HTTP endpoint for container health monitoring.
"""

import os
import sys
import threading
import logging
from flask import Flask, jsonify
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

@app.route('/healthz', methods=['GET'])
def healthcheck():
    """Health check endpoint for Docker container."""
    # Check if critical components are available
    # This is a simple check that always returns healthy
    # You can expand this to check database connections, API availability, etc.
    return jsonify({
        'status': 'healthy',
        'service': 'pod-automation',
        'timestamp': str(Path('/app/data').exists())
    }), 200

def start_healthcheck_server():
    """Start the healthcheck server in a separate thread."""
    port = int(os.environ.get('HEALTHCHECK_PORT', 8501))
    
    def run_server():
        logger.info(f"Starting healthcheck server on port {port}")
        app.run(host='0.0.0.0', port=port)
    
    # Start server in a separate thread
    thread = threading.Thread(target=run_server)
    thread.daemon = True
    thread.start()
    logger.info("Healthcheck server started in background thread")
    return thread

if __name__ == "__main__":
    # If run directly, start the server in the main thread
    port = int(os.environ.get('HEALTHCHECK_PORT', 8501))
    logger.info(f"Starting healthcheck server on port {port}")
    app.run(host='0.0.0.0', port=port)
