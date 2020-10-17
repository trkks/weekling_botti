import asyncio
import json
import io
#import os
import sys
import getpass

from nio import (AsyncClient, MatrixRoom, RoomMessageText, LoginResponse,
                 LoginError)

# TODO add logging
# TODO handle logouts

LOGIN_FILE = "bot_login_info.json"
client = None

async def message_callback(room: MatrixRoom, event: RoomMessageText) -> None:
    # TODO Listen to all joined rooms -> one bot to serve them all?
    #FIXME Crashes here because client == None, as set in global scope
    if room.room_id == client.room_id and event.sender != client.user_id:
        msg = event.body
        if len(msg) > 1 and msg[0] == "!":
            msg = msg.split(" ")
            if len(msg) > 0 and len(msg[0]) > 0 and msg[1:] == "close":
                await client.close()
            else: 
                await client.room_send(
                    room_id=client.room_id,
                    message_type="m.room.message",
                    content = {
                        "msgtype":"m.text",
                        "body": "Message received in room {}\n"
                                .format(room.display_name) +
                                f"{room.user_name(event.sender)} | {event.body}"
                    }
                )


def load_bot_info():
    """
    Load the login and room info from external file and 
    return them as a dict or None if failed
    """
    # Load info from json-file
    # NOTE the file is to be filled locally, do not add to git!
    with io.open(LOGIN_FILE, "r", encoding="utf-8") as fp:
        info = json.load(fp)
        print(f"Loaded bot initialization info: {info}")

    return info


async def main() -> None:
    bot_info = load_bot_info()

    """
    Create the client-object with correct info and login 
    if an access token is not found, login with password 
    Return the client and login-response
    """
    client = AsyncClient(bot_info["homeserver"], bot_info["user_id"])
    #TODO Set all the rooms bot has previously been invited to and to
    # which it will listen 
    client.room_id = bot_info["joined_rooms"][0] #NOTE
    print(f"DEBUG: {client.room_id}")
    # NOTE bot-functionality commented out as not to accidentally do stupid
    # stuff on matrix rooms
    # Add the functionality for reacting to matrix-events

    # Ask password from command line
    password = getpass.getpass()
    if password: ##isinstance(response, LoginResponse):
        response = await client.login(password)
        # Save info to file for future use
        bot_info["access_token"] = response.access_token
        #bot_info["device_id"] = response.device_id
        try:
            with io.open(LOGIN_FILE, "w", encoding="utf-8") as fp:
                fp.write(json.dumps(bot_info))
        except OSError as e:
            print(f"Writing login-info failed: {e}")
    else: #"Login" with access token
        client.access_token = bot_info["access_token"]
        #client.device_id = bot_info["device_id"]


    #FIXME client == None in message_callback -> read more about asyncio
    client.add_event_callback(message_callback, RoomMessageText)

    # Send initial greeting to rooms bot has joined
    # NOTE Will crash here if login failed
    await client.room_send(
        # Watch out! If you join an old room you'll see lots of old
        # messages 
        room_id=client.room_id,
        message_type="m.room.message",
        content = {
            "msgtype": "m.text",
            "body": "Moi t.botti"
        }
    ) 
    print(f"Logged in as {client}, sent a test message to {client.room_id}")

    # This is from the tutorial:
    # If you made a new room and haven't joined as that user, you can use
    # await client.join("your-room-id")

    await client.sync_forever(timeout=30000) # milliseconds


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
