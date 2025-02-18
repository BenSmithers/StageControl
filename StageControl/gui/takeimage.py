
import asyncio
from open_gopro import Params, WiredGoPro, WirelessGoPro, proto

import os 

import datetime 
from PIL import Image, ImageDraw, ImageFont, ImageOps

# setting 90 is for turning "auto" on/off for exposure time
# setting 19
exposure_times = [
    "Auto",
    2,5,10,15,20,30
]

# iso min is setting 24 
# iso max is setting 75
isos = [
    100, 200, 400, 800
]



async def main(sno):

    async with WiredGoPro(sno) as gopro:
        assert gopro
        assert (await gopro.http_command.load_preset_group(group=proto.EnumPresetGroup.PRESET_GROUP_ID_PHOTO)).ok

        media_set_before = set((await gopro.http_command.get_media_list()).data.files)
                    
        # Take a photo
        assert (await gopro.http_command.set_shutter(shutter=Params.Toggle.ENABLE)).ok

        # Get the media list after
        media_set_after = set((await gopro.http_command.get_media_list()).data.files)
        # The video (is most likely) the difference between the two sets
        photo = media_set_after.difference(media_set_before).pop()

        # Download the photo
        print(f"Downloading {photo.filename}...")
        await gopro.http_command.download_file(camera_file=photo.filename, local_file="./photo.jpg")
        await gopro.http_command.delete_all()
        print("We have purged the database.")

def entrypoint(cno=0):
    if cno==0:
        ip_add = "172.29.134.51"
        sno = "006934"
    else:
        ip_add = "172.29.106.51"
        sno = "185906"
    asyncio.run(main(sno))

    image = Image.open("photo.jpg")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(120)
    draw.text((0, 0),str(datetime.datetime.now()),(255,255,255),font=font)
    image.save("photo_camera_{}.jpg".format(cno))
    os.remove("photo.jpg")


if __name__=="__main__":
    entrypoint(0)