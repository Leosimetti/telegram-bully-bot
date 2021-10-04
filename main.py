import logging
from aiogram import Bot, Dispatcher, executor, types
import os
import random
import mc


API_TOKEN = os.getenv("BULLY_BOT_TOKEN") 

# logs
logging.basicConfig(level=logging.INFO)

# initialization
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

dir_to_txt = "Dialogs/"

@dp.message_handler(content_types=["new_chat_members"])
async def new_chat(message: types.Message):
	dialog_filename = f"{dir_to_txt}{message.chat.id}.txt"

	if not os.path.exists(dialog_filename):
		open(dialog_filename, "w").close()
	for user in message.new_chat_members:
		if user.id == bot.id:
			await message.answer(f"ТОЛЯ, сделай меня админом!!!!!")


@dp.message_handler(commands=['start'], chat_type=types.ChatType.PRIVATE)
async def start(message: types.Message):
	await message.answer(f'Иди найхуй пидор.')


@dp.message_handler(commands=['help'])
async def react(message: types.Message):
	await message.answer('Мои команды:\n/gen - сгенерировать фразу\n/info - данные о базе')

@dp.message_handler(commands=['gen'])
async def gen(message: types.Message):
	await bot.delete_message(message.chat.id, message.message_id )
	chat_path = f"{dir_to_txt}{message.chat.id}.txt"
	with open(chat_path, encoding="utf8") as f:
		text_lines = len(f.readlines())

	if text_lines >= 4:
		with open(chat_path, encoding="utf8") as file:
			texts = file.read().splitlines()
		# Выбираем рандомный текст
		generator = mc.StringGenerator(samples=texts)
		random_text = generator.generate_string(attempts=100, validator=mc.util.combine_validators(mc.validators.words_count(minimal=1, maximal=200)))
		try:
			await message.answer(random_text.lower())
		except:
			pass

@dp.message_handler(commands=['info'])
async def info(message: types.Message):
	chat_path = f"{dir_to_txt}{message.chat.id}.txt"
	with open(chat_path, encoding="utf8") as f:
		text_count = len(f.readlines())

	await message.answer(
		f"ID чата: {message.chat.id}\nсохранено {text_count} строк")

@dp.message_handler(content_types=['text'])
async def sov(message: types.Message):
	text_length = len(message.text)
	chat_path = f"{dir_to_txt}{message.chat.id}.txt"
	if message.text in [
		"/gen",
		"/start",
		"/help",
		"/info"

	]:
		return
	if (
		message.text.startswith("http://")
		or message.text.startswith("https://")
		or message.text.startswith("/")
	):
		return
		
	if 0 < text_length <= 500:
		with open(chat_path, "a", encoding="utf8") as f:
			f.write(message.text + "\n")

	with open(chat_path, encoding="utf8") as f:
		text_lines = len(f.readlines())
		
	is_reply = message.reply_to_message
	if is_reply:
		is_reply_to_bot = is_reply.from_user.is_bot
	else:
		is_reply_to_bot = None
		
	rnd = random.randint(0,6)
	if rnd == 0 or is_reply_to_bot:
		if text_lines >= 4:
			with open(chat_path, encoding="utf8") as file:
				texts = file.read().splitlines()
			# Выбираем рандомный текст
			generator = mc.StringGenerator(samples=texts)
			random_text = generator.generate_string(attempts=100, validator=mc.util.combine_validators(mc.validators.words_count(minimal=1, maximal=100)))
			try:
				await message.reply(random_text)#.lower())
			except:
				pass

if __name__ == "__main__":
	if not os.path.exists("Dialogs/"):
		os.mkdir("Dialogs/")
	executor.start_polling(dp, skip_updates=True)
