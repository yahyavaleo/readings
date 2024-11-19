import os
import requests
import time
import json
import webbrowser

from dotenv import load_dotenv


class PocketSavesRetriever:
    def __init__(self, consumer_key, redirect_uri):
        """
        Initialize the Pocket API retriever

        :param consumer_key: Your Pocket consumer key
        :param redirect_uri: Redirect URI for authentication callback
        """
        self.consumer_key = consumer_key
        self.redirect_uri = redirect_uri
        self.request_token = None
        self.access_token = None
        self.username = None

    def get_request_token(self):
        """
        Obtain a request token from Pocket
        """
        url = "https://getpocket.com/v3/oauth/request"
        payload = {"consumer_key": self.consumer_key, "redirect_uri": self.redirect_uri}
        headers = {"Content-Type": "application/json", "X-Accept": "application/json"}

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            self.request_token = response.json()["code"]
            print(f"Request Token obtained: {self.request_token}")
            return self.request_token
        else:
            raise Exception(f"Failed to get request token. Status: {response.status_code}")

    def authorize_user(self):
        """
        Redirect user to Pocket authorization page
        """
        if not self.request_token:
            raise Exception("Request token not obtained. Call get_request_token() first.")

        auth_url = (
            f"https://getpocket.com/auth/authorize?request_token={self.request_token}&redirect_uri={self.redirect_uri}"
        )
        print("Please authorize the app in the browser that will now open.")
        webbrowser.open(auth_url)

        input("Press Enter after you have authorized the app in the browser...")

    def get_access_token(self):
        """
        Convert request token to access token
        """
        if not self.request_token:
            raise Exception("Request token not obtained. Call get_request_token() first.")

        url = "https://getpocket.com/v3/oauth/authorize"
        payload = {"consumer_key": self.consumer_key, "code": self.request_token}
        headers = {"Content-Type": "application/json", "X-Accept": "application/json"}

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            result = response.json()
            self.access_token = result["access_token"]
            self.username = result["username"]
            print(f"Access token obtained for user: {self.username}")
            return self.access_token
        else:
            raise Exception(f"Failed to get access token. Status: {response.status_code}")

    def retrieve_saves(self, count=100, offset=0, state="unread"):
        """
        Retrieve Pocket saves

        :param count: Number of items to retrieve (default 100)
        :param offset: Number of items to skip (for pagination)
        :param state: State of saves to retrieve (unread, archive, all)
        :return: List of Pocket items
        """
        if not self.access_token:
            raise Exception("Access token not obtained. Complete authentication first.")

        url = "https://getpocket.com/v3/get"
        payload = {
            "consumer_key": self.consumer_key,
            "access_token": self.access_token,
            "state": state,
            "sort": "newest",
            "count": count,
            "offset": offset,
        }
        headers = {"Content-Type": "application/json", "X-Accept": "application/json"}

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            saves = response.json().get("list", {})
            return [saves[item] for item in saves]
        else:
            raise Exception(f"Failed to retrieve saves. Status: {response.status_code}")


def main():
    load_dotenv()
    CONSUMER_KEY = os.getenv("CONSUMER_KEY")
    REDIRECT_URI = "pocketapp1234:authorizationFinished"

    # Initialize the retriever
    pocket_retriever = PocketSavesRetriever(CONSUMER_KEY, REDIRECT_URI)

    try:
        # Get request token
        pocket_retriever.get_request_token()

        # Authorize user
        pocket_retriever.authorize_user()

        # Get access token
        pocket_retriever.get_access_token()

        # Retrieve saves
        saves = pocket_retriever.retrieve_saves(count=50)

        # Print saves details
        for save in saves:
            print(f"Title: {save.get('resolved_title', 'No Title')}")
            print(f"URL: {save.get('resolved_url', 'No URL')}")
            print(f"Time Added: {save.get('time_added', 'Unknown')}")
            print("---")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
