import logging
import requests

# Logger setup
logger = logging.getLogger("4chan client")
logger.propagate = False
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)
logger.addHandler(sh)

class ChanClient:
    API_BASE = "http://a.4cdn.org"

    """
    Get JSON data for a given thread
    """
    def get_thread(self, board, thread_number):
        try:
            # Sample API call: http://a.4cdn.org/fit/thread/12345678.json
            request_pieces = [board, "thread", f"{thread_number}.json"]
            api_call = self.build_request(request_pieces)
            return self.execute_request(api_call)
        except Exception as e:
            logger.error(f"Error fetching thread {thread_number} from board {board}: {e}")
            return None

    """
    Get catalog JSON data for a given board
    """
    def get_catalog(self, board):
        try:
            #Sample API call: http://a.4cdn.org/fit/catalog.json
            request_pieces = [board, "catalog.json"]
            api_call = self.build_request(request_pieces)
            return self.execute_request(api_call)
        except Exception as e:
            logger.error(f"Error fetching catalog for board {board}: {e}")
            return None

    """
    Build the API request URL from pieces
    """
    def build_request(self, request_pieces):
        api_call = "/".join([self.API_BASE] + request_pieces)
        return api_call

    """
    Execute the HTTP request and return JSON response
    """
    def execute_request(self, api_call):
        try:
            logger.info(f"Making API call: {api_call}")
            resp = requests.get(api_call)
            resp.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
            
            json_data = resp.json()  # Parse JSON response
            logger.info(f"Response status: {resp.status_code}")
            logger.info(f"Fetched JSON data: {json_data}")
            return json_data
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            return None
        except ValueError as e:
            logger.error(f"Error parsing JSON: {e}")
            return None

if __name__ == "__main__":
    client = ChanClient()
    
  
