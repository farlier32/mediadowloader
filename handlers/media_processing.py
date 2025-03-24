import yt_dlp
import os
from typing import Tuple
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def sanitize_filename(filename: str) -> str:
    """Удаляет небезопасные символы из имени файла."""
    return re.sub(r'[<>:"/\\|?*]', '', filename)

async def download_media(url: str, output_path: str, is_audio: bool = False) -> Tuple[str, dict]:
    """Загружает медиафайл, возвращая путь к файлу и информацию о нем."""
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'noplaylist': True,
        'writethumbnail': False,
        'merge_output_format': 'mp4'  # Явное указание формата объединения
    }

    if is_audio:
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        })
    else:
        if "youtube.com" in url or "youtu.be" in url:
            ydl_opts.update({
                'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                'merge_output_format': 'mp4'
            })
        else:
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                'merge_output_format': 'mp4'
            })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        return filename, info
    except yt_dlp.DownloadError as e:
        logging.error(f"Ошибка загрузки {url}: {e}")
        raise  # Перебрасываем исключение, чтобы обработать его в обработчике
    except Exception as e:
        logging.exception(f"Неизвестная ошибка при загрузке {url}: {e}")
        raise

