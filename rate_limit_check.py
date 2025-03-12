import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

TOTAL_REQUESTS = 1001  # Total number of requests to be made
CLIENT_ID = os.getenv('CLIENT_ID')  # Client ID for authentication
SECRET = os.getenv('SECRET')  # Secret key for authentication
BASE_URL = 'https://api.frontegg.com'  # Base URL for the API
ENDPOINT_TO_CHECK = '/identity/resources/users/v2'  # Specific API endpoint to check rate limits
PRINT_STATUS_FOR_EACH_REQUEST = True  # Control printing status for each request

completed_requests = 0
failed_requests = 0
non_2xx_responses = 0

def get_vendor_token():
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
    token = response.json().get('token')
    print(f"Retrieved Token:\n{token}\n")
    return token

AUTHORIZATION = f'Bearer {get_vendor_token()}'
digit_count = len(str(TOTAL_REQUESTS))
print(f"Starting rate limit check at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

def check_rate_limits_on_endpoint():
    global completed_requests, failed_requests, non_2xx_responses
    headers = {'Authorization': AUTHORIZATION}
    url = f"{BASE_URL}{ENDPOINT_TO_CHECK}"
    
    try:
        response = requests.get(url, headers=headers)
        request_number = completed_requests + 1
        if PRINT_STATUS_FOR_EACH_REQUEST:
            print(f"Request #{request_number:0{digit_count}}: {url} - Status Code: {response.status_code}")
        
        # If a 429 (Too Many Requests) is received, exit the loop.
        if response.status_code == 429:
            non_2xx_responses += 1
            print("429 received. Breaking out of the loop.")
            return False
        
        if response.status_code != 200:
            non_2xx_responses += 1
            print(f"Non-200 response received: {response.status_code}.")
            # You can choose to continue on other non-200 responses if needed.
        
        completed_requests += 1
        if completed_requests % 100 == 0:
            print(f"Completed {completed_requests} requests")
    except Exception as e:
        failed_requests += 1
        print(f"Request #{completed_requests + 1:0{digit_count}}: {url} - Failed with exception: {e}")
    return True

def main():
    start_time = time.time()
    for _ in range(TOTAL_REQUESTS):
        if not check_rate_limits_on_endpoint():
            break
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\nFinished {completed_requests} successful requests")
    print(f"Time taken: {elapsed_time:.3f} seconds")
    print(f"Successful requests: {completed_requests}")
    print(f"Failed requests: {failed_requests}")
    print(f"Non-200 responses: {non_2xx_responses}")
    if elapsed_time > 0 and completed_requests > 0:
        print(f"Requests per second: {completed_requests / elapsed_time:.2f} [#/sec]")
        print(f"Time per successful request: {elapsed_time / completed_requests * 1000:.3f} [ms] (mean)")
        print(f"Time per attempted request: {elapsed_time / TOTAL_REQUESTS * 1000:.3f} [ms] (mean)")
        print(f"Transfer rate: {completed_requests * 799 / 1024 / elapsed_time:.2f} [Kbytes/sec] received")
    print("\nRate limit check completed.")

if __name__ == "__main__":
    main()
