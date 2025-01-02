import requests
import json
import psycopg2
from psycopg2 import sql
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import logging
import schedule
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("4chan crawler")

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = "localhost"
DB_NAME = "fourchan_data"
DB_USER = "atharvr"
DB_PASSWORD = "Bing2025"
DB_PORT = "5432"
FAKTORY_SERVER_URL = "tcp://localhost:7419"
DATABASE_URL = "postgresql://atlocalhost:5432/4chan_data/"

# Function to establish a database connection
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn

# Function to insert posts into the database
def insert_posts_into_db(posts, conn):
    with conn.cursor() as cur:
        try:
            cur.execute("SET search_path TO fourchan_schema;")
        except Exception as e:
            logger.error(f"Error setting schema search path: {e}")
            return  # Exit the function if schema can't be set

        for post in posts:
            try:
                post_data = {
                    'post_id': post.get('no'),
                    'name': post.get('name', ''),
                    'comment': json.dumps(post.get('com', '')),
                    'filename': post.get('filename', ''),
                    'ext': post.get('ext', ''),
                    'w': post.get('w', None),
                    'h': post.get('h', None),
                    'time': post.get('time'),
                    'resto': post.get('resto', 0)
                }
                logger.info(f"Inserting post data: {post_data}")
                cur.execute("""
                    INSERT INTO chanposts (post_id, name, comment, filename, ext, w, h, time, resto)
                    VALUES (%(post_id)s, %(name)s, %(comment)s, %(filename)s, %(ext)s, %(w)s, %(h)s, %(time)s, %(resto)s)
                    ON CONFLICT (post_id) DO NOTHING;
                """, post_data)
                logger.info(f"Inserted post with ID: {post_data['post_id']}")
            except Exception as e:
                conn.rollback()
                logger.error(f"Error inserting data for post {post.get('no')}: {e}")
            else:
                conn.commit()

# Function to fetch threads from 4chan API
def fetch_thread_ids_from_4chan(board):
    url = f"https://a.4cdn.org/{board}/threads.json"
    response = requests.get(url)
    if response.status_code == 200:
        pages = response.json()
        thread_ids = []
        for page in pages:
            for thread in page['threads']:
                thread_ids.append(thread['no'])
        return thread_ids
    else:
        logger.error(f"Failed to fetch data from 4chan API. Status Code: {response.status_code}")
        return []

# Function to fetch posts from each thread
def fetch_posts_from_threads(board, thread_ids):
    posts = []
    for thread_id in thread_ids:
        url = f"https://a.4cdn.org/{board}/thread/{thread_id}.json"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                thread_data = response.json()
                thread_posts = thread_data.get('posts', [])
                posts.extend(thread_posts)
            else:
                logger.warning(f"Failed to fetch posts for thread {thread_id}: Status Code {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Error fetching posts for thread {thread_id}: {e}")
    return posts

# Main function to run the crawler
def run_4chan_crawler(board="fit"):
    logger.info(f"Starting crawl for board: {board}")
    conn = get_db_connection()

    try:
        thread_ids = fetch_thread_ids_from_4chan(board)
        if thread_ids:
            posts = fetch_posts_from_threads(board, thread_ids)
            if posts:
                insert_posts_into_db(posts, conn)
            else:
                logger.info("No posts to insert.")
        else:
            logger.info("No threads found.")
    except Exception as e:
        logger.error(f"Error during crawling: {e}")
    finally:
        conn.close()
        logger.info("Database connection closed.")

# Schedule the crawler to run every 10 minutes
schedule.every(10).minutes.do(run_4chan_crawler, board="fit")

# Run scheduled tasks
if __name__ == "__main__":
    logger.info("Starting the 10-minute scheduler for the 4chan crawler.")
    while True:
        schedule.run_pending()
        time.sleep(1)
