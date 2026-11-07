
import streamlit as st
import tempfile
import math
from moviepy import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    concatenate_audioclips
)

st.set_page_config(page_title="Rehan Digital AI Studio")

st.title("🎬 Rehan Digital AI Studio")
st.subheader("Your Personal Video Editing Studio ❤️")

st.header("✂️ Video Merger")

videos = st.file_uploader(
    "Select Your Videos",
    type=["mp4", "mov", "avi"],
    accept_multiple_files=True
)

st.header("🎵 Add Background Music")

music = st.file_uploader(
    "Select MP3 Music",
    type=["mp3", "wav", "m4a"]
)

volume = st.slider("Music Volume", 0.0, 1.0, 0.3)

if st.button("🎬 Create Final Video"):
    if not videos or len(videos) < 2:
        st.warning("Please select at least 2 videos.")
    else:
        clips = []
        music_clip = None
        final = None
        temp_files = []

        try:
            for video in videos:
                temp = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".mp4"
                )
                temp.write(video.getvalue())
                temp.close()
                temp_files.append(temp.name)
                clips.append(VideoFileClip(temp.name))

            final = concatenate_videoclips(
                clips, method="compose"
            )

            if music is not None:
                audio_temp = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".mp3"
                )
                audio_temp.write(music.getvalue())
                audio_temp.close()
                temp_files.append(audio_temp.name)

                music_clip = AudioFileClip(audio_temp.name)

                if music_clip.duration < final.duration:
                    count = math.ceil(
                        final.duration / music_clip.duration
                    )
                    music_clip = concatenate_audioclips(
                        [music_clip] * count
                    )

                music_clip = music_clip.subclipped(
                    0, final.duration
                ).with_volume_scaled(volume)

                final = final.with_audio(music_clip)

            output = "Rehan_Final_Video.mp4"

            final.write_videofile(
                output,
                codec="libx264",
                audio_codec="aac"
            )

            st.success("Your Video Is Ready! ❤️")
            st.video(output)

            with open(output, "rb") as f:
                st.download_button(
                    "⬇️ Download Final Video",
                    f,
                    file_name=output,
                    mime="video/mp4"
                )

        except Exception as e:
            st.error(f"Error: {e}")

        finally:
            if final:
                final.close()
            if music_clip:
                music_clip.close()
            for clip in clips:
                clip.close()
            for path in temp_files:
                import os
                try:
                    os.remove(path)
                except OSError:
                    pass
