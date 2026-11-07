
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
    concatenate_audioclips
)
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(page_title="Rehan AI Studio", page_icon="🎬")

st.title("🎬 Rehan AI Studio")
st.subheader("Your Personal Video Editing Studio ❤️")

st.header("📹 Upload Your Video")

videos = st.file_uploader(
    "Select one or more videos",
    type=["mp4", "mov", "avi"],
    accept_multiple_files=True
)

st.header("✍️ Write Urdu Poetry")

poetry = st.text_area(
    "اپنی اردو شاعری یہاں لکھیں",
    placeholder="دل کی بات شاعری میں لکھیں... ❤️",
    height=120
)

font_size = st.slider("Poetry Font Size", 20, 100, 45)

font_color = st.selectbox(
    "Poetry Color",
    ["White", "Yellow", "Red", "Green", "Cyan"]
)

position = st.selectbox(
    "Poetry Position",
    ["Top", "Center", "Bottom"]
)

st.info("بہترین اردو لکھائی کے لیے Noto Nastaliq Urdu کی TTF فونٹ فائل اپلوڈ کریں۔")

font_upload = st.file_uploader(
    "Upload Urdu Font (TTF)",
    type=["ttf", "otf"]
)

st.header("🎵 Background Music")

music = st.file_uploader(
    "Select MP3 Music (Optional)",
    type=["mp3", "wav", "m4a"]
)

volume = st.slider("Music Volume", 0.0, 1.0, 0.3)

if st.button("🎬 Create My Final Video"):

    if not videos:
        st.warning("Please upload at least one video.")

    elif not poetry.strip():
        st.warning("Please write your Urdu poetry first.")

    else:
        video_clips = []
        audio_clips = []
        music_parts = []
        final = None
        output_path = None
        temp_files = []

        try:
            # Save uploaded videos
            for video in videos:
                suffix = os.path.splitext(video.name)[1] or ".mp4"

                temp = tempfile.NamedTemporaryFile(
                    delete=False, suffix=suffix
                )
                temp.write(video.getvalue())
                temp.close()
                temp_files.append(temp.name)

                video_clips.append(VideoFileClip(temp.name))

            # Join videos, or use one video
            if len(video_clips) == 1:
                base = video_clips[0]
            else:
                base = concatenate_videoclips(
                    video_clips, method="compose"
                )

            final = base

            # Choose Urdu font
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

            # Shape Urdu text
            shaped_text = arabic_reshaper.reshape(poetry)
            display_text = get_display(shaped_text)

            # Create transparent poetry layer
            width, height = int(base.w), int(base.h)
            overlay = Image.new(
                "RGBA", (width, height), (0, 0, 0, 0)
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

            x = max(10, (width - text_width) // 2)

            if position == "Top":
                y = 50
            elif position == "Center":
                y = (height - text_height) // 2
            else:
                y = height - text_height - 70

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

            poetry_layer = ImageClip(
                np.array(overlay)
            ).with_duration(base.duration)

            final = CompositeVideoClip(
                [base, poetry_layer]
            )

            # Add optional background music
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
                        audio_parts = AudioFileClip(audio_temp.name)
                        music_parts.append(audio_parts)

                    music_clip = concatenate_audioclips(music_parts)
                else:
                    music_clip = original_music

                music_clip = music_clip.subclipped(
                    0, final.duration
                ).with_volume_scaled(volume)

                final = final.with_audio(music_clip)

            # Export final video
            output_temp = tempfile.NamedTemporaryFile(
                delete=False, suffix=".mp4"
            )
            output_path = output_temp.name
            output_temp.close()

            final.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=base.fps
            )

            st.success("Your Urdu Poetry Video Is Ready! ❤️")
            st.video(output_path)

            with open(output_path, "rb") as file:
                st.download_button(
                    "⬇️ Download Final Video",
                    file,
                    file_name="Rehan_Urdu_Poetry_Video.mp4",
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
