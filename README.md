# Rate Limit Check Script

This script is designed to test the rate limits of a specified API endpoint by making a large number of requests concurrently. It uses the `requests` library to send HTTP requests and the `concurrent.futures` module to manage concurrency.

## Features
- Sends a specified number of requests to an API endpoint.
- Uses a specified level of concurrency to manage request threads.
- Authenticates using a vendor token obtained from the Frontegg API.
- Reports on the number of completed, failed, and non-2xx responses.

## Setup

1. **Install Dependencies**
   
   Make sure you have Python installed. Then, install the required packages using pip:
   ```bash
   pip install requests python-dotenv
   ```

   **Required Packages:**
   - `requests`: For making HTTP requests.
   - `python-dotenv`: For loading environment variables from a `.env` file.

2. **Environment Variables**

   Create a `.env` file in the root directory and add your `CLIENT_ID` and `SECRET`:
   ```
   CLIENT_ID=your_client_id_here
   SECRET=your_secret_here
   ```

3. **Run the Script**

   Execute the script using Python:
   ```bash
   python3 rate_limit_check.py
   ```

The script will output the results of the rate limit test, including the time taken, number of completed requests, and any failed or non-2xx responses. 