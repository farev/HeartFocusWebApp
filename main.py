import asyncio
import websockets
import json

TERRA_STREAM_URL = "wss://ws.tryterra.co/stream"  # Replace with actual streaming endpoint

async def stream_terra():
    async with websockets.connect(TERRA_STREAM_URL) as websocket:
        auth_message = json.dumps({
            "type": "subscribe",
            "api_key": "gFbEGLBB-289H3TqDSwlMN1MsZlwIBbf",
            "dev_id": "4actk-heartfocus-testing-zC3CEBBRcu",
        })
        await websocket.send(auth_message)

        while True:
            data = await websocket.recv()
            print("Received data:", data)
            # Process and forward data to the web app

asyncio.get_event_loop().run_until_complete(stream_terra())
