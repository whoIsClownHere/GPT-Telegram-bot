# Импортируем необходимые классы.
import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup
from translation import trns
from morphy import morph
from tts import Tts

# Запускаем логгирование
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
# Определяем функцию-обработчик сообщений.
# У неё два параметра, updater, принявший сообщение и контекст - дополнительная информация о сообщении.


def echo(update, context):
    return update.message.text


async def help_command(update, context):
    await update.message.reply_text(
        "Я бот справочник")


async def tts(update, context):
    global current_func
    current_func = 'tts'
    await update.message.reply_text(
        "Впиши сначала язык, а после запрос.\n Образец - 'ru, Привет!'\n"
        "Доступные языки:\nzh-TW\tКитайский\nen\tАнглийский\nru\tРусский"
        "\nfr\tФранцузский\nes\tИспанский\npt\tПортугальский\nuk\tУкраинский")


async def translate(update, context):
    global current_func, lang
    lang = context.args[0]
    await update.effective_message.reply_text('что перевести (введите или добавьте файл)?')
    current_func = 'translation'

async def morphology(update, context):
    global current_func
    current_func = 'morphology'
    await update.message.reply_text("введите слово")


async def donation(update, context):
    await update.message.reply_text("шутка, донатов нет")


async def downloader(update, context):
    global current_func
    file = await context.bot.get_file(update.message.document)
    await file.download_to_drive('data/trans.txt')
    await update.message.reply_text('какие языки использовать? (в формате en-ru)')
    current_func = 'translation-1'



async def dialog(update, context): #заменить на болталку из прошлого бота
    global current_func, lang
    print(current_func, lang)
    if current_func == 'dialog':
        print(update.message.text)
        await update.message.reply_text(update.message.text)
    elif current_func == 'tts':
        chat_id = update.effective_message.chat_id
        print('tts:', update.message.text)
        Tts.text_to_speech(update.message.text[0] + update.message.text[1],
                            update.message.text[3:len(update.message.text) + 1])
        await context.bot.send_audio(chat_id=chat_id, audio=open('audio.mp3', 'rb'))
        current_func = 'dialog'
    elif current_func == 'morphology':
        print('mp:', update.message.text)
        await update.message.reply_text(morph(update.message.text))
        current_func = 'dialog'
    elif current_func == 'translation':
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
    application.add_handler(CommandHandler("morphology", morphology))
    application.add_handler(CommandHandler("donation", donation))
    application.add_handler(CommandHandler("translate", translate))
    application.add_handler(CommandHandler("tts", tts))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, dialog)
    application.add_handler(MessageHandler(filters.Document.ALL, downloader))
    application.add_handler(text_handler)  # Регистрируем обработчик в приложении.
    application.run_polling()
main()
