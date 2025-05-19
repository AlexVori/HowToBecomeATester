import pytest
from playwright.sync_api import sync_playwright, APIRequestContext
import json

from spotify_token import get_spotify_token

SPOTIFY_TOKEN = get_spotify_token()

ARTIST_ID = "3F2lwRt2FQ30q32nj35oHq"
URL_APP = f"https://api.spotify.com/v1/artists/{ARTIST_ID}"

@pytest.fixture(scope="session")
def api_context() -> APIRequestContext:
    playwright = sync_playwright().start()
    context = playwright.request.new_context(
        base_url="https://api.spotify.com/v1",
        extra_http_headers={
            "Authorization": f"Bearer {SPOTIFY_TOKEN}",
            "Accept": "application/json"
        }
    )
    yield context
    playwright.stop()

def test_get_artist_info(api_context):

    response = api_context.get(URL_APP)
    assert response.status == 200, f"Unexpected status code: {response.status}"
    body = response.json()


    # Extract and print relevant artist details
    print("🎤 Artist Info:")
    print(f"Name: {body.get('name')}")
    print(f"Genres: {', '.join(body.get('genres', []))}")
    print(f"Popularity: {body.get('popularity')}")
    print(f"Followers: {body.get('followers', {}).get('total')}")
    print(f"Spotify URL: {body.get('external_urls', {}).get('spotify')}")

    related_artists_response = api_context.get(f"{URL_APP}/related-artists")
    assert response.status == 200, f"Unexpected status code: {response.status}"
    related_artists_body = related_artists_response.json()
    related_artists = related_artists_body.get("artists", [])

    print("\n🎤 Related Artists:")
    if related_artists:
        for i, artist in enumerate(related_artists, start=1):
            artist_name = artist.get("name")
            print(f"{i}. {artist_name}")
    else:
        print("No related artists found.")

def test_get_top10_tracks(api_context):
    response = api_context.get(f"{URL_APP}/top-tracks?market=US")

    assert response.status == 200, f"Unexpected status code: {response.status}"

    body = response.json()
    tracks = body.get("tracks", [])

    print("\n🎵 Top Tracks:")
    for i, track in enumerate(tracks):
        track_name = track.get('name')
        track_popularity = track.get('popularity')
        album_info = track.get('album', {})
        album_name = album_info.get('name')
        release_date = album_info.get('release_date')
        precision = album_info.get('release_date_precision')

        # Extract year based on precision
        if precision == "year":
            year = release_date
        else:
            year = release_date.split("-")[0] if release_date else "Unknown"

        print(f"{i + 1}. {track_name} from album '{album_name}' released in {year}. Popularity rating: {track_popularity}")

    assert len(tracks) > 0, "No tracks returned in response"
