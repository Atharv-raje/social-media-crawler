# Social Media Data Collection System

This project implements an automated data collection system that crawls and stores data from Reddit and 4chan. The system includes separate crawlers for each platform, database integration, and scheduled data collection.

## System Architecture

The system consists of several key components:
1. Reddit Crawler
2. 4chan Crawler
3. PostgreSQL Database Integration
4. Scheduled Task Management

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database:
   - Create a new database named 'postgres'
   - Create necessary schemas and tables (scripts provided in project)

5. Configure environment variables:
Create a `.env` file in the root directory with the following variables:
```
DB_HOST=localhost
DB_NAME=postgres
DB_USER=your_username
DB_PASSWORD=your_password
DB_PORT=5432

REDDIT_CLIENT_ID=your_client_id
REDDIT_SECRET=your_secret
REDDIT_USER_AGENT=your_user_agent
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
```

## Component Overview

### 1. Reddit Crawler (reddit_crawler.py, reddit_client.py)

The Reddit crawler consists of two main components:

- `reddit_client.py`: Handles Reddit API authentication and data fetching
  - Uses OAuth2 authentication
  - Manages token expiration and renewal
  - Fetches posts and comments from specified subreddits

- `reddit_crawler.py`: Manages data processing and storage
  - Creates necessary database tables
  - Processes and stores posts and comments
  - Handles duplicate prevention
  - Maintains data consistency

### 2. 4chan Crawler (chan_crawler.py, chan_client.py)

The 4chan crawler includes:

- `chan_client.py`: Manages 4chan API interactions
  - Handles API requests
  - Implements error handling and logging
  - Fetches thread and catalog data

- `chan_crawler.py`: Processes and stores 4chan data
  - Implements scheduled crawling
  - Manages database connections
  - Handles data insertion and updates

### 3. Database Integration (db_connector.py)

The database connector:
- Manages PostgreSQL connections
- Implements connection pooling
- Handles connection errors and retries
- Provides a unified interface for all database operations

### 4. Scheduler (schedule_worker.py)

The scheduler:
- Manages crawling schedules for both platforms
- Implements configurable intervals
- Handles task queuing and execution
- Provides logging and monitoring

## Database Schema

### Reddit Tables

```sql
CREATE TABLE reddit_posts (
    id VARCHAR PRIMARY KEY,
    title TEXT,
    body TEXT,
    created_utc TIMESTAMP,
    score INT,
    url TEXT,
    subreddit VARCHAR
);

CREATE TABLE reddit_comments (
    id VARCHAR PRIMARY KEY,
    post_id VARCHAR REFERENCES reddit_posts(id),
    body TEXT,
    created_utc TIMESTAMP,
    score INT
);
```

### 4chan Tables

```sql
CREATE TABLE chanposts (
    post_id BIGINT PRIMARY KEY,
    name VARCHAR,
    comment TEXT,
    filename VARCHAR,
    ext VARCHAR,
    w INT,
    h INT,
    time BIGINT,
    resto BIGINT
);
```

## Usage

1. Start the Reddit crawler:
```bash
python schedule_worker.py
```

2. Start the 4chan crawler:
```bash
python chan_crawler.py
```

The system will automatically:
- Collect data from specified subreddits every 5 minutes
- Collect data from specified 4chan boards every 10 minutes
- Store all data in the PostgreSQL database
- Handle errors and retries automatically

## Monitoring and Logging

The system implements comprehensive logging:
- All API requests are logged
- Database operations are tracked
- Errors are captured with stack traces
- Execution times are monitored

Logs can be found in the application's output and can be configured to write to files.

## Error Handling

The system implements robust error handling:
- API rate limiting management
- Network error recovery
- Database connection retry logic
- Data validation and sanitization

## Security Considerations

- API credentials are stored in environment variables
- Database passwords are never hardcoded
- Input data is sanitized before storage
- API rate limits are respected

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
