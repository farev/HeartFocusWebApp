import os
import logging
import flask
from flask import render_template
import asyncio
import websockets
import json
from flask_socketio import SocketIO, emit
import ssl
import requests

# Enhanced logging setup
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Flask and SocketIO initialization
app = flask.Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Terra streaming constants
TERRA_STREAM_URL = "wss://ws.tryterra.co/connect"
TERRA_API_KEY = "gFbEGLBB-289H3TqDSwlMN1MsZlwIBbf"
TERRA_DEV_ID = "4actk-heartfocus-testing-zC3CEBBRcu"

def get_token():
    url = 'https://ws.tryterra.co/auth/developer'
    headers = {
        'accept': 'application/json',
        'dev-id': TERRA_DEV_ID,
        'x-api-key': TERRA_API_KEY,
    }
    
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        token = response.json().get("token")
        return token
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching token: {e}")
        return None

# Background task to stream heart rate data from Terra and send it to the frontend
async def stream_terra():
    logging.info("stream_terra function started")
    while True:
        try:
            logging.info(f"Attempting to connect to Terra API at {TERRA_STREAM_URL}")
            
            ssl_context = ssl._create_unverified_context()
            
            async with websockets.connect(TERRA_STREAM_URL, ssl=ssl_context) as websocket:
                logging.info("Connected to Terra API successfully")
                
                token = get_token()
                if not token:
                    raise Exception("Failed to get authentication token")

                auth_message = json.dumps({
                    "op": 3,
                    "d": {
                        "token": token,
                        "type": 1
                    }
                })

                logging.info("Sending authentication message")
                await websocket.send(auth_message)
                logging.info("Sent authentication message to Terra API")
                
                async def send_heartbeat():
                    while True:
                        await websocket.send(json.dumps({"op": 1}))
                        await asyncio.sleep(interval / 1000)

                # Continuously listen for incoming data
                while True:
                    data = await websocket.recv()
                    logging.info(f"Received data from Terra API: {data}")
                    message = json.loads(data)

                    if message.get('op') == 2:  # Hello message
                        interval = message['d']['heartbeat_interval']
                        asyncio.create_task(send_heartbeat())
                    elif message.get('op') == 1:  # Heartbeat ACK
                        logging.info("Received heartbeat acknowledgment")
                    elif message.get('op') == 0:  # Actual data
                        heart_rate_data = message.get('d', {})
                        logging.info(f"Parsed heart rate data: {heart_rate_data}")
                        socketio.emit('heart_rate_update', heart_rate_data)
                    else:
                        logging.warning(f"Unknown message type: {message}")

        except websockets.exceptions.ConnectionClosed as e:
            logging.error(f"WebSocket connection closed: {str(e)}")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON data: {str(e)}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
        
        logging.info("Attempting to reconnect in 5 seconds...")
        await asyncio.sleep(5)  # Wait for 5 seconds before attempting to reconnect

# Handle client connections
@socketio.on('connect')
def handle_connect():
    logging.info("Client connected")
    socketio.start_background_task(stream_terra)
    logging.info("Started stream_terra background task")

@socketio.on('disconnect')
def handle_disconnect():
    logging.info("Client disconnected")

@app.route('/')
def index():
    return render_template('index.html')

# Run the Flask app with SocketIO support
if __name__ == "__main__":
    logging.info("Starting Flask-SocketIO server...")
    socketio.run(app, host="0.0.0.0", port=8080, debug=True, allow_unsafe_werkzeug=True)