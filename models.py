def create_reddit_table(conn):
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
        conn.commit()