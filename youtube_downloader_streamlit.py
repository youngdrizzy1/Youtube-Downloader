import streamlit as st
from pytubefix import YouTube
from io import BytesIO
import time
import requests
from urllib.parse import parse_qs, urlparse

st.set_page_config(page_title="YouTube Downloader", page_icon="▶️")
st.title("YouTube Video Downloader")
st.markdown("---")

if "download_complete" not in st.session_state:
    st.session_state.download_complete = False
if "video_buffer" not in st.session_state:
    st.session_state.video_buffer = None

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.youtube.com/",
}

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats"""
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    
    parsed = urlparse(url)
    if parsed.netloc == "youtube.com" or parsed.netloc == "www.youtube.com":
        if parsed.path == "/watch":
            query = parse_qs(parsed.query)
            return query.get("v", [None])[0]
    return url.split("v=")[-1].split("&")[0]

url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=... or https://youtu.be/...")

if url:
    try:
        video_id = extract_video_id(url)
        clean_url = f"https://www.youtube.com/watch?v={video_id}"
        
        yt = YouTube(clean_url)
        
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
                
                stream_url = stream.url
                
                response = requests.get(stream_url, headers=HEADERS, stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                for chunk in response.iter_content(chunk_size=1024*1024): 
                    if chunk:
                        video_buffer.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress_percent = min(int((downloaded / total_size) * 100), 100)
                            progress_bar.progress(progress_percent)
                            status_text.text(f"Downloading... {progress_percent}%")
                
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

if st.session_state.get('download_complete', False) and st.session_state.get('video_buffer'):
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