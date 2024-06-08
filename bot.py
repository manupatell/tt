import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Your Telegram bot token
TOKEN = '7464935338:AAHz6kOVLkom_7M9INTtO3J9TUihIEXM0DE'

def search_movie(movie_name):
    # Base URL for JustWatch search
    base_url = "https://www.justwatch.com/in/search"
    
    # Parameters for the search query
    params = {
        "q": movie_name
    }
    
    # Send a GET request to search for the movie
    response = requests.get(base_url, params=params)
    
    # Parse the HTML content of the search results page with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the first movie link in the search results
    movie_link = soup.find("a", class_="title-list-grid__item--link")
    
    # If a movie link is found
    if movie_link:
        movie_url = "https://www.justwatch.com" + movie_link["href"]
        
        # Send a GET request to the movie's page
        movie_response = requests.get(movie_url)
        movie_soup = BeautifulSoup(movie_response.text, 'html.parser')
        
        # Extract the movie name
        movie_name = movie_soup.find("h1", class_="title").text.strip() if movie_soup.find("h1", class_="title") else None
        
        # Extract IMDb ID
        imdb_link = movie_soup.find("a", href=lambda href: href and "imdb.com" in href)
        imdb_id = imdb_link["href"].split('/')[-2] if imdb_link else None
        
        # Extract streaming providers
        providers = movie_soup.find_all("div", class_="price-comparison__grid__row__icon")
        streaming_providers = [provider.get('alt') for provider in providers if provider.get('alt')]
        
        # Create a dictionary with movie details
        movie_details = {
            "Movie URL": movie_url,
            "Movie Name": movie_name,
            "IMDb ID": imdb_id,
            "Streaming Providers": streaming_providers
        }
        
        return movie_details
    else:
        return None

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Use /search <movie_name> to get movie details from JustWatch.')

def search(update: Update, context: CallbackContext) -> None:
    if context.args:
        movie_name = " ".join(context.args)
        movie_details = search_movie(movie_name)
        
        if movie_details:
            response_message = (
                f"Movie URL: {movie_details['Movie URL']}\n"
                f"Movie Name: {movie_details['Movie Name']}\n"
                f"IMDb ID: {movie_details['IMDb ID']}\n"
                f"Streaming Providers: {', '.join(movie_details['Streaming Providers'])}"
            )
        else:
            response_message = "Movie not found."
    else:
        response_message = "Please provide a movie name."
    
    update.message.reply_text(response_message)

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("search", search))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
