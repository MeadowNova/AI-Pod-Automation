import requests
import time
import logging
from pod_automation.config import get_config

logger = logging.getLogger(__name__)

class PinterestAPI:
    """Client for interacting with the Pinterest API."""

    TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"
    API_BASE_URL = "https://api.pinterest.com/v5"

    def __init__(self, app_id=None, app_secret=None, access_token=None, refresh_token=None):
        config = get_config()
        pinterest_cfg = config.get("api.pinterest", {})

        self.app_id = app_id or pinterest_cfg.get("app_id")
        self.app_secret = app_secret or pinterest_cfg.get("app_secret")
        self.access_token = access_token or pinterest_cfg.get("access_token")
        self.refresh_token = refresh_token or pinterest_cfg.get("refresh_token")
        self.token_expiry = pinterest_cfg.get("token_expiry", 0)

        if not self.app_id or not self.app_secret:
            logger.warning("Pinterest App ID and Secret are required.")

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def refresh_access_token(self):
        """Refresh the Pinterest access token using the refresh token."""
        if not self.refresh_token:
            logger.error("No refresh token available.")
            return False

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.app_id,
            "client_secret": self.app_secret
        }

        try:
            response = requests.post(self.TOKEN_URL, data=data)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                self.refresh_token = token_data.get("refresh_token", self.refresh_token)
                self.token_expiry = time.time() + token_data.get("expires_in", 3600)

                # Save updated tokens
                config = get_config()
                pinterest_cfg = config.get("api.pinterest", {})
                pinterest_cfg["access_token"] = self.access_token
                pinterest_cfg["refresh_token"] = self.refresh_token
                pinterest_cfg["token_expiry"] = self.token_expiry
                config.set("api.pinterest", pinterest_cfg)
                config.save_config()

                logger.info("Pinterest access token refreshed successfully.")
                return True
            else:
                logger.error(f"Failed to refresh Pinterest token: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Exception refreshing Pinterest token: {str(e)}")
            return False

    def get_user_profile(self):
        """Fetch the Pinterest user profile."""
        url = f"{self.API_BASE_URL}/user_account"
        headers = self._get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_boards(self):
        """Fetch the user's Pinterest boards."""
        url = f"{self.API_BASE_URL}/boards"
        headers = self._get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def create_pin(self, board_id, title, description, link, image_url):
        """Create a new pin on a board."""
        url = f"{self.API_BASE_URL}/pins"
        headers = self._get_headers()
        data = {
            "board_id": board_id,
            "title": title,
            "description": description,
            "link": link,
            "media_source": {
                "source_type": "image_url",
                "url": image_url
            }
        }
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
