#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File:        redacted.py
Author:      github.com/richburg
Created:     2025-08-31
Description: Redact your messages in a specific Discord channel
"""

import logging
import sys
from typing import Final, Optional

from httpx import Client

# - Logging setup -

logging.basicConfig(
    level="INFO",
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# - API endpoints -

API_BASE: Final[str] = "https://discord.com/api/v9"
MESSAGES_ENDPOINT: Final[str] = API_BASE + "/channels/{0}/messages?limit=100"
MESSAGE_ENDPOINT: Final[str] = API_BASE + "/channels/{0}/messages/{1}"

# - Core functions -


def create_client(account_token: str) -> Client:
    client = Client(headers={"Authorization": account_token})
    return client


def get_messages(session: Client, channel_id: str, user_id: str) -> list[dict]:
    before: Optional[int] = None
    filtered_messages: list[dict] = []

    while True:
        url: str = MESSAGES_ENDPOINT.format(channel_id)
        url += f"&before={before}" if before else ""

        response = session.get(url)
        response.raise_for_status()

        unfiltered_messages: Optional[dict] = response.json()
        if not unfiltered_messages:
            break

        for message in unfiltered_messages:
            if message["author"]["id"] == user_id:
                filtered_messages.append(message)

        before = int(unfiltered_messages[-1]["id"])

    logging.info(f"Found {len(filtered_messages)} message(s) sent by you")
    return filtered_messages


def delete_message(session: Client, message_id: str, channel_id: str) -> None:
    response = session.delete(MESSAGE_ENDPOINT.format(channel_id, message_id))
    if response.is_success:
        logging.info(f"Message with ID {message_id} is deleted")
    else:
        logging.info(f"Unable to delete message with ID {message_id}")


# - Command line interface


def die(message: str, code: int) -> None:
    print("error:", message)
    sys.exit(code)


def main() -> None:
    if len(sys.argv) < 4:
        die("incorrect cli usage", 2)

    token: str = sys.argv[1]
    user_id: str = sys.argv[2]
    channel_id: str = sys.argv[3]

    session = create_client(token)
    messages = get_messages(session, channel_id, user_id)

    for message in messages:
        delete_message(session, message["id"], channel_id)


if __name__ == "__main__":
    main()
