import json
from pyrogram import Client, filters, idle
from pyrogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, CallbackQuery, BotCommand
from pyrogram.handlers import MessageHandler
import datetime
from pyromod import listen
from pyrogram import *
import asyncio
import logging


api_id = ""
api_hash = ""
bot_token = ""

bot_client = Client("bot_client", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
parser_client = Client("parser_client", api_id=api_id, api_hash=api_hash)

USER_DATA_FILE = "user_data.json"
id_collection = []

def load_user_data():
    try:
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_data(user_data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(user_data, f)

user_data = load_user_data()

main_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отслеживать канал')],
    [KeyboardButton(text='Добавить канал')],
    [KeyboardButton(text='Удалить канал')],
    [KeyboardButton(text='Список каналов')]
], resize_keyboard=True)


cache = {}

async def get_messages(client, channel, period):
    cache_key = (channel, period)
    if cache_key in cache:
        return cache[cache_key]

    messages = []
    today = datetime.date.today()
    this_week_start = today - datetime.timedelta(days=today.weekday())
    two_hours_ago = datetime.datetime.now() - datetime.timedelta(hours=2)
    one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)

    if period == '1':
        async for message in client.get_chat_history(chat_id=channel, limit=1000):
            if message.date.date() == today and message.date <= datetime.datetime.now():
                messages.append(message)
    elif period == '7':
        async for message in client.get_chat_history(chat_id=channel, limit=1700):
            if message.date.date() >= this_week_start and message.date.date() <= datetime.datetime.now().date():
                messages.append(message)
    elif period == '2h':
        async for message in client.get_chat_history(chat_id=channel, limit=800):
            if message.date >= two_hours_ago and message.date <= datetime.datetime.now():
                messages.append(message)
    elif period == '1h':
        async for message in client.get_chat_history(chat_id=channel, limit=800):
            if message.date >= one_hour_ago and message.date <= datetime.datetime.now():
                messages.append(message)

    cache[cache_key] = messages
    print(cache)

    return messages


async def send_messages(client, user_id, messages):
    lm = []
    for message in messages:
        try:
            if message.media_group_id is None:
                if message.video:
                    video = await message.download(in_memory=True)
                    await client.send_video(chat_id=user_id, video=video, caption=message.caption.html, caption_entities=message.caption_entities, parse_mode=enums.ParseMode.HTML)
                elif message.photo:
                    photo = await message.download(in_memory=True)
                    await client.send_photo(chat_id=user_id, photo=photo, caption=message.caption, caption_entities=message.caption_entities, parse_mode=enums.ParseMode.HTML)
                if message.video or message.photo is None:
                    await client.send_message(chat_id=user_id, text=message.text, entities=message.entities, parse_mode=enums.ParseMode.HTML)
                if message.animation:
                    animation = await message.download(in_memory=True)
                    await client.send_animation(chat_id=user_id, animation=animation)
            else:
                media_group = await client.get_media_group(chat_id=message.chat.id, message_id=message.id)
                for media in media_group:
                    if media.video:
                        _media = await client.download_media(media.video.file_id, in_memory=True, file_name=media.video.file_name)
                    elif media.audio:
                        _media = await client.download_media(media.audio.file_id, in_memory=True)
                    elif media.photo:
                        _media = await client.download_media(media.photo.file_id, in_memory=True)
                    elif media.document:
                        _media = await client.download_media(media.document.file_id, in_memory=True, file_name=media.document.file_name)
                    lm.append(_media)
                await client.send_media_group(chat_id=user_id, media=lm)
        except Exception as e:
            print(f'Errors: {e}')
    await client.send_message(chat_id=user_id, text="Все сообщения отправлены")


@bot_client.on_message(filters.command("start"))
async def command_start(client, message: Message):
    idf = str(message.from_user.id)
    if idf not in id_collection:
        id_collection.append(idf)
    print(id_collection)
    await message.reply('Welcome!', reply_markup=main_menu_keyboard)

@bot_client.on_message(filters.command("track_channel") | filters.regex(r"^Отслеживать канал$"))
async def track_channel(client, message: Message):
    if not user_data:
        await message.reply("У вас нет отслеживаемых каналов.")
        return
    channels = user_data
    inline_keyboard = [[InlineKeyboardButton(channel, callback_data=f"track#{channel}")] for channel in channels]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    await message.reply("Выберите канал для отслеживания", reply_markup=reply_markup)

@bot_client.on_callback_query(filters.regex(r"^track#"))
async def track_channel_callback(client, callback_query: CallbackQuery):
    data = callback_query.data
    user_id = str(callback_query.from_user.id)

    parts = data.split('#')
    channel = parts[1]

    print(f'{user_id} получен при запросе на {channel}')

    data_inline_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton('1 день', callback_data=f'1#day#{channel}')],
        [InlineKeyboardButton('1 неделя', callback_data=f"7#day#{channel}")],
        [InlineKeyboardButton('1 час', callback_data=f"1h#hour#{channel}")],
        [InlineKeyboardButton('2 часа', callback_data=f"2h#hour#{channel}")],
        [InlineKeyboardButton('Назад', callback_data="back")]
    ])
    await callback_query.message.reply("Выберите период для отслеживания", reply_markup=data_inline_keyboard)

@bot_client.on_callback_query(filters.regex(r"^1#day#(.+)$|^7#day#(.+)$|^1h#hour#(.+)$|^2h#hour#(.+)$"))
async def track_channel_period_callback(client, callback_query: CallbackQuery):
    user_id = str(callback_query.from_user.id)
    print(user_id)
    data = callback_query.data
    parts = data.split('#')
    channel = str(parts[2])
    period = str(parts[0])

    period_name = 0

    if period == "7":
        period_name = "неделю"
    if period == "1":
        period_name = "1 день"
    if period == "1h":
        period_name = "1 час"
    if period == "2h":
        period_name = "2 часа"


    await bot_client.send_message(user_id, f"Начинаю вывод сообщений из канала... {channel} за {period_name}")

    messages = await get_messages(parser_client, channel, period)

    await send_messages(bot_client, user_id, messages)



@bot_client.on_message(filters.command("add_channel") | filters.regex(r"^Добавить канал$"))
async def add_channel(client, message: Message):
    channel_input = await client.ask(message.chat.id, "Отлично! Пришлите имя канала в формате @channelname или URL канала в формате https://t.me/channelname")
    channel_input = channel_input.text.strip()

    if len(channel_input) < 64:
        if channel_input.startswith("@"):
            channel_name = channel_input
        elif channel_input.startswith("https://t.me/"):
            channel_name = "@" + channel_input.split("/")[-1]
        else:
            inline_keyboard = [[InlineKeyboardButton("Назад", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(inline_keyboard)
            await message.reply(f"Invalid input. Please make sure that the input is in the format @channelname or https://t.me/channelname.", reply_markup=reply_markup)
            return

        if channel_name in user_data:
            await message.reply(f"Channel {channel_name} is already in the list of channels.")
            return
        user_data[channel_name] = None
        save_user_data(user_data)

        await message.reply(f"Channel {channel_name} added.")
    else:
        await message.reply(f"Invalid channelname")

@bot_client.on_message(filters.command("remove_channel") | filters.regex(r"^Удалить канал$"))
async def remove_channel(client, message: Message):
    if not user_data:
        await message.reply("У вас нет отслеживаемых каналов.")
        return
    channels = user_data
    inline_keyboard = [[InlineKeyboardButton(channel, callback_data=f"remove#{channel}")] for channel in channels]
    inline_keyboard.append([InlineKeyboardButton("Назад", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    await message.reply("Выберите канал, который нужно удалить", reply_markup=reply_markup)

@bot_client.on_callback_query(filters.regex(r"^remove#"))
async def remove_channel_callback(client, callback_query: CallbackQuery):
    channel = callback_query.data.split("#")[1]
    user_id = str(callback_query.from_user.id)
    if channel not in user_data:
        await callback_query.message.edit_text("Канал больше не существует в базе данных.")
        return
    del user_data[channel]
    save_user_data(user_data)
    await callback_query.message.edit_text(f"Channel {channel} removed.")

@bot_client.on_callback_query(filters.regex("^back"))
async def back_command(client: Client, callback_query: CallbackQuery):
    await callback_query.message.reply("Вы вернулись в главное меню.")

@bot_client.on_message(filters.command("list_channel") | filters.regex(r"^Список каналов$"))
async def list_channels(_, message: Message):
    if not user_data:
        await message.reply("У вас нет отслеживаемых каналов.")
        return
    channels = user_data
    inline_keyboard = [[InlineKeyboardButton(channel, callback_data=channel)] for channel in channels]
    inline_keyboard.append([InlineKeyboardButton("Назад", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    await message.reply("Список каналов", reply_markup=reply_markup)

bot_client.add_handler(MessageHandler(command_start, filters.command(commands='start')))
bot_client.add_handler(MessageHandler(track_channel, filters.command(commands='track_channel')))
bot_client.add_handler(MessageHandler(add_channel, filters.command(commands='add_channel')))
bot_client.add_handler(MessageHandler(remove_channel, filters.command(commands='remove_channel')))
bot_client.add_handler(MessageHandler(list_channels, filters.command(commands='list_channels')))

bot_commands = [
    BotCommand(
        command='start',
        description='get started'
    ),
    BotCommand(
        command='track_channel',
        description='Pick channel for tracking'
    ),
    BotCommand(
        command='add_channel',
        description='Add channel to list for tracking'
    ),
    BotCommand(
        command='remove_channel',
        description='Remove channel from the list for tracking'
    ),
    BotCommand(
        command='list_channels',
        description='Show list for tracking'
    ),
]

bot_client.start()
parser_client.start()
bot_client.set_bot_commands(bot_commands)
idle()
