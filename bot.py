import asyncio
import json
import os
import sys
import getpass

from nio import AsyncClient, MatrixRoom, RoomMessageText

ROOM_ID =  ***JOINED_ROOM_ID*** #NOTE
client = AsyncClient(***BOT_HOMESERVER***, #NOTE
                     ***BOT_USER_ID***) #NOTE

async def message_callback(room: MatrixRoom, event: RoomMessageText) -> None:
    if room.room_id == client.room_id and event.sender != client.user_id:
        await client.room_send(
            room_id=client.room_id,
            message_type="m.room.message",
            content = {
                "msgtype":"m.text",
                "body": f"Message received in room {room.display_name}\n"\
                        f"{room.user_name(event.sender)} | {event.body}"
            }
        )

async def main() -> None:
    client.access_token = ***BOT_ACCESS_TOKEN*** #NOTE

    client.add_event_callback(message_callback, RoomMessageText)
    client.room_id = ROOM_ID

    # If you made a new room and haven't joined as that user, you can use
    # await client.join("your-room-id")

    # TODO enable access_token-only login
    await client.login(***BOT_PASSWORD***) #NOTE 
    print("Logged in")

    await client.room_send(
        # Watch out! If you join an old room you'll see lots of old messages
        room_id=client.room_id,
        message_type="m.room.message",
        content = {
            "msgtype": "m.text",
            #"body": "Moi t.botti"
        }
    )

    await client.sync_forever(timeout=30000) # milliseconds

# TODO 
#if __name__ == "__main__":
#    try:
#        asyncio.run( 
#            main() 
#        )
#    except (KeyboardInterrupt):
#        pass

asyncio.get_event_loop().run_until_complete(main())
