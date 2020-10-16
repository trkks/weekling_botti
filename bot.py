import asyncio
import json
import io
#import os
#import sys
#import getpass

from nio import (AsyncClient, MatrixRoom, RoomMessageText, LoginResponse,
                 LoginError)

# TODO add logging
# TODO handle logouts

LOGIN_FILE = "bot_login_info.json"

async def message_callback(room: MatrixRoom, event: RoomMessageText) -> None:
    # TODO Listen to all joined rooms -> one bot to serve them all?
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


def load_bot_info():
    """
    Load the login and room info from external file and 
    return them as a dict or None if failed
    """
    info = None
    # Load info from json-file
    # NOTE the file is to be filled locally, do not add to git!
    try:
        with io.open(LOGIN_FILE, "r", encoding="utf-8") as fp:
            info = json.load(fp)
            print(f"Loaded bot initialization info: {info}")
    #TODO just crash here instead?
    except OSError as e:
        print(f"Reading login-info failed: {e}")
    except ValueError as e:
        print(f"Decoding login-info from JSON failed: {e}")
        
    return info


# NOTE bot_ -prefix because the nio API has a static function called 'login()'
async def bot_login(bot_info):
    """
    Create the client-object with correct info and login 
    if an access token is not found, login with password 
    Return the client and login-response
    """
    client = AsyncClient(bot_info["homeserver"], bot_info["user_id"])
    response = None
    #TODO handle keys not being in bot_info or just crash?
    if "access_token" not in bot_info:
        #TODO Ask password from command line instead (getpass())?
        response = await client.login(bot_info["password"])
        if isinstance(response, LoginResponse):
            # Save access token to file for future use
            bot_info["access_token"] = response.access_token
            #TODO Set all the rooms bot has previously been invited to and to
            # which it will listen 
            if len(bot_info["joined_rooms"]) > 0:
                #TODO
                client.room_id = bot_info["joined_rooms"][0]
                print("Bot has been set the first room listed: {}"
                      .format(bot_info["joined_rooms"][0]))
            else:
                client = None
                print("No rooms to listen to specified.")
            try:
                with io.open(LOGIN_FILE, "w", encoding="utf-8") as fp:
                    fp.write(json.dumps(bot_info))
            except OSError as e:
                print(f"Writing login-info failed: {e}")
        else: #Login failed
            client = None
    else:
        #TODO
        print("NOT IMPLEMENTED: Logging in with the present access token.")
        client = None

    return (client, response)


async def main() -> None:
    info = load_bot_info()
    (client, login_resp) = await bot_login(info) if info else (None,None)
    if client:
        print(f"Logged in as {client}: {login_resp}")
        # NOTE bot-functionality commented out as not to accidentally do stupid
        # stuff on matrix rooms
        # Add the functionality for reacting to matrix-events
        #client.add_event_callback(message_callback, RoomMessageText)

        # Send initial greeting to rooms bot has joined
        # TODO Pitäisköhän vaan poistaa weekling sieltä muista paitsi
        # testihuoneista, ettei lähetetä vahingossa spämmiä?
        #await client.room_send(
        #    # Watch out! If you join an old room you'll see lots of old
        #    # messages 
        #    room_id=client.room_id,
        #    message_type="m.room.message",
        #    content = {
        #        "msgtype": "m.text",
        #        #"body": "Moi t.botti"
        #    }
        #) 

        # This is from the tutorial:
        # If you made a new room and haven't joined as that user, you can use
        # await client.join("your-room-id")

        #await client.sync_forever(timeout=30000) # milliseconds
        print("Logging out... {}".format(await client.logout()))
    else: 
        print(f"Login as {client} failed: {login_resp}") 


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
