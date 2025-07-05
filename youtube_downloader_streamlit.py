import streamlit as st
from pytubefix import YouTube
from io import BytesIO
import time

st.set_page_config(page_title="YouTube Downloader", page_icon="▶️")
st.title("YouTube Video Downloader")
st.markdown("---")

if "download_complete" not in st.session_state:
    st.session_state.download_complete = False
if "video_buffer" not in st.session_state:
    st.session_state.video_buffer = None

url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    try:
        yt = YouTube(url)
        
        with st.expander("Video Information", expanded=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(yt.thumbnail_url, width=200)
            with col2:
                st.subheader(yt.title)
                st.caption(f"Channel: {yt.author}")
                st.caption(f"Duration: {time.strftime('%H:%M:%S', time.gmtime(yt.length))}")
                st.caption(f"Views: {yt.views:,}")
        
        stream = yt.streams.filter(progressive=True, file_extension="mp4").get_highest_resolution()
        st.info(f"Selected quality: {stream.resolution} ({stream.filesize_mb:.1f} MB)")
        
        if st.button("Download Video"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                video_buffer = BytesIO()
                
                def progress_callback(stream, chunk, bytes_remaining):
                    progress = 1.0 - bytes_remaining / stream.filesize
                    progress_percent = progress * 100
                    progress_bar.progress(min(int(progress_percent), 100))
                    status_text.text(f"Downloading... {int(progress_percent)}%")
                
                yt.register_on_progress_callback(progress_callback)
                stream.stream_to_buffer(video_buffer)
                
                video_buffer.seek(0)
                st.session_state.video_buffer = video_buffer
                st.session_state.video_title = yt.title
                st.session_state.download_complete = True
                
                progress_bar.progress(100)
                status_text.text("Download complete!")
                st.success("✅ Video downloaded successfully!")
                
            except Exception as e:
                st.error(f"Error during download: {str(e)}")
                
    except Exception as e:
        st.error(f"Error: {str(e)}")

if st.session_state.download_complete and st.session_state.video_buffer:
    st.markdown("---")
    st.subheader("Download Your Video")
    video_title = st.session_state.video_title.replace(" ", "_").replace("/", "-")[:50] + ".mp4"
    
    st.download_button(
        label="Save Video to Device",
        data=st.session_state.video_buffer,
        file_name=video_title,
        mime="video/mp4"
    )
    
    if st.button("Clear Download"):
        st.session_state.download_complete = False
        st.session_state.video_buffer = None
        st.experimental_rerun()

st.markdown("---")
st.caption("Note: This tool downloads videos in the highest available MP4 format. "
           "Videos longer than 20 minutes might take longer to download.")