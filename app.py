
import streamlit as st
import tempfile
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    CompositeVideoClip,
    concatenate_videoclips,
    concatenate_audioclips,
    vfx
)
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(
    page_title="Rehan AI Studio",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Rehan AI Studio")
st.subheader("Your Personal Video Editing Studio ❤️")

# Ready Urdu poetry
shayari_options = {
    "اپنی شاعری خود لکھیں": "",
    "اداس شاعری": "ہنستے ہوئے چہرے کے پیچھے غم چھپائے بیٹھے ہیں،\nہم بھی کسی کے انتظار میں دل لگائے بیٹھے ہیں۔",
    "محبت کی شاعری": "تیری یادوں کا چراغ دل میں جلائے رکھتے ہیں،\nہم آج بھی تجھے اپنا بنائے رکھتے ہیں۔",
    "زندگی کی شاعری": "زندگی نے ہر قدم پر نیا سبق سکھایا ہے،\nجو اپنا تھا کبھی، وقت نے اسے بھی آزمایا ہے۔",
    "دوستی کی شاعری": "دوستی نام ہے مشکل میں ساتھ نبھانے کا،\nصرف خوشیوں میں نہیں، غم میں بھی کام آنے کا۔"
}

st.header("🥀 Ready Urdu Shayari")

selected_shayari = st.selectbox(
    "شاعری منتخب کریں",
    list(shayari_options.keys())
)

st.header("📹 Upload Your Video")

videos = st.file_uploader(
    "Select one or more videos",
    type=["mp4", "mov", "avi"],
    accept_multiple_files=True
)

st.header("✍️ Write Urdu Poetry")

default_poetry = shayari_options[selected_shayari]

poetry = st.text_area(
    "اپنی اردو شاعری یہاں لکھیں",
    value=default_poetry,
    placeholder="دل کی بات شاعری میں لکھیں... ❤️",
    height=130
)

font_size = st.slider(
    "Poetry Font Size",
    20, 100, 45
)

font_color = st.selectbox(
    "Poetry Color",
    ["White", "Yellow", "Red", "Green", "Cyan"]
)

position = st.selectbox(
    "Poetry Position",
    ["Top", "Center", "Bottom"]
)

st.header("✨ Text Animation")

animation = st.selectbox(
    "Choose Animation",
    ["Fade In", "No Animation"]
)

st.info(
    "بہترین اردو لکھائی کے لیے Noto Nastaliq Urdu کی TTF فونٹ فائل اپلوڈ کریں۔"
)

font_upload = st.file_uploader(
    "Upload Urdu Font",
    type=["ttf", "otf"]
)

st.header("📱 Video Format")

video_format = st.selectbox(
    "Video Size",
    ["9:16 (Reels / TikTok)", "Original Video"]
)

resolution = st.selectbox(
    "Video Quality",
    ["720p", "1080p"]
)

st.header("🎵 Background Music")

music = st.file_uploader(
    "Select MP3 Music (Optional)",
    type=["mp3", "wav", "m4a"]
)

volume = st.slider(
    "Music Volume",
    0.0, 1.0, 0.3
)

if st.button("🎬 Create My Final Video"):

    if not videos:
        st.warning("Please upload at least one video.")

    elif not poetry.strip():
        st.warning("Please write or select Urdu poetry.")

    else:
        video_clips = []
        audio_clips = []
        music_parts = []
        final = None
        base = None
        music_clip = None
        poetry_layer = None
        temp_files = []
        output_path = None

        try:
            # Save and open uploaded videos
            for video in videos:
                suffix = os.path.splitext(video.name)[1] or ".mp4"

                temp = tempfile.NamedTemporaryFile(
                    delete=False, suffix=suffix
                )
                temp.write(video.getvalue())
                temp.close()
                temp_files.append(temp.name)

                video_clips.append(VideoFileClip(temp.name))

            # Join videos
            if len(video_clips) == 1:
                base = video_clips[0]
            else:
                base = concatenate_videoclips(
                    video_clips, method="compose"
                )

            # Make vertical 9:16 video if selected
            if video_format == "9:16 (Reels / TikTok)":
                target_w = 720 if resolution == "720p" else 1080
                target_h = 1280 if resolution == "720p" else 1920

                scale = max(
                    target_w / base.w,
                    target_h / base.h
                )

                resized = base.resized(
                    new_size=(
                        int(base.w * scale),
                        int(base.h * scale)
                    )
                )

                x1 = (resized.w - target_w) // 2
                y1 = (resized.h - target_h) // 2

                base = resized.cropped(
                    x1=x1,
                    y1=y1,
                    x2=x1 + target_w,
                    y2=y1 + target_h
                )

            final = base

            # Select font
            if font_upload is not None:
                font_temp = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".ttf"
                )
                font_temp.write(font_upload.getvalue())
                font_temp.close()
                temp_files.append(font_temp.name)
                font_path = font_temp.name
            else:
                font_path = (
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                )

            font = ImageFont.truetype(font_path, font_size)

            # Urdu text shaping
            shaped_text = arabic_reshaper.reshape(poetry)
            display_text = get_display(shaped_text)

            width = int(base.w)
            height = int(base.h)

            overlay = Image.new(
                "RGBA",
                (width, height),
                (0, 0, 0, 0)
            )

            draw = ImageDraw.Draw(overlay)

            colors = {
                "White": "white",
                "Yellow": "yellow",
                "Red": "red",
                "Green": "lime",
                "Cyan": "cyan"
            }

            bbox = draw.multiline_textbbox(
                (0, 0),
                display_text,
                font=font,
                spacing=12,
                align="center",
                stroke_width=2
            )

            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (width - text_width) // 2 - bbox[0]

            if position == "Top":
                y = 50 - bbox[1]
            elif position == "Center":
                y = (height - text_height) // 2 - bbox[1]
            else:
                y = height - text_height - 70 - bbox[1]

            draw.multiline_text(
                (x, y),
                display_text,
                font=font,
                fill=colors[font_color],
                spacing=12,
                align="center",
                stroke_width=2,
                stroke_fill="black"
            )

            # Add poetry overlay
            poetry_layer = ImageClip(
                np.array(overlay)
            ).with_duration(base.duration)

            # Text animation
            if animation == "Fade In":
                poetry_layer = poetry_layer.with_effects(
                    [vfx.FadeIn(1.5)]
                )

            final = CompositeVideoClip(
                [base, poetry_layer],
                size=(width, height)
            ).with_duration(base.duration)

            # Add background music
            if music is not None:
                audio_temp = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".mp3"
                )
                audio_temp.write(music.getvalue())
                audio_temp.close()
                temp_files.append(audio_temp.name)

                original_music = AudioFileClip(audio_temp.name)
                audio_clips.append(original_music)

                if original_music.duration < final.duration:
                    count = math.ceil(
                        final.duration / original_music.duration
                    )

                    for _ in range(count):
                        part = AudioFileClip(audio_temp.name)
                        music_parts.append(part)

                    music_clip = concatenate_audioclips(music_parts)
                else:
                    music_clip = original_music

                music_clip = music_clip.subclipped(
                    0, final.duration
                ).with_volume_scaled(volume)

                final = final.with_audio(music_clip)

            # Export video
            output_temp = tempfile.NamedTemporaryFile(
                delete=False, suffix=".mp4"
            )
            output_path = output_temp.name
            output_temp.close()

            st.info("آپ کی ویڈیو بن رہی ہے، براہ کرم انتظار کریں...")

            final.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=base.fps or 24
            )

            st.success("Your Urdu Poetry Video Is Ready! ❤️")

            st.video(output_path)

            with open(output_path, "rb") as file:
                st.download_button(
                    "⬇️ Download Final Video",
                    file,
                    file_name="Rehan_AI_Studio_Video.mp4",
                    mime="video/mp4"
                )

        except Exception as e:
            st.error(f"Error: {e}")

        finally:
            if final is not None:
                try:
                    final.close()
                except Exception:
                    pass

            if base is not None:
                try:
                    base.close()
                except Exception:
                    pass

            for clip in video_clips:
                try:
                    clip.close()
                except Exception:
                    pass

            for clip in audio_clips + music_parts:
                try:
                    clip.close()
                except Exception:
                    pass

            for path in temp_files:
                try:
                    os.remove(path)
                except OSError:
                    pass
