#!/usr/bin/env python3
"""
Date: 2024-10-07
Purpose: lvrbot - Low Volume Reply Bot (for Reddit)
Website: https://lvrbot.com
"""
import configparser
import json
import pathlib
import praw

software_version = "0.0.1"
user_agent = "python:com.lvrbot:v" + software_version + " (by u/lvrbot)"
post_limit = 10

config = configparser.ConfigParser()
config.read(str(pathlib.Path(__file__).absolute())[:-2] + "ini")

client_id = config["config"]["client_id"]
client_secret = config["config"]["client_secret"]
reddit_username = config["config"]["reddit_username"]
reddit_password = config["config"]["reddit_password"]
subreddit = config["config"]["subreddit"]
reply_prefix = config["config"]["reply_prefix"]
reply_suffix = config["config"]["reply_suffix"]

reddit_read = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent,
)

reddit_write = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    username=reddit_username,
    password=reddit_password,
    user_agent=user_agent,
)


# =============================================================================
# Main                                                                     Main
# ----------------------------------------------------------
def main():

    live_ids = get_live_posts()
    past_ids = get_past_posts()
    remaining_ids = get_remaining_ids(live_ids, past_ids)

    try:

        id_to_comment_on = remaining_ids.pop()

    except Exception as e:

        exit(f"No new posts to comment on.\n\rError: {e}")

    write_to_past_posts(id_to_comment_on)

    submission = reddit_write.submission(id_to_comment_on)
    submission.reply(
        body=reply_prefix + " " + get_reply_text() + "  \n  \n" + reply_suffix
    )


# =============================================================================
# Functions                                                           Functions
# ----------------------------------------------------------
def get_file_contents(filename):

    with open(filename) as file:
        file_contents = file.read().splitlines()

    return [x for x in file_contents if not x.startswith("#") if x != ""]


def get_reply_text():

    with open(str(pathlib.Path(__file__).absolute())[:-2] + "replies") as file:
        file_contents = json.load(file)

    # Retrieve the top reply
    reply_text = file_contents[0]

    # Move the top reply to the bottom of the list
    reorder_replies()

    return reply_text["reply"]


def reorder_replies():

    with open(str(pathlib.Path(__file__).absolute())[:-2] + "replies") as file:
        file_contents = json.load(file)

    # Remove the top reply and set it as the reply to post
    top_entry = file_contents.pop(0)

    # Move the top reply to the bottom of the list
    file_contents.append(top_entry)

    # Re-write the reordered list to the file
    with open(str(pathlib.Path(__file__).absolute())[:-2] + "replies", "w") as file:
        json.dump(file_contents, file, indent=4)

    return


def get_live_posts():

    live_ids = []

    for live_posts in reddit_read.subreddit(subreddit).new(limit=post_limit):
        live_ids.append(live_posts.id)

    return live_ids


def get_past_posts():

    past_ids = []

    past_posts = get_file_contents(
        str(pathlib.Path(__file__).absolute())[:-2] + "posts"
    )

    for past_post in past_posts:
        past_ids.append(past_post)

    return past_ids


def get_remaining_ids(live_ids, past_ids):
    return set(live_ids) - set(past_ids)


def get_id_to_comment_on(remaining_ids):
    return str(remaining_ids.pop())


def write_to_past_posts(post_id):
    past_posts_file = open(str(pathlib.Path(__file__).absolute())[:-2] + "posts", "a")
    past_posts_file.write(post_id + "\n")
    past_posts_file.close()
    return


# ----------------------------------------------------------
if __name__ == "__main__":
    main()
