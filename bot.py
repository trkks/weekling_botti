#!/usr/bin/env python3

import asyncio
import json
import os
import sys
import getpass
#from PIL import Image
#import aiofiles.os
#import magic

from nio import AsyncClient, LoginResponse, UploadResponse

CONFIG_FILE = "credentials.json"

# Check out main() below to see how it's done.


def write_details_to_disk(resp: LoginResponse, homeserver) -> None:
    """Writes the required login details to disk so we can log in later without
    using a password.

    Arguments:
        resp {LoginResponse} -- the successful client login response.
        homeserver -- URL of homeserver, e.g. "https://matrix.example.org"
    """
    # open the config file in write-mode
    with open(CONFIG_FILE, "w") as f:
        # write the login details to disk
        json.dump(
            {
                "homeserver": homeserver,  # e.g. "https://matrix.example.org"
                "user_id": resp.user_id,  # e.g. "@user:example.org"
                "device_id": resp.device_id,  # device ID, 10 uppercase letters
                "access_token": resp.access_token  # cryptogr. access token
            },
            f
        )


async def send_image(client, room_id, image):
    """Send image to toom.

    Arguments:
    ---------
    client : Client
    room_id : str
    image : str, file name of image

    This is a working example for a JPG image.
        "content": {
            "body": "someimage.jpg",
            "info": {
                "size": 5420,
                "mimetype": "image/jpeg",
                "thumbnail_info": {
                    "w": 100,
                    "h": 100,
                    "mimetype": "image/jpeg",
                    "size": 2106
                },
                "w": 100,
                "h": 100,
                "thumbnail_url": "mxc://example.com/SomeStrangeThumbnailUriKey"
            },
            "msgtype": "m.image",
            "url": "mxc://example.com/SomeStrangeUriKey"
        }

    """
    #mime_type = magic.from_file(image, mime=True)  # e.g. "image/jpeg"
    #if not mime_type.startswith("image/"):
    #    print("Drop message because file does not have an image mime type.")
    #    return

    #im = Image.open(image)
    #(width, height) = im.size  # im.size returns (width,height) tuple

    ## first do an upload of image, then send URI of upload to room
    #file_stat = await aiofiles.os.stat(image)
    #async with aiofiles.open(image, "r+b") as f:
    #    resp, maybe_keys = await client.upload(
    #        f,
    #        content_type=mime_type,  # image/jpeg
    #        filename=os.path.basename(image),
    #        filesize=file_stat.st_size)
    #if (isinstance(resp, UploadResponse)):
    #    print("Image was uploaded successfully to server. ")
    #else:
    #    print(f"Failed to upload image. Failure response: {resp}")

    content = {
        "body": os.path.basename(image),  # descriptive title
        "info": {
            "size": file_stat.st_size,
            "mimetype": mime_type,
            "thumbnail_info": None,  # TODO
            "w": width,  # width in pixel
            "h": height,  # height in pixel
            "thumbnail_url": None,  # TODO
        },
        "msgtype": "m.image",
        "url": resp.content_uri,
    }

    try:
        await client.room_send(
            room_id,
            message_type="m.room.message",
            content=content
        )
        print("Image was sent successfully")
    except Exception:
        print(f"Image send of file {image} failed.")


async def main() -> None:
    # Otherwise the config file exists, so we'll use the stored credentials
    # open the file in read-only mode
    client = AsyncClient("***HOMESERVER***", "***MATRIX_USER***") #NOTE
    client.access_token = "***ACCESS_TOKEN***" #NOTE
    
    #client.user_id = config['user_id']
    #client.device_id = config['device_id']

    # Now we can send messages as the user
    room_id = "***ROOM_ID***" #NOTE
    #room_id = input(f"Enter room id for image message: [{room_id}] ")

    #image = "exampledir/samplephoto.jpg"
    #image = input(f"Enter file name of image to send: [{image}] ")

    #await send_image(client, room_id, image)
    await client.room_send(
        room_id = room_id,
        message_type="m.room.message",
        content = {
            "msgtype":"m.text",
            "body":"Moi"
        }
    )

    client.login()
    print("Logged in using stored credentials. Sent a test message.")

    # Close the client connection after we are done with it.
    await client.close()

asyncio.get_event_loop().run_until_complete(main())
