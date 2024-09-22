import os

BASE_URL = 'http://free-proxy.cz/en'
TOKEN = os.getenv('TOKEN')
UPLOAD_URL = 'https://test-rg8.ddns.net/api/post_proxies'
TOKEN_URL = 'https://test-rg8.ddns.net/api/get_token'
BATCH_SIZE = 30
PAYLOAD_POST_PROXIES = {
    'user_id': TOKEN,
}
HEADERS_GET_TOKEN = headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'Content-Type': 'application/json',
}
PAGES_TO_SCRAPE = 5
