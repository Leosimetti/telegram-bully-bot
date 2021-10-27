import asyncio
import logging
import os
import random
from dataclasses import dataclass, field
from datetime import datetime
from time import time
from typing import Optional, Union

import markovify
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType

import bloodbath

API_TOKEN: Optional[str] = os.getenv("BULLY_BOT_TOKEN")
NEAREST_ANIME_DATE = datetime(year=2021, month=10, day=30, hour=19)
ANIME_ROOM = 301

MODEL_REFRESH_SEC = 30.0
EMPTY_MODEL_DELAY_SEC = 1.0
MAX_CACHE_AGE_SEC = 60 * 60  # 1 hour

DEFAULT_SAMPLES = "\n".join(["бебра", "иди мойся", "воняешь", "попу мыл?"])
DEFAULT_STICKERS = [
    "CAACAgIAAxkBAAIHEmFpignJ7aloUf0eh" "_vekLFEUq2nAAIUAAP6U-sWktE_IbXY9aYhBA"
]

logging.basicConfig(level=logging.INFO)
bot: Bot = Bot(token=API_TOKEN)
dp: Dispatcher = Dispatcher(bot)

dir_to_txt: str = "Dialogs/"

generators_lock = asyncio.Lock()


@dataclass
class ModelInfo:
    model: markovify.NewlineText
    stickers: list[str]
    created: float = field(default_factory=lambda: time())
    has_new_msgs = False


model_cache: dict[str, ModelInfo] = {}


def refresh_generator(chat_id):
    global model_cache
    chat_id = str(chat_id)

    chat_path: str = f"{dir_to_txt}{chat_id}.txt"

    if os.path.exists(chat_path):
        with open(chat_path, encoding="utf8") as file:
            lines = file.read()
            if len(lines.splitlines()) >= 4:
                samples = lines
            else:
                samples = DEFAULT_SAMPLES
    else:
        samples = DEFAULT_SAMPLES

    generator: markovify.NewlineText = markovify.NewlineText(
        samples, state_size=1
    )
    generator.compile(inplace=True)

    chat_path: str = f"{dir_to_txt}{chat_id}_stickers.txt"

    if os.path.exists(chat_path):
        with open(chat_path, encoding="utf8") as file:
            stickers = file.read().splitlines()
            if len(stickers) <= 2:
                stickers = DEFAULT_STICKERS
    else:
        stickers = DEFAULT_STICKERS

    model_cache[chat_id] = ModelInfo(model=generator, stickers=stickers)


async def get_cached_model(chat_id) -> ModelInfo:
    chat_id = str(chat_id)
    global model_cache
    async with generators_lock:
        if chat_id not in model_cache:
            refresh_generator(chat_id)
        return model_cache[chat_id]


async def generators_refresh_task():
    global model_cache

    t = time() - MAX_CACHE_AGE_SEC
    print("Starting cacher")
    while True:
        # print("_before generators_lock")
        async with generators_lock:

            for chat_id in list(model_cache.keys()):
                m = model_cache[chat_id]
                if m.created < t:
                    model_cache.pop(chat_id)
                    continue

                if m.has_new_msgs:
                    print("refreshing the chats...")
                    refresh_generator(chat_id)

        # refresh_generator(chat_id)

        # print("_after generators_lock")

        await asyncio.sleep(MODEL_REFRESH_SEC)


async def generate_message(chat_id: Union[str, int]) -> str:
    global model_cache
    generator = (await get_cached_model(chat_id)).model

    while not (
        sentence := generator.make_sentence(
            tries=100, min_words=1, test_output=random.random() < 0.6
        )
    ):
        await asyncio.sleep(EMPTY_MODEL_DELAY_SEC)
        async with generators_lock:
            refresh_generator(chat_id)
        generator = (await get_cached_model(chat_id)).model

    # print("\n\n 🤡TEXT🤡 IS "+sentence+"\n\n")
    return sentence


async def generate_sticker(chat_id: Union[str, int]) -> str:
    global model_cache
    stickers = (await get_cached_model(chat_id)).stickers

    return random.choice(stickers)


async def get_time_to_anime(message, bypass=False):
    clean_message: str = bloodbath.sanitize(message.text)

    time_words = ["когда", "через", "сколько", "when"]
    anime_words = ["аниме", "онеме", "сходка", "сходочка", "anime"]
    msg = clean_message.lower()

    time_left = NEAREST_ANIME_DATE - datetime.now()
    if time_left.seconds > 0:
        has_anime = any(word in msg for word in anime_words)
        has_time = any(word in msg for word in time_words)
        has_gde = "где" in msg
        is_nice_message = has_anime and has_time
        is_place_message = has_gde and has_anime
        if is_place_message:
            await message.answer(f"Онеме будет в {ANIME_ROOM}")
        elif is_nice_message or bypass:

            times = (
                time_left.days,
                time_left.seconds // 3600,
                (time_left.seconds // 60) % 60,
                time_left.seconds % 60,
            )
            proper_times = zip(times, ["дней", "часов", "минут", "секунд"])
            answer = [
                f"{time[0]} {time[1]}" for time in proper_times if time[0] > 0
            ]
            await message.answer(
                f"До онеме сходОчки в {ANIME_ROOM} осталось {' '.join(answer)}"
            )
    else:
        await message.answer("Anime is no more...")
    return is_nice_message


@dp.message_handler(content_types=["new_chat_members"])
async def new_chat(message: types.Message) -> None:
    dialog_filename: str = f"{dir_to_txt}{message.chat.id}.txt"
    if not os.path.exists(dialog_filename):
        open(dialog_filename, "w").close()
    print("а кто")
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
    chat_id = message.chat.id

    await bot.delete_message(chat_id, message.message_id)
    await message.answer(
        await generate_message(chat_id), disable_web_page_preview=True
    )


@dp.message_handler(commands=["info"])
async def info(message: types.Message) -> None:
    chat_path: str = f"{dir_to_txt}{message.chat.id}.txt"
    with open(chat_path, encoding="utf8") as f:
        text_count = len(f.readlines())

    await message.answer(
        f"ID чата: {message.chat.id}\nсохранено {text_count} строк"
    )


@dp.message_handler(commands=["kogda"])
async def sxodka_time(message: types.message) -> None:
    chat_id = message.chat.id
    await bot.delete_message(chat_id, message.message_id)
    await get_time_to_anime(message, bypass=True)


@dp.message_handler(commands=["sticker"])
async def give_stick(message: types.message) -> None:
    chat_id = message.chat.id
    await bot.delete_message(chat_id, message.message_id)
    await message.answer_sticker(await generate_sticker(chat_id=chat_id))


async def allow_model_update(chat_id):
    async with generators_lock:
        if model := model_cache.get(str(chat_id)):
            model.has_new_msgs = True


@dp.message_handler(content_types=ContentType.STICKER)
async def send_stick(message: types.Message) -> None:
    chat_path = f"{dir_to_txt}{message.chat.id}_stickers.txt"
    file_id = message.sticker.file_id
    with open(chat_path, "a", encoding="utf8") as f:
        f.write(file_id + "\n")
    await allow_model_update(message.chat.id)

    is_reply = message.reply_to_message
    is_reply_to_bot = is_reply.from_user.is_bot if is_reply else False
    if random.randint(0, 3) == 0 or (is_reply_to_bot * random.randint(0, 1)):
        sticker = await generate_sticker(chat_id=message.chat.id)
        if is_reply_to_bot:
            await message.reply_sticker(sticker)
        else:
            await message.answer_sticker(sticker)


@dp.message_handler(content_types=ContentType.TEXT)
async def sov(message: types.Message) -> None:
    global model_cache
    clean_message: str = bloodbath.sanitize(message.text)
    chat_path = f"{dir_to_txt}{message.chat.id}.txt"

    if await get_time_to_anime(message):
        return

    if bloodbath.valid(clean_message):
        with open(chat_path, "a", encoding="utf8") as f:
            f.write(message.text + "\n")
        await allow_model_update(message.chat.id)

    is_reply = message.reply_to_message
    is_reply_to_bot = is_reply.from_user.is_bot if is_reply else False
    if random.randint(0, 5) == 0 or is_reply_to_bot:

        if random.randint(0, 4) == 0:
            random_stick = await generate_sticker(message.chat.id)
            await message.reply_sticker(random_stick)
        else:
            random_text = await generate_message(message.chat.id)
            await message.reply(random_text, disable_web_page_preview=True)


if __name__ == "__main__":
    if not os.path.exists("Dialogs/"):
        os.mkdir("Dialogs/")
    loop = asyncio.get_event_loop()

    cacher = loop.create_task(generators_refresh_task())

    executor.start_polling(dp, skip_updates=True, loop=loop)
