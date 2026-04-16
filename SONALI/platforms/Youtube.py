import asyncio
import os
import re
from typing import Union

import aiohttp
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

# Use the appropriate utility import based on your project structure
# Change to BrandrdXMusic.utils.formatters if needed
from SONALI.utils.formatters import time_to_seconds 
from SONALI import LOGGER

try:
    from py_yt import VideosSearch
except ImportError:
    from youtubesearchpython.__future__ import VideosSearch

API_URL = "https://shrutibots.site"
cookies_file = "SONALI/assets/cookies.txt"

async def download_song(link: str) -> str:
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
    if not video_id or len(video_id) < 3:
        return None

    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")

    if os.path.exists(file_path):
        return file_path

    try:
        async with aiohttp.ClientSession() as session:
            params = {"url": video_id, "type": "audio"}
            async with session.get(f"{API_URL}/download", params=params, timeout=aiohttp.ClientTimeout(total=7)) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                download_token = data.get("download_token")
                if not download_token:
                    return None
                
                stream_url = f"{API_URL}/stream/{video_id}?type=audio&token={download_token}"
                async with session.get(stream_url, timeout=aiohttp.ClientTimeout(total=300)) as file_response:
                    target_resp = file_response
                    if file_response.status == 302:
                        redirect_url = file_response.headers.get('Location')
                        target_resp = await session.get(redirect_url)
                    
                    if target_resp.status == 200:
                        with open(file_path, "wb") as f:
                            async for chunk in target_resp.content.iter_chunked(16384):
                                f.write(chunk)
                        return file_path if os.path.getsize(file_path) > 0 else None
    except Exception as e:
        LOGGER.error(f"Download Song Error: {e}")
        if os.path.exists(file_path): os.remove(file_path)
    return None

async def download_video(link: str) -> str:
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
    if not video_id or len(video_id) < 3:
        return None

    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")

    if os.path.exists(file_path):
        return file_path

    try:
        async with aiohttp.ClientSession() as session:
            params = {"url": video_id, "type": "video"}
            async with session.get(f"{API_URL}/download", params=params, timeout=aiohttp.ClientTimeout(total=7)) as response:
                if response.status != 200: return None
                data = await response.json()
                token = data.get("download_token")
                if not token: return None
                
                stream_url = f"{API_URL}/stream/{video_id}?type=video&token={token}"
                async with session.get(stream_url, timeout=aiohttp.ClientTimeout(total=600)) as file_response:
                    target_resp = file_response
                    if file_response.status == 302:
                        redirect_url = file_response.headers.get('Location')
                        target_resp = await session.get(redirect_url)
                    
                    if target_resp.status == 200:
                        with open(file_path, "wb") as f:
                            async for chunk in target_resp.content.iter_chunked(16384):
                                f.write(chunk)
                        return file_path if os.path.getsize(file_path) > 0 else None
    except Exception as e:
        LOGGER.error(f"Download Video Error: {e}")
        if os.path.exists(file_path): os.remove(file_path)
    return None

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz and "unavailable videos are hidden" not in (errorz.decode("utf-8")).lower():
        return errorz.decode("utf-8")
    return out.decode("utf-8")

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset: entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        res = (await results.next())["result"][0]
        duration_sec = int(time_to_seconds(res["duration"])) if res["duration"] else 0
        return res["title"], res["duration"], duration_sec, res["thumbnails"][0]["url"].split("?")[0], res["id"]

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        results = VideosSearch(link, limit=1)
        return (await results.next())["result"][0]["title"]

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        results = VideosSearch(link, limit=1)
        return (await results.next())["result"][0]["duration"]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        results = VideosSearch(link, limit=1)
        return (await results.next())["result"][0]["thumbnails"][0]["url"].split("?")[0]

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        file = await download_video(link)
        return (1, file) if file else (0, "Download failed")

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid: link = self.listbase + link
        if "&" in link: link = link.split("&")[0]
        playlist = await shell_cmd(f"yt-dlp --cookies {cookies_file} -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}")
        return [k for k in playlist.split("\n") if k]

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        results = VideosSearch(link, limit=1)
        res = (await results.next())["result"][0]
        track_details = {
            "title": res["title"], "link": res["link"], "vidid": res["id"],
            "duration_min": res["duration"], "thumb": res["thumbnails"][0]["url"].split("?")[0],
        }
        return track_details, res["id"]

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        ydl_opts = {"quiet": True, "cookiefile": cookies_file}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for f in r["formats"]:
                if "dash" not in str(f.get("format", "")).lower():
                    formats_available.append({
                        "format": f.get("format"), "filesize": f.get("filesize"),
                        "format_id": f.get("format_id"), "ext": f.get("ext"),
                        "format_note": f.get("format_note"), "yturl": link,
                    })
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        a = VideosSearch(link, limit=10)
        res = (await a.next()).get("result")[query_type]
        return res["title"], res["duration"], res["thumbnails"][0]["url"].split("?")[0], res["id"]

    async def download(self, link: str, mystic, video: Union[bool, str] = None, videoid: Union[bool, str] = None, **kwargs) -> str:
        if videoid: link = self.base + link
        file = await download_video(link) if video else await download_song(link)
        return (file, True) if file else (None, False)
