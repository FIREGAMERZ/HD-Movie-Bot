import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import requests
from bs4 import BeautifulSoup

TOKEN = "7139621410:AAEWNXk8JQFmQTpSbNBbUZ7gl9Zk45qIkgo"
app = Flask(__name__)
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

url_list = {}
api_key = "44a1bfad3948393badd4d5e4e7ec9b81f39282af"

def search_movies(query):
    movies_list = []
    website = BeautifulSoup(requests.get(f"https://mkvcinemas.skin/?s={query.replace(' ', '+')}").text, "html.parser")
    movies = website.find_all("a", {'class': 'ml-mask jt'})
    for movie in movies:
        if movie:
            title = movie.find("span", {'class': 'mli-info'}).text
            movies_list.append(title)
            url_list[title] = movie['href']
    return movies_list

def get_movie(query):
    movie_details = {}
    movie_page_link = BeautifulSoup(requests.get(f"{url_list[query]}").text, "html.parser")
    if movie_page_link:
        title = movie_page_link.find("div", {'class': 'mvic-desc'}).h3.text
        movie_details["title"] = title
        links = movie_page_link.find_all("a", {'rel': 'noopener', 'data-wpel-link': 'internal'})
        final_links = {}
        for i in links:
            url = f"https://urlshortx.com/api?api={api_key}&url={i['href']}"
            response = requests.get(url)
            if response.status_code == 200:
                link = response.json()
                final_links[f"{i.text}"] = link['shortenedUrl']
        movie_details["links"] = final_links
    return movie_details

def welcome(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f"Hello {update.message.from_user.first_name}, Welcome to SB Movies.\n"
                              f"🔥 Download Your Favourite Movies For 💯 Free And 🍿 Enjoy it.")
    update.message.reply_text("👇 Enter Movie Name 👇")

def find_movie(update: Update, context: CallbackContext) -> None:
    query = update.message.text
    movies_list = search_movies(query)
    if movies_list:
        reply_markup = InlineKeyboardMarkup.from_column(
            [[InlineKeyboardButton(title, callback_data=title)] for title in movies_list])
        update.message.reply_text('Search Results...', reply_markup=reply_markup)
    else:
        update.message.reply_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')

def movie_result(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    s = get_movie(query.data)
    caption = f"🎥 {s['title']}\n\n"
    for title, link in s["links"].items():
        caption += f"🎬 {title}: {link}\n"
    query.message.reply_text(text=caption)

dispatcher.add_handler(CommandHandler('start', welcome))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, find_movie))
dispatcher.add_handler(CallbackQueryHandler(movie_result))

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    # Logic to set up webhook
    return 'Webhook setup successful'  # Or any appropriate response

def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return 'ok'

if __name__ == '__main__':
    app.run(port=5000)
