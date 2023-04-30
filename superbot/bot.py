
import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup
from translation import trns
from morphy import morph
from tts import Tts


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
reply_keyboard = [['/translate en-ru', '/donation'],
                      ['/morphology', '/tts']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
current_func = 'dialog'
lang = 'en-ru'


async def start(update, context):
    await update.message.reply_text(
        "Чем могу помочь?",
        reply_markup=markup
    )


async def translation_downloader(update, context):
    global current_func
    file = await context.bot.get_file(update.message.document)
    await file.download_to_drive('data/trans.txt')
    await update.message.reply_text('С какого языка перевести? (в формате en-ru)')
    current_func = 'translation-1'


def echo(update, context):
    return update.message.text


async def help_command(update, context):
    await update.message.reply_text(
        "Я бот, который поможет с языками")


async def tts(update, context):
    global current_func
    current_func = 'text_to_speach'
    await update.message.reply_text(
        "Впиши сначала язык, а после запрос.\n Образец - 'ru, Привет!'\n"
        "Доступные языки:\nzh-TW\tКитайский\nen\tАнглийский\nru\tРусский"
        "\nfr\tФранцузский\nes\tИспанский\npt\tПортугальский\nuk\tУкраинский")


async def tr_file_or_text(update, context):
    global current_func, lang
    lang = context.args[0]
    await update.effective_message.reply_text('Введите то, что надо перевести (или пришлите файл)')
    current_func = 'text_translater'


async def morphology(update, context):
    global current_func
    current_func = 'find_information_about_word'
    await update.message.reply_text("введите слово")


async def dialog(update, context):
    global current_func, lang
    print(current_func, lang)
    if current_func == 'dialog':
        print(update.message.text)
        await update.message.reply_text(update.message.text)
    elif current_func == 'text_to_speach':
        chat_id = update.effective_message.chat_id
        print('text_to_speach:', update.message.text)
        Tts.text_to_speech(update.message.text[0] + update.message.text[1],
                           update.message.text[3:len(update.message.text) + 1])
        await context.bot.send_audio(chat_id=chat_id, audio=open('audio.mp3', 'rb'))
        current_func = 'dialog'
    elif current_func == 'find_information_about_word':
        print('mp:', update.message.text)
        await update.message.reply_text(morph(update.message.text))
        current_func = 'dialog'
    elif current_func == 'text_translater':
        print("tr:", update.message.text)
        await update.message.reply_text(trns(update.message.text, lang))
        current_func = 'dialog'
    elif current_func == 'translation-1':
        chat_id = update.effective_message.chat_id
        lang = update.message.text
        await update.message.reply_text('подождите немного, переводится')
        file = trns(lang, file=True)
        with open(file, 'r') as f:
            await context.bot.send_document(chat_id=chat_id, document=f)
        current_func = 'dialog'


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("find_information_about_word", morphology))
    application.add_handler(CommandHandler("text_to_speach", tts))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("text_translater", tr_file_or_text))
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, dialog)
    application.add_handler(MessageHandler(filters.Document.ALL, translation_downloader))
    application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
