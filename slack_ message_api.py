import logging,os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
# client = WebClient(token=os.environ.get("env"))

logger = logging.getLogger(__name__)


def fetchchannel():
    channel_name = "watchdog_alarms"
    conversation_id = None
    try:
        # print(client.conversations_list())
        # Call the conversations.list method using the WebClient
        for result in client.conversations_list():
            # print(result)
            if conversation_id is not None:
                break
            for channel in result["channels"]:
                print(channel["name"])
                if channel["name"] == channel_name:
                    print(channel)
                    conversation_id = channel["id"]
                    # Print result
                    print(f"Found conversation ID: {conversation_id}")
                    break

    except SlackApiError as e:
        print(f"Error: {e}")




def publish_message():
    # ID of channel you want to post message to
    # channel_id = "C01918B8WDD"
    channel_id = "C01A549VDHS"
    # channel_id = "slow_control"

    try:
        # Call the conversations.list method using the WebClient
        result = client.chat_postMessage(
            channel=channel_id,
            text="And I am Bubble :)"
            # You could also use a blocks[] array to send richer content
        )
        # Print result, which includes information about the message (like TS)
        print(result)

    except SlackApiError as e:
        print(f"Error: {e}")


if __name__ =="__main__":
    # fetchchannel()
    publish_message()
