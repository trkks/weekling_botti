import asyncio
import json
import io
#import os
import sys
import getpass
import datetime
from itertools import takewhile

from pymongo import MongoClient
from nio import (AsyncClient, MatrixRoom, RoomMessageText, InviteMemberEvent, 
                 LoginResponse, LoginError, JoinError)

import logic

# TODO handle logouts

LOGIN_FILE = "bot_login_info.json"

# Hemppa-hack-copypaste
def hemppa_hack(body, jointime, join_hack_time):
    # HACK to ignore messages for some time after joining.
    if jointime:
        if (datetime.datetime.now() - jointime).seconds < join_hack_time:
            print(f"Waiting for join delay, ignoring message: {body}")
            return False
        jointime = None 
    return True
# end of copypaste


def pass_to_invite_callback(client):

    async def invite_callback(room, event):
        result = await client.join(room.room_id)
        if type(result) == JoinError:
            print(f"Error joining room {room.room_id}")
        else:
            # Send initial greeting to rooms bot has joined
            # NOTE Will crash here if login failed
            await client.room_send(
                # Watch out! If you join an old room you'll see lots of old
                # messages 
                room_id=room.room_id,
                message_type="m.room.message",
                content = {
                    "msgtype": "m.text",
                    "body": "Terve t.botti"
                }
            ) 
    
            print(f"Joining room '{room.display_name}'({room.room_id})"\
                  f"invited by '{event.sender}'")

    return invite_callback

def pass_to_message_callback(client, db, jointime, join_hack_time):

    async def message_callback(room: MatrixRoom, event: RoomMessageText) -> None:
        if hemppa_hack(event.body, jointime, join_hack_time):
            print("event.sender == {}".format(event.sender))
            print("client.user_id == {}".format(client.user_id))
            # TODO Listen to all joined rooms -> one bot to serve them all?
            if room.room_id in client.rooms.keys() \
            and event.sender != client.user_id:
                msg = event.body.strip()
                print("event.body: {}".format(event.body))
                if len(msg) > 1 and msg[0] == "!":
                    msg = msg[1:]
                    command = None
                    args = ""
                    hours = 1
                    if " " in msg:
                        try:
                            command = msg[0:msg.index(" ")] 
                            args = msg[len(command):]
                            if "_" in command:
                                hours = int(command[command.index("_")+1:])
                                command = msg[0:msg.index("_")] 
                        except ValueError:
                            command = None
                            args = ""
                    print("msg: '{}'".format(msg))

                    # Choose the logic
                    msg_to_send = None

                    if command == "aloita":
                        msg_to_send = logic.aloita(args, room.room_id, db)
                    elif command == "tulokset":
                        msg_to_send = logic.tulokset(hours, args, room.room_id, db)
                    elif command == "kaikki":
                        msg_to_send = logic.kaikki(hours, args, room.room_id, db)
                    elif msg == "ohje":
                        print("helping")
                        msg_to_send = logic.ohje()

                    if msg_to_send:
                        await client.room_send(
                            room_id=room.room_id,
                            message_type="m.room.message",
                            content = {
                                "msgtype":"m.text",
                                "body": msg_to_send
                            }
                        )

    return message_callback


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

    mongo_client = MongoClient("mongodb+srv://{}:{}@{}/weekling?retryWrites=true&w=majority".format(bot_info["db_username"], 
                    bot_info["db_password"],
                    bot_info["db_hostname"]))
    db = mongo_client.weekling  

    
    # NOTE Hemppa-hack
    jointime = datetime.datetime.now() # HACKHACKHACK to avoid running old 
                                       # commands after join
    join_hack_time = 5  # Seconds

    """
    Create the client-object with correct info and login 
    if an access token is not found, login with password 
    Return the client and login-response
    """
    client = AsyncClient(bot_info["homeserver"])
   
    client.add_event_callback(
        pass_to_invite_callback(client),
        InviteMemberEvent
    )

    client.add_event_callback(
        pass_to_message_callback(client, db, jointime, join_hack_time),
        RoomMessageText
    )

 
    # Ask password from command line, press enter to use stored access token
    access_token = bot_info["access_token"]
    user_id = bot_info["user_id"]
    if len(access_token) != 0 and len(user_id) != 0: 
        client.access_token = access_token
        # Manually set user id because not calling client.login()
        client.user_id = user_id
        #client.device_id = bot_info["device_id"]
    else: 
        password = getpass.getpass()
        response = await client.login(password)
        # Save info to file for future use
        bot_info["access_token"] = response.access_token
        #bot_info["device_id"] = response.device_id
        try:
            with io.open(LOGIN_FILE, "w", encoding="utf-8") as fp:
                fp.write(json.dumps(bot_info))
        except OSError as e:
            print(f"Writing login-info failed: {e}")

    print(f"Logged in as {client}")

    await client.sync_forever(timeout=30000, full_state=False) # milliseconds


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
