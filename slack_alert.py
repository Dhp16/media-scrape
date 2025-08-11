import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from manage_podcasts.config import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID


def send_slack_message(text):
    try:
        if not SLACK_BOT_TOKEN:
            raise ValueError("SLACK_BOT_TOKEN is not set.")

        client = WebClient(token=SLACK_BOT_TOKEN)

        response = client.chat_postMessage(channel=SLACK_CHANNEL_ID, text=text)
        print(
            f"Message sent successfully to channel {SLACK_CHANNEL_ID}. Response: {response['ts']}"
        )

    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")
    except ValueError as e:
        print(f"Configuration error: {e}")


if __name__ == "__main__":
    send_slack_message("Hello from your Python script!")
