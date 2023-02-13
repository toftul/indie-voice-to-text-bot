import logging
import os
import pathlib
import time

import telegram
import whisper
from pydub import AudioSegment
from telegram import Update
from telegram.ext import MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, filters

from filter_allowed_chats import FilterAllowedChats

from config import TG_TOKEN, my_allowed_chat_ids

def create_project_folder():
    pathlib.Path(file_download_path).mkdir(exist_ok=True)


async def escape_markdown_chars(text: str) -> str:
    temporal = text
    for char in escaping_chars:
        temporal = temporal.replace(char, f"\\{char}")
    return temporal


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Дароу! Всем у кого нет тг премиума посвящается. Теперь я тут буду переводить голосовухи в текст."
    )


async def clean_up_files(ogg_file_path, mp3_file_path):
    os.remove(ogg_file_path)
    os.remove(mp3_file_path)


async def convert_ogg_to_mp3(ogg_file_path, mp3_file_path):
    given_audio = AudioSegment.from_file(ogg_file_path, format="ogg")
    given_audio.export(mp3_file_path, format="mp3")


async def set_typing_in_chat(context, effective_chat_id):
    await context.bot.send_chat_action(chat_id=effective_chat_id, action=telegram.constants.ChatAction.TYPING)


async def get_as_markdown(text, processing_time):
    transcription = text["text"].removeprefix(" ")
    language_ = text["language"]
#    markdown_message = '''\
#LANG: {language}
#TIME: {processing_time}s
#WORDS:
#```
#{transcription}
#```
#        '''.format(transcription=transcription, language=language_, processing_time=int(processing_time))
#    escaped_markdown_message = await escape_markdown_chars(markdown_message)
    markdown_message = '''
{transcription}
'''.format(transcription=transcription)
    escaped_markdown_message = await escape_markdown_chars(markdown_message)
    return escaped_markdown_message


async def download_voice_message(context, file_id, mp3_audio_path, ogg_audio_path):
    new_file = await context.bot.get_file(file_id)
    await new_file.download_to_drive(custom_path=ogg_audio_path)
    await convert_ogg_to_mp3(ogg_audio_path, mp3_audio_path)


async def transcribe_audio(mp3_audio_path):
    audio = whisper.load_audio(mp3_audio_path)
    result = model.transcribe(audio)
    return result


async def process_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat_id = update.effective_chat.id
    message_id = update.message.message_id
    file_unique_id = update.message.voice.file_unique_id
    file_id = update.message.voice.file_id
    ogg_audio_path = os.path.join(file_download_path, f"{file_unique_id}.ogg")
    mp3_audio_path = f"{ogg_audio_path}.mp3"

    try:
        start_time = time.time()
        logging.debug("Voice message received")
        await set_typing_in_chat(context, effective_chat_id)
        await download_voice_message(context, file_id, mp3_audio_path, ogg_audio_path)
        result = await transcribe_audio(mp3_audio_path)

        final_time = time.time()
        processing_time = (final_time - start_time)

        response_message = await get_as_markdown(result, processing_time)
        await context.bot.send_message(
            chat_id=effective_chat_id, text=response_message, reply_to_message_id=message_id,
            parse_mode=telegram.constants.ParseMode.MARKDOWN_V2
        )

    except Exception as e:
        error_message = f"Error converting video to audio. Exception={e}"
        await context.bot.send_message(chat_id=effective_chat_id, text=error_message, reply_to_message_id=message_id)
        pass
    finally:
        await clean_up_files(ogg_audio_path, mp3_audio_path)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

bot_token = TG_TOKEN #os.environ.get("TELEGRAM_BOT_TOKEN")
allowed_chat_ids = my_allowed_chat_ids #os.environ.get("ALLOWED_CHAT_IDS", default="").split(",")
file_download_path = "/tmp/whispering-for-chaos"
device = os.environ.get("WHISPER_DEVICE", default="cpu")
whisper_model = os.environ.get("WHISPER_MODEL", default="large")
escaping_chars = ['_', '*', '[', ']', '(', ')', '~', '>', '+', '-', '=', '|', '{', '}', '.', '!']
logging.info(f"configuration: device={device}, whisper_model={whisper_model} allowed_chat_ids={allowed_chat_ids}")
logging.info(f"Up to load whisper model, this might take a bit")
model = whisper.load_model(
    whisper_model, 
    #device=device
)
logging.info(f"Finished loading the whisper model")


create_project_folder()
application = ApplicationBuilder().token(bot_token).build()

start_handler = CommandHandler('start', start)
filter_allowed_chats = FilterAllowedChats(allowed_chat_ids)
audio_message_handler = MessageHandler(
    filter_allowed_chats,
    #filters.VOICE,
    process_voice_message
)

application.add_handler(start_handler)
application.add_handler(audio_message_handler)

application.run_polling()
