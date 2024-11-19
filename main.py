import os
import requests
from dotenv import load_dotenv

load_dotenv()
CONSUMER_KEY = os.getenv("CONSUMER_KEY")


# Step 1: Request a temporary request token
def get_request_token():
    url = "https://getpocket.com/v3/oauth/request"
    headers = {"X-Accept": "application/json"}
    data = {"consumer_key": CONSUMER_KEY, "redirect_uri": "https://getpocket.com"}
    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()
    return response_data.get("code")


# Step 2: Get user authorization
def authorize_user(request_token):
    print("Visit the following URL to authorize the app:")
    print(f"https://getpocket.com/auth/authorize?request_token={request_token}&redirect_uri=https://getpocket.com")
    input("Press Enter after authorizing the app...")


# Step 3: Convert request token to access token
def get_access_token(request_token):
    url = "https://getpocket.com/v3/oauth/authorize"
    headers = {"X-Accept": "application/json"}
    data = {"consumer_key": CONSUMER_KEY, "code": request_token}
    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()
    return response_data.get("access_token")


def fetch_saved_items(consumer_key, access_token):
    url = "https://getpocket.com/v3/get"
    headers = {"X-Accept": "application/json"}
    data = {
        "consumer_key": consumer_key,
        "access_token": access_token,
        "state": "all",  # Options: unread, archive, or all
        "detailType": "complete",  # Fetch full details
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json().get("list", {})


if __name__ == "__main__":
    request_token = get_request_token()
    authorize_user(request_token)
    ACCESS_TOKEN = get_access_token(request_token)
    saved_items = fetch_saved_items(CONSUMER_KEY, ACCESS_TOKEN)
    for item_id, item in saved_items.items():
        print(f"Title: {item.get('resolved_title')}, URL: {item.get('resolved_url')}")
