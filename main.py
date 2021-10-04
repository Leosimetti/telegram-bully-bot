import logging
import os
import random
from typing import Optional

import mc
from aiogram import Bot, Dispatcher, executor, types

import bloodbath

API_TOKEN: Optional[str] = os.getenv("BULLY_BOT_TOKEN")


logging.basicConfig(level=logging.INFO)
bot: Bot = Bot(token=API_TOKEN)
dp: Dispatcher = Dispatcher(bot)

dir_to_txt: str = "Dialogs/"


@dp.message_handler(content_types=["new_chat_members"])
async def new_chat(message: types.Message) -> None:
    dialog_filename: str = f"{dir_to_txt}{message.chat.id}.txt"
    if not os.path.exists(dialog_filename):
        open(dialog_filename, "w").close()
    for user in message.new_chat_members:
        if user.id == bot.id:
            await message.answer("ТОЛЯ, сделай меня админом!!!!!")


@dp.message_handler(commands=["start"], chat_type=types.ChatType.PRIVATE)
async def start(message: types.Message) -> None:
    await message.answer("Иди найхуй пидор.")


@dp.message_handler(commands=["help"])
async def react(message: types.Message) -> None:
    await message.answer(
        "Мои команды:\n/gen - сгенерировать фразу\n/info - данные о базе"
    )


@dp.message_handler(commands=["gen"])
async def gen(message: types.Message) -> None:
    await bot.delete_message(message.chat.id, message.message_id)
    chat_path: str = f"{dir_to_txt}{message.chat.id}.txt"
    with open(chat_path, encoding="utf8") as f:
        lines = f.readlines()
        if len(lines) >= 4:
            # Выбираем рандомный текст
            generator: mc.StringGenerator = mc.StringGenerator(samples=lines)
            random_text: str = generator.generate_string(
                attempts=100,
                validator=mc.util.combine_validators(
                    mc.validators.words_count(minimal=1, maximal=200)
                ),
            )
            await message.answer(random_text)


@dp.message_handler(commands=["info"])
async def info(message: types.Message) -> None:
    chat_path: str = f"{dir_to_txt}{message.chat.id}.txt"
    with open(chat_path, encoding="utf8") as f:
        text_count = len(f.readlines())

    await message.answer(
        f"ID чата: {message.chat.id}\nсохранено {text_count} строк"
    )


@dp.message_handler(content_types=["text"])
async def sov(message: types.Message) -> None:
    clean_message: str = bloodbath.sanitize(message.text)
    chat_path = f"{dir_to_txt}{message.chat.id}.txt"

    if bloodbath.valid(clean_message):
        with open(chat_path, "a", encoding="utf8") as f:
            f.write(message.text + "\n")

    is_reply = message.reply_to_message
    is_reply_to_bot = is_reply.from_user.is_bot if is_reply else False
    if random.randint(0, 6) == 0 or is_reply_to_bot:
        with open(chat_path, encoding="utf8") as file:
            lines = file.readlines()
            if len(lines) >= 4:
                samples = lines
            else:
                samples = ["бебра", "иди мойся", "воняешь", "попу мыл?"]
        # Выбираем рандомный текст
        generator = mc.StringGenerator(samples=samples)
        random_text = generator.generate_string(
            attempts=100,
            validator=mc.util.combine_validators(
                mc.validators.words_count(minimal=1, maximal=100)
            ),
        )
        await message.reply(random_text)


if __name__ == "__main__":
    if not os.path.exists("Dialogs/"):
        os.mkdir("Dialogs/")
    executor.start_polling(dp, skip_updates=True)
