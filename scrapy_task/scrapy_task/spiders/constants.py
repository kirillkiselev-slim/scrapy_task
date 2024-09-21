import os

USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
              ' AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/128.0.6613.114 Safari/537.36')
BASE_URL = 'http://free-proxy.cz/en'
TOKEN = os.getenv('TOKEN')
UPLOAD_URL = 'https://test-rg8.ddns.net/api/post_proxies'
TOKEN_URL = 'https://test-rg8.ddns.net/api/get_token'
BATCH_SIZE = 10
PAYLOAD_POST_PROXIES = {
    'user_id': TOKEN,
}
HEADERS_GET_TOKEN = headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'Content-Type': 'application/json',
}
