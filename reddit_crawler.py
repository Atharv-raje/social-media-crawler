from datetime import datetime, timezone
from db_connector import get_db_connection
from reddit_client import fetch_posts, fetch_comments

# Function to create tables if they don't exist
def create_reddit_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reddit_posts (
                id VARCHAR PRIMARY KEY,
                title TEXT,
                body TEXT,
                created_utc TIMESTAMP,
                score INT,
                url TEXT,
                subreddit VARCHAR
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reddit_comments (
                id VARCHAR PRIMARY KEY,
                post_id VARCHAR REFERENCES reddit_posts(id),
                body TEXT,
                created_utc TIMESTAMP,
                score INT
            );
        """)
        conn.commit()

# Function to insert posts
def insert_posts_into_db(posts, subreddit, conn):
    with conn.cursor() as cur:
        for post in posts:
            created_utc = datetime.fromtimestamp(post['created_utc'], tz=timezone.utc)
            cur.execute("""
                INSERT INTO reddit_posts (id, title, body, created_utc, score, url, subreddit)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """, (post['id'], post['title'], post['body'], created_utc, post['score'], post['url'], subreddit))
            comments = fetch_comments(post['id'])
            print('comments')
            print(comments)
            print('end comments')
            insert_comments_into_db(comments, post['id'], conn)
        conn.commit()

# def fetch_comments(post_id):
#     global latest_comment_timestamps
#     token = get_reddit_access_token()
#     headers = {'Authorization': f'bearer {token}', 'User-Agent': REDDIT_USER_AGENT}
#     url = f'https://oauth.reddit.com/comments/{post_id}?limit=10'
#     response = requests.get(url, headers=headers)
#     comments = []

#     if response.status_code == 200:
#         try:
#             # Navigate to the correct part of the JSON response where comments are located
#             comment_data = response.json()[1]['data']['children']
            
#             for comment in comment_data:
#                 comment_info = comment['data']
                
#                 # Ensure we only fetch required fields for each comment
#                 comment_id = comment_info.get('id')
#                 comment_body = comment_info.get('body')
#                 comment_created_utc = comment_info.get('created_utc')
#                 comment_score = comment_info.get('score')

#                 # Append to comments list if required fields are present
#                 if comment_id and comment_body and comment_created_utc is not None:
#                     comments.append({
#                         'id': comment_id,
#                         'body': comment_body,
#                         'created_utc': comment_created_utc,
#                         'score': comment_score
#                     })

#             # Debugging: Print the comments list to confirm correct extraction
#             print(f"Fetched {len(comments)} comments for post 2 {post_id}:")
#             print(json.dumps(comments, indent=2))
        
#         except (IndexError, KeyError, TypeError) as e:
#             print(f"Error parsing JSON response for comments on post {post_id}: {e}")
#     else:
#         print(f"Error fetching comments for post {post_id}: {response.status_code}")
    
#     return comments

# Function to insert comments
def insert_comments_into_db(comments, post_id, conn):
    print('in inserting')
    with conn.cursor() as cur:
        for comment in comments:
            print('comment')
            print(comment)
            try:
                created_utc = datetime.fromtimestamp(comment['created_utc'], tz=timezone.utc)
                cur.execute("""
                    INSERT INTO reddit_comments (id, post_id, body, created_utc, score)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """, (comment['id'], post_id, comment['body'], created_utc, comment['score']))
                # Debugging: Print each comment being inserted
                print(f"Inserted comment {comment['id']} for post {post_id}")
            except Exception as e:
                print(f"Error inserting comment {comment['id']} for post {post_id}: {e}")
        conn.commit()

# Main crawler function
def run_reddit_crawler(subreddits, limit=10):
    conn = get_db_connection()
    create_reddit_tables(conn)
    for subreddit in subreddits:
        posts = fetch_posts(subreddit, limit)
        insert_posts_into_db(posts, subreddit, conn)
    conn.close()
