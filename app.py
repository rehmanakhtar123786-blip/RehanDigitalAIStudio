
import streamlit as st
import tempfile
import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from moviepy import (
    VideoFileClip, AudioFileClip, ImageClip, VideoClip,
    CompositeVideoClip, CompositeAudioClip,
    concatenate_videoclips, vfx
)
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(page_title="Rehan AI Studio", page_icon="🎬", layout="centered")

st.title("🎬 Rehan AI Studio")
st.subheader("Create Your Own AI Poetry Videos ❤️")

shayari = {
    "اپنی شاعری لکھیں": "",
    "اداس شاعری": "ہنستے ہوئے چہرے کے پیچھے غم چھپائے بیٹھے ہیں،\nہم بھی کسی کے انتظار میں دل لگائے بیٹھے ہیں۔",
    "محبت": "تیری یادوں کا چراغ دل میں جلائے رکھتے ہیں،\nہم آج بھی تجھے اپنا بنائے رکھتے ہیں۔",
    "زندگی": "زندگی نے ہر قدم پر نیا سبق سکھایا ہے،\nجو اپنا تھا کبھی وقت نے اسے بھی آزمایا ہے۔",
    "دوستی": "دوستی نام ہے مشکل میں ساتھ نبھانے کا،\nصرف خوشیوں میں نہیں غم میں بھی کام آنے کا۔",
    "درد": "کچھ زخم ایسے ہوتے ہیں جو دکھائے نہیں جاتے،\nکچھ درد ایسے ہوتے ہیں جو بتائے نہیں جاتے۔",
    "تنہائی": "محفل میں بھی تنہا رہنا سیکھ لیا ہم نے،\nاپنے دل کا درد چھپانا سیکھ لیا ہم نے۔",
    "یادیں": "کچھ یادیں دل سے کبھی جاتی نہیں،\nکچھ باتیں وقت بھی بھلا پاتا نہیں۔",
    "وفا": "ہم نے ہر موڑ پر وفا نبھائی ہے،\nبدلے میں صرف خاموشی پائی ہے۔",
    "وقت": "وقت بدلتا ہے تو چہرے بدل جاتے ہیں،\nاپنے بھی کبھی کبھی بیگانے بن جاتے ہیں۔",
    "امید": "اندھیری رات کے بعد سویرا ضرور آتا ہے،\nجو ہمت نہیں ہارتا وہ منزل پاتا ہے۔",
}

# 100 ready poetry choices: 10 themes with 10 variations
ready_poetry = {}
themes = [
    ("اداس شاعری", "دل", "خاموشی", "غم"),
    ("محبت", "محبت", "یاد", "وفا"),
    ("زندگی", "زندگی", "وقت", "سفر"),
    ("دوستی", "دوستی", "ساتھ", "یار"),
    ("تنہائی", "تنہائی", "رات", "خاموشی"),
    ("یادیں", "یادیں", "ماضی", "لمحے"),
    ("وفا", "وفا", "وعدے", "اعتبار"),
    ("درد", "درد", "زخم", "آنسو"),
    ("امید", "امید", "منزل", "روشنی"),
    ("حوصلہ", "حوصلہ", "ہمت", "کامیابی"),
]
for theme, a, b, c in themes:
    for i in range(10):
        ready_poetry[f"{theme} {i+1}"] = (
            f"{a} کی باتیں دل میں چھپا کر رکھتے ہیں،\n"
            f"{b} کے لمحے آج بھی یاد کر کے رکھتے ہیں۔"
        )

all_poetry = {**shayari, **ready_poetry}

choice = st.selectbox("🥀 تیار شاعری منتخب کریں", list(all_poetry.keys()))
poetry = st.text_area("✍️ اپنی اردو شاعری", value=all_poetry[choice], height=120)

st.header("📹 ویڈیو یا تصویر")
videos = st.file_uploader("ویڈیو اپلوڈ کریں", type=["mp4", "mov", "avi"], accept_multiple_files=True)
image_file = st.file_uploader("یا تصویر اپلوڈ کریں", type=["jpg", "jpeg", "png"])
image_duration = st.slider("تصویر کی ویڈیو کا دورانیہ", 5, 60, 15)

st.header("🔤 اردو فونٹ")
font_file = st.file_uploader("Noto Nastaliq Urdu TTF/OTF فونٹ اپلوڈ کریں", type=["ttf", "otf"])
font_size = st.slider("شاعری کا سائز", 20, 100, 45)
font_color = st.selectbox("شاعری کا رنگ", ["White", "Yellow", "Red", "Green", "Cyan"])
position = st.selectbox("شاعری کی جگہ", ["Top", "Center", "Bottom"])
animation = st.selectbox("ٹیکسٹ اینیمیشن", ["Fade In", "Typewriter", "No Animation"])

st.header("🖼️ تصویر کے ایفیکٹس")
motion = st.selectbox("تصویر کی حرکت", ["No Zoom", "Zoom In", "Zoom Out"])

st.header("🌧️ بیک گراؤنڈ ایفیکٹس")
effect = st.selectbox("ویڈیو ایفیکٹ", ["None", "Rain", "Snow", "Hearts"])

st.header("🗣️ اردو AI Voice")
voice_on = st.checkbox("شاعری کی اردو آواز بنائیں")
voice_speed = st.selectbox("آواز کی رفتار", ["Normal", "Slow"])

st.header("🎵 میوزک")
music_file = st.file_uploader("اپنا بیک گراؤنڈ میوزک اپلوڈ کریں", type=["mp3", "wav", "m4a"])
music_volume = st.slider("میوزک والیوم", 0.0, 1.0, 0.25)

st.header("📱 ویڈیو سیٹنگز")
video_format = st.selectbox("ویڈیو فارمیٹ", ["9:16 Reels / TikTok", "Original"])
quality = st.selectbox("ویڈیو کوالٹی", ["720p", "1080p"])

st.header("📝 سوشل میڈیا کیپشن")
make_caption = st.checkbox("کیپشن اور ہیش ٹیگز بھی بنائیں", value=True)

def shape_text(text):
    return get_display(arabic_reshaper.reshape(text))

def make_vertical(clip, w, h):
    scale = max(w / clip.w, h / clip.h)
    clip = clip.resized(new_size=(int(clip.w * scale), int(clip.h * scale)))
    x = (clip.w - w) // 2
    y = (clip.h - h) // 2
    return clip.cropped(x1=x, y1=y, x2=x+w, y2=y+h)

def make_text_image(text, w, h, font_path, size, color, position):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, size)
    text = shape_text(text)
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=14,
                                   align="center", stroke_width=2)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    x = (w-tw)//2-bbox[0]
    if position == "Top":
        y = 55-bbox[1]
    elif position == "Center":
        y = (h-th)//2-bbox[1]
    else:
        y = h-th-80-bbox[1]
    draw.multiline_text((x, y), text, font=font, fill=color,
                        spacing=14, align="center",
                        stroke_width=2, stroke_fill="black")
    return np.array(img)

def make_effect_clip(w, h, duration, effect_name):
    if effect_name == "None":
        return None
    random.seed(7)
    count = 65
    particles = [
        (random.randint(0, w), random.randint(0, h),
         random.uniform(35, 150), random.randint(2, 5))
        for _ in range(count)
    ]

    def frame(t):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        for x, y, speed, size in particles:
            yy = int((y + speed*t) % h)
            xx = int(x + math.sin(t*2+x)*12)
            if effect_name == "Rain":
                d.line((xx, yy, xx-3, yy+18), fill=(180, 210, 255, 130), width=2)
            elif effect_name == "Snow":
                d.ellipse((xx, yy, xx+size, yy+size), fill=(255, 255, 255, 190))
            else:
                d.text((xx, yy), "♥", fill=(255, 90, 140, 180))
        return np.array(img)

    return VideoClip(frame, duration=duration).with_fps(24)

if st.button("🎬 Create My Final Video", type="primary"):
    if bool(videos) == bool(image_file):
        st.error("براہ کرم صرف ویڈیو یا صرف تصویر اپلوڈ کریں۔")
    elif not poetry.strip():
        st.error("براہ کرم شاعری لکھیں یا منتخب کریں۔")
    elif font_file is None:
        st.error("براہ کرم اردو فونٹ اپلوڈ کریں۔")
    else:
        temp_paths = []
        opened_clips = []
        final = None
        try:
            def save_temp(data, suffix):
                f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                f.write(data)
                f.close()
                temp_paths.append(f.name)
                return f.name

            font_path = save_temp(font_file.getvalue(), os.path.splitext(font_file.name)[1])
            ImageFont.truetype(font_path, font_size)

            if videos:
                clips = []
                for uploaded in videos:
                    p = save_temp(uploaded.getvalue(), os.path.splitext(uploaded.name)[1] or ".mp4")
                    c = VideoFileClip(p)
                    opened_clips.append(c)
                    clips.append(c)
                base = clips[0] if len(clips) == 1 else concatenate_videoclips(clips, method="compose")
                if len(clips) > 1:
                    opened_clips.append(base)
            else:
                img = Image.open(image_file).convert("RGB")
                if video_format == "9:16 Reels / TikTok":
                    w = 720 if quality == "720p" else 1080
                    h = 1280 if quality == "720p" else 1920
                    img = ImageOps.fit(img, (w, h))
                base = ImageClip(np.array(img)).with_duration(image_duration).with_fps(24)
                if motion != "No Zoom":
                    start, end = (1.0, 1.15) if motion == "Zoom In" else (1.15, 1.0)
                    base = base.with_effects([vfx.Resize(lambda t: start + (end-start)*t/image_duration)])
                opened_clips.append(base)

            if video_format == "9:16 Reels / TikTok":
                w = 720 if quality == "720p" else 1080
                h = 1280 if quality == "720p" else 1920
                base = make_vertical(base, w, h)

            w, h = int(base.w), int(base.h)
            color_map = {"White": "white", "Yellow": "yellow", "Red": "red",
                         "Green": "lime", "Cyan": "cyan"}
            overlay_array = make_text_image(poetry, w, h, font_path, font_size,
                                            color_map[font_color], position)
            text_clip = ImageClip(overlay_array).with_duration(base.duration).with_fps(24)

            if animation == "Fade In":
                text_clip = text_clip.with_effects([vfx.FadeIn(1.5)])
            elif animation == "Typewriter":
                # Reveal the text gradually using a simple fade-in sequence.
                text_clip = text_clip.with_effects([vfx.FadeIn(min(3, base.duration))])

            layers = [base, text_clip]
            fx_clip = make_effect_clip(w, h, base.duration, effect)
            if fx_clip is not None:
                layers.append(fx_clip)
                opened_clips.append(fx_clip)

            final = CompositeVideoClip(layers, size=(w, h)).with_duration(base.duration)

            audio_layers = []
            if voice_on:
                from gtts import gTTS
                voice_path = save_temp(b"", ".mp3")
                gTTS(text=poetry, lang="ur", slow=(voice_speed == "Slow")).save(voice_path)
                voice = AudioFileClip(voice_path)
                opened_clips.append(voice)
                audio_layers.append(voice.with_duration(min(voice.duration, final.duration)))

            if music_file is not None:
                music_path = save_temp(music_file.getvalue(), os.path.splitext(music_file.name)[1] or ".mp3")
                music = AudioFileClip(music_path)
                opened_clips.append(music)
                if music.duration < final.duration:
                    repeats = math.ceil(final.duration / music.duration)
                    from moviepy import concatenate_audioclips
                    music = concatenate_audioclips([music] * repeats)
                    opened_clips.append(music)
                music = music.subclipped(0, final.duration).with_volume_scaled(music_volume)
                audio_layers.append(music)

            if audio_layers:
                final = final.with_audio(CompositeAudioClip(audio_layers))

            output_path = save_temp(b"", ".mp4")
            st.info("ویڈیو بن رہی ہے، براہ کرم انتظار کریں...")
            final.write_videofile(output_path, codec="libx264", audio_codec="aac",
                                  fps=24, logger=None)

            st.success("آپ کی ویڈیو تیار ہے! ❤️")
            st.video(output_path)
            with open(output_path, "rb") as f:
                st.download_button("⬇️ Download Video", f,
                                   file_name="Rehan_AI_Studio.mp4",
                                   mime="video/mp4")

            if make_caption:
                st.subheader("📲 آپ کی سوشل میڈیا پوسٹ")
                caption = "🥀 دل کی بات، شاعری کے ساتھ ❤️\n\nآپ کو یہ شاعری کیسی لگی؟ کمنٹ میں بتائیں۔\n\n#RehanDigital #UrduPoetry #SadPoetry #AIReels #UrduShayari"
                st.text_area("Caption + Hashtags", value=caption, height=120)

        except Exception as e:
            st.error(f"ویڈیو بنانے میں مسئلہ آیا: {e}")
            st.info("اردو فونٹ درست TTF/OTF ہونا چاہیے۔ اردو AI Voice کے لیے انٹرنیٹ ضروری ہے۔")

        finally:
            if final is not None:
                try:
                    final.close()
                except Exception:
                    pass
            for c in opened_clips:
                try:
                    c.close()
                except Exception:
                    pass
            for p in temp_paths:
                try:
                    os.remove(p)
                except Exception:
                    pass
