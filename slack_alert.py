import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Make sure to install the library first: pip install slack-sdk

# Your Slack bot token (starts with 'xoxb-').
# It's best practice to store this in an environment variable.
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

# The channel ID where you want to send the message.
# You can find this in the URL of the channel (e.g., C0XXXXXXX).
CHANNEL_ID = "C09A8LUMU4R"  # Or a channel ID like 'C1234567890'


def send_slack_message(channel, text):
    """
    Sends a message to a Slack channel.
    """
    try:
        # Check if the bot token is set
        if not SLACK_BOT_TOKEN:
            raise ValueError("SLACK_BOT_TOKEN is not set.")

        client = WebClient(token=SLACK_BOT_TOKEN)

        response = client.chat_postMessage(channel=channel, text=text)
        print(
            f"Message sent successfully to channel {channel}. Response: {response['ts']}"
        )

    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")
    except ValueError as e:
        print(f"Configuration error: {e}")


if __name__ == "__main__":
    send_slack_message(CHANNEL_ID, text="Hello from your Python script!")
