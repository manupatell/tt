import requests
from bs4 import BeautifulSoup
import imdb  # Install using `pip install imdbpy`
from telegram import Update, Ext  # Install using `pip install python-telegram-bot`

# **DO NOT include your bot token here!**
# Store it securely in an environment variable or a separate configuration file.
bot_token = os.getenv("6767569372:AAHBwlrvRvYkUxhBigvKSELDuWZToyVA5fM")  # Replace with your actual token

def search_justwatch(movie_name):
    """Searches Justwatch for a movie and returns the movie URL if found.

    Args:
        movie_name (str): The name of the movie to search for.

    Returns:
        str: The URL of the movie on Justwatch, or None if not found.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the HTTP request.
    """

    base_url = "https://www.justwatch.com/en/IN/search"  # Adjust region if needed
    search_params = {"q": movie_name}

    try:
        response = requests.get(base_url, params=search_params)
        response.raise_for_status()  # Raise an exception for non-200 status codes

        soup = BeautifulSoup(response.content, 'html.parser')

        # Try to find the first movie result (heuristic)
        movie_link = soup.find("a", class_="title-list-grid__item--link")  # Adjust selector as needed
        if movie_link:
            return base_url + movie_link["href"]
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error searching Justwatch for {movie_name}: {e}")
        return None


def get_imdb_info(movie_title):
    """Searches IMDb for a movie and returns the IMDb ID and streaming provider (if found).

    Args:
        movie_title (str): The title of the movie to search for.

    Returns:
        dict: A dictionary containing the IMDb ID (if found) and a potential streaming 
              provider (based on heuristics).

    Raises:
        imdb.exceptions.IMDbError: If an error occurs while fetching IMDb data.
    """

    ia = imdb.IMDb()

    try:
        # Search IMDb by title (may return multiple results)
        movies = ia.search_movie(movie_title)

        # Check if results are found and pick the first match (heuristic)
        if movies:
            movie = movies[0]
            imdb_id = movie.movieID
            # Try to identify streaming provider from movie description (limited accuracy)
            streaming_provider = None
            for provider in ["netflix", "hulu", "disneyplus"]:
                if provider in movie.summary.lower():
                    streaming_provider = provider.capitalize()
                    break
            return {"imdb_id": imdb_id, "streaming_provider": streaming_provider}
        else:
            return {}

    except imdb.exceptions.IMDbError as e:
        print(f"Error fetching IMDb data for {movie_token}: {e}")
        return {}


def handle_search(update: Update, context: Ext.CallbackContext):
    """Handles user search queries."""

    # Extract movie name from the message (assuming single word after "/search")
    movie_name = update.message.text.split()[1]

    justwatch_url = search_justwatch(movie_name)

    if justwatch_url:
        update.message.reply_text(f"Justwatch URL: {justwatch_url}")

        # Extract movie title from Justwatch URL (heuristic)
        movie_title = justwatch_url.split("/")[-1].replace("-", " ")

        imdb_info = get_imdb_info(movie_title)
        imdb_id = imdb_info.get('imdb_id')
        streaming_provider = imdb_info.get('streaming_provider')

        message = f"Movie Title: {movie_title}\n"
        if imdb_id:
            message += f"IMDb ID: {imdb_id}\n"
        if streaming_provider:
            message += f"Potential Streaming Provider: {streaming_provider}"
        update.message.reply_text(message)
    else:
        update.message.reply_text(f"Movie '{movie_name}' not found on Just
