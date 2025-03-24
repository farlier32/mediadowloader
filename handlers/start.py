from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router

router = Router()


@router.message(Command("start"))
async def start_handler(msg: Message):

    await msg.answer('Привет')

