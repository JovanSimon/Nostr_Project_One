import asyncio
import json
from queue import Queue
import websockets


class WebSocket:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance:
            return cls.instance
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        if cls.instance:
            return
        self.outgoing = Queue()
        self.responses = Queue()

    async def core(self):
        uri = f"wss://relay.damus.io"
        async with websockets.connect(uri, ssl=False) as websocket:
            self.websocket = websocket
            while True:
                payload = self.outgoing.get()
                await self._send(websocket, payload)
                response = await self._recv(websocket)
                self.responses.put(response)

    async def _send(self, websocket, payload):
        await websocket.send(json.dumps(payload).encode('utf-8'))

    async def _recv(self, websocket):
        data = await websocket.recv()
        return json.loads(data)

    def send(self, payload):
        self.outgoing.put(payload)
        return self.responses.get()

    async def fetch_text_notes(self):
        payload = {
            "method": "get",
            "type": "note",
            "kind": 1,
            "pubkey": "npub14ma4qdfprx5293ez8dzmu5vuavze6fk6sp37yv297n7wh54hcg3s76c5va"
        }
        response = self.send(payload)
        return response["data"]


if __name__ == "__main__":
    websocket = WebSocket()
    asyncio.run(websocket.core())
    text_notes = asyncio.run(websocket.fetch_text_notes())
    for note in text_notes:
        print(note["content"])
