import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup
from morphy import morph
from tts import Tts


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
reply_keyboard = [['/help', '/text_to_speach'],
                      ['/find_information_about_word']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
current_func = 'dialog'
lang = 'en-ru'


async def start(update, context):
    await update.message.reply_text(
        "Чем могу помочь?",
        reply_markup=markup
    )

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


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("find_information_about_word", morphology))
    application.add_handler(CommandHandler("text_to_speach", tts))
    application.add_handler(CommandHandler("start", start))
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, dialog)
    application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
