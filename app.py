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
        'dev-id': TERRA_DEV_ID,  # Replace with your dev ID
        'x-api-key': TERRA_API_KEY,  # Replace with your API key
    }
    
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        token = response.json().get("token")
        return token
    except requests.exceptions.RequestException as e:
        print(f"Error fetching token: {e}")
        return None



# Background task to stream heart rate data from Terra and send it to the frontend
async def stream_terra():
    logging.info("stream_terra function started")
    while True:
        try:
            logging.info(f"Attempting to connect to Terra API at {TERRA_STREAM_URL}")
            
            # Bypass SSL verification
            ssl_context = ssl._create_unverified_context()
            
            async with websockets.connect(TERRA_STREAM_URL, ssl=ssl_context) as websocket:
                logging.info("Connected to Terra API successfully")
                
                # Authenticate with the Terra streaming API
                token = get_token()  # Get the token from the authentication endpoint
                auth_message = json.dumps({
                    "op": 3,
                    "d": {
                        "token": token,
                        "type": 1  # 1 for developer
                    }
                })

                logging.info(f"Sending authentication message: {auth_message}")
                await websocket.send(auth_message)
                logging.info("Sent authentication message to Terra API")
                
                # Wait for authentication response
                #auth_response = await websocket.recv()
                #logging.info(f"Received authentication response: {auth_response}")

                '''if 'op' in heart_rate_data:
                    if heart_rate_data['op'] == 2:
                        interval = heart_rate_data['d']['heartbeat_interval']
                        await websocket.send(json.dumps({"op": 0}))
                        asyncio.get_event_loop().call_later(interval / 1000, asyncio.create_task, websocket.send(json.dumps({"op": 0})))
                    elif heart_rate_data['op'] == 1:
                        # Handle heartbeat acknowledgment if necessary
                        pass'''
                
                async def send_heartbeat():
                    while True:
                        await websocket.send(json.dumps({"op": 1}))
                        await asyncio.sleep(interval / 1000)
                
                # Continuously listen for incoming data
                '''while True:
                    data = await websocket.recv()
                    logging.info(f"Received data from Terra API: {data}")
                    heart_rate_data = json.loads(data)
                    logging.info(f"Parsed heart rate data: {heart_rate_data}")
                    # Send live data to all connected clients
                    socketio.emit('heart_rate_update', heart_rate_data)'''
                
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
    # Start Terra streaming in the background once a client connects
    asyncio.run(stream_terra())  # Use asyncio.run to properly handle the coroutine
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