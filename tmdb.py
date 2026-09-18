import requests


API_KEY = "5326de6853eb6b84402447748595915f"

BASE_URL = "https://api.themoviedb.org/3"

IMAGE_URL = "https://image.tmdb.org/t/p/w500"


def tmdb_request(endpoint, params=None):

    if params is None:
        params = {}

    params["api_key"] = API_KEY
    params["language"] = "en-US"

    url = BASE_URL + endpoint

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(
            f"TMDB Error: {response.status_code}"
        )

    return response.json()


def trending_movies():

    data = tmdb_request(
        "/trending/all/week"
    )

    return data.get("results", [])


def top_rated_movies():

    data = tmdb_request(
        "/movie/top_rated"
    )

    return data.get("results", [])


def search_movies(query):

    data = tmdb_request(
        "/search/multi",
        {
            "query": query,
            "include_adult": False
        }
    )

    return [
        movie
        for movie in data.get("results", [])
        if movie.get("media_type") in ["movie", "tv"]
    ]


def movie_details(movie_id, media_type="movie"):

    return tmdb_request(
        f"/{media_type}/{movie_id}",
        {
            "append_to_response": "credits,reviews"
        }
    )


def movies_by_genre(genre_id):

    data = tmdb_request(
        "/discover/movie",
        {
            "with_genres": genre_id,
            "sort_by": "popularity.desc"
        }
    )

    return data.get("results", [])


def hidden_gems():

    data = tmdb_request(
        "/discover/movie",
        {
            "sort_by": "vote_average.desc",
            "vote_count.gte": 50
        }
    )

    return data.get("results", [])


def movies_by_year(year):

    data = tmdb_request(
        "/discover/movie",
        {
            "primary_release_year": year,
            "sort_by": "popularity.desc"
        }
    )

    return data.get("results", [])