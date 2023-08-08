import json
from aiohttp import web
from mautrix.types import EventType, RoomID
from maubot import Plugin, MessageEvent
from maubot.handlers import event, web
from nio import MatrixRoom, AsyncClient
import json
from aiohttp.web import Request, Response, json_response
import os

if not os.path.exists('rooms.json'):
    print("Run initialize.py first to create a lookup of room ID's")
    exit(1)

with open('rooms.json', 'r') as f:
    rooms = json.load(f)

class MessageServer(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            with open('messages.json', 'r') as f:
                self.messages = json.load(f)
            os.shutil.copyfile('messages.json', 'messages.json.bak')
        except:
            self.messages = []

    async def get_room_name(self, room_id):
        response = await self.client.get_room_info(room_id)
        print(response)
        return response['name']

    @event.on(EventType.ROOM_MESSAGE)
    async def handler(self, event: MessageEvent) -> None:
        if event.sender != self.client.mxid:
            try:
                if os.path.exists('blacklist.txt'):
                    with open('blacklist.txt', 'r') as f:
                        blacklist = f.read().splitlines()
                    if event.room_id in blacklist:
                        print(f"Skipping blacklisted room {event.room_id}")
                        return

                sender_info = await self.client.get_displayname(event.sender)

                if event.room_id in rooms:
                    source = rooms[event.room_id]['source']
                    names = rooms[event.room_id]['names']
                else:
                    source = ""
                    names = []
                timestamp = event.timestamp
                
                message_info = {
                    "from": sender_info,
                    "source": source,
                    "message": event.content.body,
                    "names": names if len(names) < 5 else names[:5]+["..."],
                    "timestamp": timestamp,
                    "participants": len(names),
                    "room_id": event.room_id,
                }
                
                self.messages.append(message_info)
                with open('messages.json', 'w') as f:
                    f.write(json.dumps(self.messages, indent=4))
                print(message_info)
            except Exception as e:
                print( f"Exception: {e}" )

    @web.get("/messages")
    async def get_messages(self, req: Request) -> Response:
        mcopy = self.messages.copy()

        query_params = req.rel_url.query
        source = query_params.get('source')
        since = query_params.get('since')
        sender = query_params.get('sender')

        if source:
            print(f"source: {source.lower()}")
            mcopy = [m for m in mcopy if m['source'].lower() == source.lower()]

        if since:
            print(f"since: {since}")
            since = int(since)
            mcopy = [m for m in mcopy if m['timestamp'] >= since]

        if sender:
            print(f"sender: {sender}")
            mcopy = [m for m in mcopy if sender.lower() in m['from'].lower()]

        return Response(text=json.dumps(mcopy, indent=4), content_type='application/json')

    @web.post("/messages")
    async def send_message(self, req: Request) -> Response:
        data = await req.json()
        print(data)
        room_id = data['room_id']
        message = data['message']
        print(f"Sending {message} to {room_id}")
        return Response(text="Message sent [debug mode, not really sent]", content_type='text/plain')
