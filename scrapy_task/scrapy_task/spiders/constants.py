import os

USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
              ' AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/128.0.6613.114 Safari/537.36')
BASE_URL = 'http://free-proxy.cz/en'
TOKEN = os.getenv('TOKEN')
UPLOAD_URL = 'https://test-rg8.ddns.net/api/post_proxies'
BATCH_SIZE = 10
