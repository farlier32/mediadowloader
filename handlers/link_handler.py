from aiogram import Router, F
from aiogram.types import Message, FSInputFile
import os
import logging
from .media_processing import download_media
from bot_instance import bot


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

router = Router()

# Фильтр для всех поддерживаемых ссылок
LINK_FILTER = F.text.regexp(
    r"(https?://(?:www\.)?(?:soundcloud\.com/[\w-]+/[\w-]+|youtube\.com/watch\?v=|youtu\.be/|tiktok\.com/.*?/video/|instagram\.com/reel/[\w-]+))"
)

@router.message(LINK_FILTER)
async def handle_media_links(msg: Message):
    """Обрабатывает ссылки на SoundCloud и YouTube."""
    url = msg.text
    output_path = "temp"

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    try:
        # Определяем тип контента и вызываем соответствующую функцию
        if "soundcloud.com" in url:
            await process_soundcloud(url, msg, output_path)
        elif "youtube.com" in url or "youtu.be" in url:
            await process_youtube(url, msg, output_path)
        elif "tiktok.com" in url:
            await process_tiktok(url, msg, output_path)
        elif "instagram.com/reel" in url:
            await process_instagram(url, msg, output_path)
        else:
            await msg.answer("⚠️ Ссылка не поддерживается.")

    except Exception as e:
        logging.exception(f"Ошибка при обработке {url}: {e}")
        await msg.answer(f"⚠️ Ошибка обработки: {str(e)}")

async def process_soundcloud(url: str, msg: Message, output_path: str):
    """Обрабатывает ссылки SoundCloud."""
    await msg.answer("🎧 Начинаю загрузку аудио...")
    try:
        filename, info = await download_media(url, output_path, is_audio=True)
        audio_path = filename.replace('.webm', '.mp3').replace('.m4a', '.mp3')
        await send_audio(msg, audio_path, info)
    except Exception as e:
        await msg.answer(f"❌ Ошибка загрузки SoundCloud: {str(e)}")

async def process_youtube(url: str, msg: Message, output_path: str):
    """Обрабатывает ссылки YouTube."""
    await msg.answer("⏬ Начинаю загрузку видео...")
    try:
        filename, info = await download_media(url, output_path)
        video_path = filename.replace('.webm', '.mp4')
        await send_video(msg, video_path, info)
    except Exception as e:
        await msg.answer(f"❌ Ошибка загрузки YouTube: {str(e)}")

async def process_tiktok(url: str, msg: Message, output_path: str):
    """Обрабатывает ссылки TikTok."""
    await msg.answer("🎵 Начинаю загрузку TikTok...")
    try:
        filename, info = await download_media(url, output_path)
        video_path = filename.replace('.webm', '.mp4')
        await send_video(msg, video_path, info)
    except Exception as e:
        await msg.answer(f"❌ Ошибка загрузки TikTok: {str(e)}")

async def process_instagram(url: str, msg: Message, output_path: str):
    """Обрабатывает ссылки Instagram Reels."""
    await msg.answer("📸 Начинаю загрузку Instagram Reels...")
    try:
        filename, info = await download_media(url, output_path)
        video_path = filename.replace('.webm', '.mp4')
        await send_video(msg, video_path, info)
    except Exception as e:
        await msg.answer(f"❌ Ошибка загрузки Instagram: {str(e)}")


async def send_audio(msg: Message, path: str, info: dict):
    """Отправляет аудиофайл в Telegram."""
    if not os.path.exists(path):
        await msg.answer("❌ Файл не найден")
        return

    file_size = os.path.getsize(path)
    if file_size > 50 * 1024 * 1024:
        await msg.answer("❌ Файл превышает 50 МБ")
        os.remove(path)
        return

    try:
        await msg.answer(f"✅ {info['title']}")
        await bot.send_audio(
            chat_id=msg.chat.id,
            audio=FSInputFile(path),
            title=info['title'][:64],
            performer=info.get('uploader', 'Unknown Artist')[:64]
        )
    except Exception as e:
        await msg.answer(f"❌ Ошибка при отправке аудио: {str(e)}")
    finally:
        if os.path.exists(path):
            os.remove(path)

async def send_video(msg: Message, path: str, info: dict):
    """Отправляет видеофайл в Telegram."""
    if not os.path.exists(path):
        await msg.answer("❌ Файл не найден")
        return

    file_size = os.path.getsize(path)
    if file_size > 50 * 1024 * 1024:
        await msg.answer("❌ Видео превышает 50 МБ")
        os.remove(path)
        return

    try:
        duration = int(info.get('duration', 0))

        await msg.answer(f"✅ {info['title']}")
        await bot.send_video(
            chat_id=msg.chat.id,
            video=FSInputFile(path),
            duration=duration,
        )
    except Exception as e:
        await msg.answer(f"❌ Ошибка при отправке видео: {str(e)}")
    finally:
        try:
            if os.path.exists(path):
                os.remove(path)
                logging.info(f"Файл {path} успешно удален")

        except OSError as e:
            logging.error(f"Не удалось удалить файл {path}: {e}")