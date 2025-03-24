# import glob

# def clear_thumbnail_files(directory: str):
#     """Удаляет все файлы .png, .webp и .jpg из указанной директории."""
#     for ext in ('.png', '.webp', '.jpg'):
#         files = glob.glob(os.path.join(directory, f'*{ext}'))
#         for file in files:
#             try:
#                 os.remove(file)
#                 logging.info(f"Удален файл: {file}")
#             except OSError as e:
#                 logging.error(f"Ошибка при удалении файла {file}: {e}")