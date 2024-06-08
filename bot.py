import requests
from bs4 import BeautifulSoup
import imdb  # Install using `pip install imdbpy`

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


def main():
    movie_name = input("Enter the movie name: ")

    # **DO NOT include your bot token here!**
    # Store it securely in an environment variable or a separate configuration file.
    # Replace '<YOUR_BOT_TOKEN>' with the actual token when deploying the bot.

    justwatch_url = search_justwatch(movie_name)

    if justwatch_url:
        print(f"Justwatch URL: {justwatch_url}")

        # Extract movie title from Justwatch URL (heuristic)
        movie_title = justwatch_url.split("/")[-1].replace("-", " ")

        imdb_info = get_imdb_info(movie_title)
        print(f"Movie Title: {movie_title}")
        print(f"IMDb ID: {imdb_info.get('imdb_id')}")
        print(f"Potential Streaming Provider: {imdb_info.get('streaming_provider')}")
    else:
        print(f"Movie '{movie_name}' not found on Justwatch.")


if __name__ == "__main__":
    main()
