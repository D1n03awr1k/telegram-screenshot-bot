import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import validators

# Получаем токен из переменных окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Функция для создания скриншота
def take_screenshot(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Без GUI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")  # Разрешение 1920x1080

    driver = webdriver.Chrome(options=chrome_options)
    try:
        # Добавляем http://, если его нет
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        driver.get(url)
        driver.save_screenshot("screenshot.png")
        return "screenshot.png"
    except Exception as e:
        return str(e)
    finally:
        driver.quit()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли мне домен (например, example.com) или IPv4, и я сделаю скриншот сайта в формате 1920x1080."
    )

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Проверка, является ли текст валидным доменом или IPv4
    if validators.domain(text) or validators.ipv4(text):
        await update.message.reply_text("Делаю скриншот, подожди немного...")
        screenshot_path = take_screenshot(text)
        
        if os.path.exists(screenshot_path):
            with open(screenshot_path, 'rb') as photo:
                await update.message.reply_photo(photo=photo)
            os.remove(screenshot_path)  # Удаляем файл после отправки
        else:
            await update.message.reply_text(f"Ошибка: {screenshot_path}")
    else:
        await update.message.reply_text("Пожалуйста, пришли валидный домен (например, example.com) или IPv4.")

# Главная функция
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
