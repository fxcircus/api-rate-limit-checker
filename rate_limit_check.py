import requests
import concurrent.futures
import time
import os
from dotenv import load_dotenv

load_dotenv()

TOTAL_REQUESTS = 1001  # Total number of requests to be made
CONCURRENCY_LEVEL = 1  # Number of concurrent threads for making requests
CLIENT_ID = os.getenv('CLIENT_ID')  # Client ID for authentication
SECRET = os.getenv('SECRET')  # Secret key for authentication
BASE_URL = 'https://api.frontegg.com'  # Base URL for the API
ENDPOINT_TO_CHECK = '/identity/resources/users/v2'  # Specific API endpoint to check rate limits
PRINT_STATUS_FOR_EACH_REQUEST = True  # Control printing status for each request

# Function to get vendor token
def get_vendor_token():
    # Edit the vendor token endpoint as needed
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json'
    }
    data = {
        'clientId': CLIENT_ID,
        'secret': SECRET
    }
    vendor_url = f"{BASE_URL}/auth/vendor/"
    response = requests.post(vendor_url, headers=headers, json=data)
    response.raise_for_status()  # Raise an error for bad responses
    token = response.json().get('token')  # Correct key for token retrieval
    print(f"Retrieved Token: {token}")  # Log the token for verification
    return token

AUTHORIZATION = f'Bearer {get_vendor_token()}'
digit_count = len(str(TOTAL_REQUESTS)) # Calculate the number of digits needed for formatting request numbers
completed_requests = 0
failed_requests = 0
non_2xx_responses = 0
print(f"Starting rate limit check at {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Function to check rate limits on a given endpoint
def check_rate_limits_on_endpoint():
    global completed_requests, failed_requests, non_2xx_responses
    headers = {
        'Authorization': AUTHORIZATION
    }
    url = f"{BASE_URL}{ENDPOINT_TO_CHECK}"
    try:
        response = requests.get(url, headers=headers)
        request_number = completed_requests + 1
        if PRINT_STATUS_FOR_EACH_REQUEST:
            print(f"Request #{request_number:0{digit_count}}: {url} - Status Code: {response.status_code}")
        if response.status_code != 200:
            non_2xx_responses += 1
        completed_requests += 1
        if completed_requests % 100 == 0:
            print(f'Completed {completed_requests} requests')
    except Exception as e:
        failed_requests += 1
        if PRINT_STATUS_FOR_EACH_REQUEST:
            print(f"Request #{completed_requests + 1:0{digit_count}}: {url} - Failed with exception: {e}")

def main():
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY_LEVEL) as executor:
        futures = [executor.submit(check_rate_limits_on_endpoint) for _ in range(TOTAL_REQUESTS)]
        concurrent.futures.wait(futures)
    
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\nFinished {TOTAL_REQUESTS} requests")
    print(f"Time taken for tests: {elapsed_time:.3f} seconds")
    print(f"Complete requests: {completed_requests}")
    print(f"Failed requests: {failed_requests}")
    print(f"Non-2xx responses: {non_2xx_responses}")
    print(f"Requests per second: {completed_requests / elapsed_time:.2f} [#/sec]")
    print(f"Time per request: {elapsed_time / completed_requests * 1000:.3f} [ms] (mean)")
    print(f"Time per request: {elapsed_time / TOTAL_REQUESTS * 1000:.3f} [ms] (mean, across all concurrent requests)")
    print(f"Transfer rate: {completed_requests * 799 / 1024 / elapsed_time:.2f} [Kbytes/sec] received")
    print("\nRate limit check completed.")

if __name__ == "__main__":
    main()
