import os
import textwrap
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pyrogram import filters
from pyrogram.types import Message
from SHUKLAMUSIC import app

@app.on_message(filters.command("mmf"))
async def mmf(_, message: Message):
    chat_id = message.chat.id
    reply_message = message.reply_to_message

    if len(message.text.split()) < 2:
        await message.reply_text("**Give me text after /mmf to memify.**")
        return

    msg = await message.reply_text("**Memifying this file! ✊🏻**")
    text = message.text.split(None, 1)[1]
    file = await app.download_media(reply_message)

    # Check if the file is a video or image based on file extension
    if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
        meme = await drawTextOnVideo(file, text)
    else:
        meme = await drawTextOnImage(file, text)

    await app.send_document(chat_id, document=meme)
    await msg.delete()

    os.remove(meme)


async def drawTextOnImage(image_path, text):
    img = Image.open(image_path)
    os.remove(image_path)

    i_width, i_height = img.size

    # Use a default font
    if os.name == "nt":
        fnt = "arial.ttf"
    else:
        fnt = "./Prince/assets/NewFont/defaulter.ttf"

    m_font = ImageFont.truetype(fnt, int((70 / 640) * i_width))

    # Split text into upper and lower parts if there's a semicolon
    if ";" in text:
        upper_text, lower_text = text.split(";")
    else:
        upper_text = text
        lower_text = ""

    draw = ImageDraw.Draw(img)
    current_h, pad = 10, 5

    # Draw upper text
    if upper_text:
        for u_text in textwrap.wrap(upper_text, width=15):
            u_width, u_height = draw.textsize(u_text, font=m_font)
            draw_text_with_shadow(draw, u_text, (i_width - u_width) / 2, current_h, m_font, (255, 255, 255))
            current_h += u_height + pad

    # Draw lower text
    if lower_text:
        current_h = i_height - 10
        for l_text in textwrap.wrap(lower_text, width=15):
            l_width, l_height = draw.textsize(l_text, font=m_font)
            draw_text_with_shadow(draw, l_text, (i_width - l_width) / 2, current_h - l_height, m_font, (255, 255, 255))
            current_h -= l_height + pad

    image_name = "memified_image.webp"
    img.save(image_name, "webp")

    return image_name


async def drawTextOnVideo(video_path, text):
    # Open video file
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Prepare output video writer
    output_path = "memified_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if os.name == "nt":
        fnt = "arial.ttf"
    else:
        fnt = "./Prince/assets/NewFont/defaulter.ttf"

    m_font = ImageFont.truetype(fnt, int((70 / 640) * width))

    # Loop through video frames
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to PIL Image for drawing
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)

        upper_text, lower_text = splitText(text)

        # Draw the text on the frame
        frame = addTextToFrame(pil_image, upper_text, lower_text, m_font, width, height)

        # Convert back to OpenCV format
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)

        # Write the modified frame to the output video
        out.write(frame)

    # Release video capture and writer
    cap.release()
    out.release()

    return output_path


def splitText(text):
    if ";" in text:
        upper_text, lower_text = text.split(";")
    else:
        upper_text = text
        lower_text = ""
    return upper_text, lower_text


def addTextToFrame(img, upper_text, lower_text, m_font, width, height):
    draw = ImageDraw.Draw(img)
    current_h, pad = 10, 5

    # Draw upper text
    if upper_text:
        for u_text in textwrap.wrap(upper_text, width=15):
            u_width, u_height = draw.textsize(u_text, font=m_font)
            draw_text_with_shadow(draw, u_text, (width - u_width) / 2, current_h, m_font, (255, 255, 255))
            current_h += u_height + pad

    # Draw lower text
    if lower_text:
        current_h = height - 10
        for l_text in textwrap.wrap(lower_text, width=15):
            l_width, l_height = draw.textsize(l_text, font=m_font)
            draw_text_with_shadow(draw, l_text, (width - l_width) / 2, current_h - l_height, m_font, (255, 255, 255))
            current_h -= l_height + pad

    return img


def draw_text_with_shadow(draw, text, x, y, font, color):
    # Draw shadow
    draw.text((x - 2, y - 2), text, font=font, fill=(0, 0, 0))
    draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0))
    # Draw main text
    draw.text((x, y), text, font=font, fill=color)

