# server.py
import asyncio
import websockets

async def echo(websocket, path):
    async for message in websocket:
        await websocket.send(f'You said: {message}')

start_server = websockets.serve(echo, 'localhost', 8081)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
