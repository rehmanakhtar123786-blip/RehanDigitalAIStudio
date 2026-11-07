
import streamlit as st
import tempfile
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
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

st.header("📹 Video Upload")

videos = st.file_uploader(
    "ویڈیو اپلوڈ کریں (ایک یا زیادہ)",
    type=["mp4", "mov", "avi"],
    accept_multiple_files=True
)

st.header("🖼️ Image to Poetry Video")

image_upload = st.file_uploader(
    "تصویر اپلوڈ کریں",
    type=["jpg", "jpeg", "png"]
)

image_duration = st.slider(
    "تصویر والی ویڈیو کتنے سیکنڈ کی ہو؟",
    5, 60, 15
)

st.header("✍️ Urdu Poetry")

poetry = st.text_area(
    "اپنی اردو شاعری یہاں لکھیں",
    value=shayari_options[selected_shayari],
    placeholder="دل کی بات شاعری میں لکھیں... ❤️",
    height=130
)

font_size = st.slider("شاعری کا سائز", 20, 100, 45)

font_color = st.selectbox(
    "شاعری کا رنگ",
    ["White", "Yellow", "Red", "Green", "Cyan"]
)

position = st.selectbox(
    "شاعری کہاں دکھانی ہے؟",
    ["Top", "Center", "Bottom"]
)

st.header("✨ Text Animation")

animation = st.selectbox(
    "Animation منتخب کریں",
    ["Fade In", "No Animation"]
)

st.header("🔤 Urdu Font")

st.info(
    "Noto Nastaliq Urdu کی درست TTF/OTF فونٹ فائل اپلوڈ کریں۔"
)

font_upload = st.file_uploader(
    "Upload Noto Nastaliq Urdu Font",
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
    "Music اپلوڈ کریں (Optional)",
    type=["mp3", "wav", "m4a"]
)

volume = st.slider(
    "Music Volume",
    0.0, 1.0, 0.3
)


def make_vertical(clip, target_w, target_h):

    scale = max(
        target_w / clip.w,
        target_h / clip.h
    )

    resized = clip.resized(
        new_size=(
            int(clip.w * scale),
            int(clip.h * scale)
        )
    )

    x1 = (resized.w - target_w) // 2
    y1 = (resized.h - target_h) // 2

    return resized.cropped(
        x1=x1,
        y1=y1,
        x2=x1 + target_w,
        y2=y1 + target_h
    )


if st.button("🎬 Create My Final Video"):

    if not videos and image_upload is None:
        st.warning("براہ کرم ویڈیو یا تصویر اپلوڈ کریں۔")

    elif videos and image_upload is not None:
        st.warning(
            "براہ کرم ایک وقت میں صرف ویڈیو یا تصویر منتخب کریں۔"
        )

    elif not poetry.strip():
        st.warning("براہ کرم شاعری لکھیں یا منتخب کریں۔")

    elif font_upload is None:
        st.warning(
            "براہ کرم Noto Nastaliq Urdu کی فونٹ فائل اپلوڈ کریں۔"
        )

    else:

        video_clips = []
        audio_clips = []
        music_parts = []
        temp_files = []

        base = None
        final = None
        music_clip = None
        output_path = None

        try:

            # Save uploaded font
            font_temp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(font_upload.name)[1]
            )

            font_temp.write(font_upload.getvalue())
            font_temp.close()

            temp_files.append(font_temp.name)

            font = ImageFont.truetype(
                font_temp.name,
                font_size
            )

            # Create video from uploaded videos
            if videos:

                for video in videos:

                    suffix = os.path.splitext(video.name)[1] or ".mp4"

                    temp = tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=suffix
                    )

                    temp.write(video.getvalue())
                    temp.close()

                    temp_files.append(temp.name)

                    video_clips.append(
                        VideoFileClip(temp.name)
                    )

                if len(video_clips) == 1:
                    base = video_clips[0]

                else:
                    base = concatenate_videoclips(
                        video_clips,
                        method="compose"
                    )

            # Create video from image
            else:

                image = Image.open(image_upload).convert("RGB")

                if video_format == "9:16 (Reels / TikTok)":

                    target_w = 720 if resolution == "720p" else 1080
                    target_h = 1280 if resolution == "720p" else 1920

                    image = ImageOps.fit(
                        image,
                        (target_w, target_h)
                    )

                base = ImageClip(
                    np.array(image)
                ).with_duration(
                    image_duration
                ).with_fps(24)

            # Resize uploaded videos
            if videos and video_format == "9:16 (Reels / TikTok)":

                target_w = 720 if resolution == "720p" else 1080
                target_h = 1280 if resolution == "720p" else 1920

                base = make_vertical(
                    base,
                    target_w,
                    target_h
                )

            width = int(base.w)
            height = int(base.h)

            # Urdu text shaping
            reshaped = arabic_reshaper.reshape(poetry)
            display_text = get_display(reshaped)

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
            ).with_duration(
                base.duration
            ).with_fps(24)

            if animation == "Fade In":

                poetry_layer = poetry_layer.with_effects(
                    [vfx.FadeIn(1.5)]
                )

            final = CompositeVideoClip(
                [base, poetry_layer],
                size=(width, height)
            ).with_duration(
                base.duration
            )

            # Add background music
            if music is not None:

                audio_temp = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".mp3"
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

                    music_clip = concatenate_audioclips(
                        music_parts
                    )

                else:
                    music_clip = original_music

                music_clip = music_clip.subclipped(
                    0,
                    final.duration
                ).with_volume_scaled(volume)

                final = final.with_audio(music_clip)

            # Export video
            output_temp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            )

            output_path = output_temp.name
            output_temp.close()

            st.info("آپ کی ویڈیو بن رہی ہے، انتظار کریں...")

            # FIXED FPS
            export_fps = getattr(base, "fps", None) or 24

            final.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=export_fps
            )

            st.success(
                "آپ کی شاعری والی ویڈیو تیار ہے! ❤️"
            )

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

            st.info(
                "اگر اردو کے خانے نظر آئیں تو کوئی دوسری "
                "درست Noto Nastaliq Urdu TTF فائل آزمائیں۔"
            )

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
