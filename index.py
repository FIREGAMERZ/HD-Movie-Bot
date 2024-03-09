import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bs4 import BeautifulSoup
import requests

# Your Telegramlink.in API key
TELEGRAMLINK_API_KEY = "7de232fc833c68108d353b812ac49ef95b45c986"
# Your Telegram bot token
TELEGRAM_BOT_TOKEN = "7139621410:AAEWNXk8JQFmQTpSbNBbUZ7gl9Zk45qIkgo"

def scrape_mkvcinemas(movie_name):
    url = f"https://mkvcinemas.rsvp/{movie_name.replace(' ', '-')}-full-movie-download-in-hd/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        download_links = [a['href'] for a in soup.find_all('a', href=True) if a.text == 'Download From Server']
        if download_links:
            return download_links[0]  # Return only the first download link found
    return None

def shorten_link(long_url):
    # Call Telegramlink.in API to shorten the URL
    response = requests.post("https://telegramlink.in/api/shorten",
                             data={"key": TELEGRAMLINK_API_KEY, "url": long_url})
    if response.status_code == 200:
        return response.json()["shortenedUrl"]
    else:
        return None

def start(update, context):
    update.message.reply_text("Welcome to the Movie Bot! Send me a movie name and I'll find the download link for you.")

def movie_handler(update, context):
    movie_name = update.message.text
    
    # Scrape mkvcinemas.rsvp for the movie download link
    download_link = scrape_mkvcinemas(movie_name)
    
    if download_link:
        # Shorten the download link
        short_link = shorten_link(download_link)
        if short_link:
            update.message.reply_text(f"Here's the download link for '{movie_name}': {short_link}")
        else:
            update.message.reply_text("Sorry, I couldn't generate the download link at the moment. Please try again later.")
    else:
        update.message.reply_text("Sorry, I couldn't find any information about this movie on mkvcinemas.rsvp.")

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, movie_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
