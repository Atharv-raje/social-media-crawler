import os
import requests
from dotenv import load_dotenv
import json
import time

# Load environment variables from .env
load_dotenv()

# Reddit API credentials
REDDIT_CLIENT_ID = "b01xL9Te80ZSYprJkajWgQ"
REDDIT_SECRET = "W3_8bxv770742-k4p5AomU65Vgl3cg"
REDDIT_USER_AGENT = "your_user_agent"
REDDIT_USERNAME = "Unable-Age-5420"
REDDIT_PASSWORD = "ssawant4reddit"

# Global token and expiry time cache
token = None
token_expiry_time = None

def get_reddit_access_token():
    global token, token_expiry_time
    if token and token_expiry_time and token_expiry_time > time.time():
        return token  # Reuse token if valid
    
    auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_SECRET)
    data = {'grant_type': 'password', 'username': REDDIT_USERNAME, 'password': REDDIT_PASSWORD}
    headers = {'User-Agent': REDDIT_USER_AGENT}

    res = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
    token = res.json().get('access_token')
    expires_in = res.json().get('expires_in', 3600)
    token_expiry_time = time.time() + expires_in - 60
    return token

# Initialize dictionaries to store timestamps
latest_post_timestamps = {}
latest_comment_timestamps = {}

# Function to load timestamps for persistence
def load_timestamps():
    global latest_post_timestamps, latest_comment_timestamps
    if os.path.exists("timestamps.json"):
        with open("timestamps.json", "r") as file:
            data = json.load(file)
            latest_post_timestamps = data.get("posts", {})
            latest_comment_timestamps = data.get("comments", {})

# Function to save timestamps
def save_timestamps():
    with open("timestamps.json", "w") as file:
        json.dump({"posts": latest_post_timestamps, "comments": latest_comment_timestamps}, file)

# Function to fetch posts
def fetch_posts(subreddit_name, limit=10):
    global latest_post_timestamps
    token = get_reddit_access_token()
    headers = {'Authorization': f'bearer {token}', 'User-Agent': REDDIT_USER_AGENT}
    url = f'https://oauth.reddit.com/r/{subreddit_name}/new?limit={limit}'  # Fetch latest posts
    
    response = requests.get(url, headers=headers)
    posts = []
    
    if response.status_code == 200:
        for post in response.json()['data']['children']:
            post_data = post['data']
            post_timestamp = post_data['created_utc']
            
            # Check if post is new
            if latest_post_timestamps.get(subreddit_name) is None or post_timestamp > latest_post_timestamps[subreddit_name]:
                post_comments = fetch_comments(post_data['id'])
                
                posts.append({
                    'subreddit': subreddit_name,
                    'id': post_data['id'],
                    'title': post_data['title'],
                    'body': post_data.get('selftext', ''),
                    'created_utc': post_data['created_utc'],
                    'score': post_data['score'],
                    'url': post_data['url'],
                    'comments': post_comments
                })
        
        if posts:
            latest_post_timestamps[subreddit_name] = max(post['created_utc'] for post in posts)
    else:
        print(f"Error fetching data for {subreddit_name}: {response.status_code}")
    
    return posts

# Function to fetch comments
def fetch_comments(post_id):
    global latest_comment_timestamps
    token = get_reddit_access_token()
    headers = {'Authorization': f'bearer {token}', 'User-Agent': REDDIT_USER_AGENT}
    url = f'https://oauth.reddit.com/comments/{post_id}?limit=10'
    response = requests.get(url, headers=headers)
    comments = []
    
    if response.status_code == 200:
        # Print full JSON response to inspect structure
        comment_data = response.json()
        # print(f"Full JSON response for post {post_id}: {json.dumps(comment_data, indent=2)}")
        
        # Try to parse the response as expected
        try:
            comment_data = response.json()[1]['data']['children']
            for comment in comment_data:
                if 'created_utc' in comment['data']:
                    comment_timestamp = comment['data']['created_utc']
                    if latest_comment_timestamps.get(post_id) is None or comment_timestamp > latest_comment_timestamps.get(post_id, 0):
                        if 'body' in comment['data']:
                            comments.append({
                                'id': comment['data']['id'],
                                'body': comment['data']['body'],
                                'created_utc': comment['data']['created_utc'],
                                'score': comment['data']['score']
                            })
        except (IndexError, KeyError, TypeError) as e:
            print(f"Error parsing JSON response for post {post_id}: {e}")

        # Debugging: Print fetched comments count
        print(f"Fetched {len(comments)} comments for post id  {post_id}")
        return comments
        if comments:
            latest_comment_timestamps[post_id] = max(comment['created_utc'] for comment in comments)
    else:
        print(f"Error fetching comments for post {post_id}: {response.status_code}")
    
    return comments

# Load timestamps
load_timestamps()

# Save timestamps after fetching
save_timestamps()
