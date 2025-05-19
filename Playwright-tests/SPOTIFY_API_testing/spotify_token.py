import requests
import base64

# Replace these with your Spotify app credentials
CLIENT_ID = "0b2c7a914ff94a599c85f27ba3eaea40"
CLIENT_SECRET = "394871a64d564653892d9856320937e1"

def get_spotify_token():
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth_str}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)

    if response.status_code != 200:
        raise Exception(f"Failed to get token: {response.status_code} - {response.text}")

    token_info = response.json()
    return token_info["access_token"]

