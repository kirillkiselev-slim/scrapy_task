import base64
import json
import logging
from http.cookies import SimpleCookie

import requests
import scrapy
from dotenv import load_dotenv
from scrapy.http import Response, Request

from .constants import (BASE_URL, UPLOAD_URL, BATCH_SIZE,
                        PAYLOAD_POST_PROXIES, HEADERS_GET_TOKEN, TOKEN_URL, TOKEN)

load_dotenv()


class ProxiesScrapy(scrapy.Spider):
    name = 'proxies'
    proxies = []
    old_form_token = None

    def start_requests(self):
        urls = [BASE_URL]
        for url in urls:
            yield scrapy.Request(
                url, meta={'proxy': self.settings.get('PROXY')})

    def parse(self, response: Response, page: int = 1, **kwargs):
        for row in response.css('#proxy_list tbody tr'):
            script_text = row.css('td.left script::text').get()
            port = row.css('td span.fport::text').get()
            if script_text is None and port is None:
                continue

            ip_encoded = script_text.split('"')[1]
            decoded_ip = base64.b64decode(ip_encoded).decode()
            self.proxies.append(f'{decoded_ip}:{port}')

        # if page < 5:
        #     next_page_url = f'{BASE_URL}/proxylist/main/{page + 1}'
        #     yield scrapy.Request(
        #         next_page_url, callback=self.parse, cb_kwargs={'page': page + 1},
        #         meta={'proxy': self.settings.get('PROXY')})
        # elif page == 5:
        return self.get_token()

    def get_token(self):
        return Request(
            url=TOKEN_URL,
            method='GET',
            callback=self.parse_token_response
        )

    def get_new_token(self):
        response = requests.get(TOKEN_URL)
        return response.headers

    def parse_token_response(self, response: Response):
        if response.status != 200:
            self.log(
                f'Cannot get token from "{TOKEN_URL}"')

        set_cookie_header = response.headers.get('Set-Cookie')
        cookie = SimpleCookie(set_cookie_header.decode('utf-8'))
        form_token = cookie.get('form_token').value
        yield from self.upload_proxies(proxies=self.proxies,
                                       form_token=form_token)

    def upload_proxies(self, proxies=None, form_token=None):
        if proxies is None:
            self.log(f'Proxies are missing.', level=logging.CRITICAL)
        if form_token is None:
            self.log(f'Form token is missing.', level=logging.CRITICAL)
        # for i in range(0, len(proxies), BATCH_SIZE):
        batch = proxies[0:0 + BATCH_SIZE]

        headers = HEADERS_GET_TOKEN.copy()
        headers['Cookie'] = f'x-user_id={TOKEN}; form_token={form_token}'

        payload = PAYLOAD_POST_PROXIES.copy()
        payload.update({'len': len(batch), 'proxies': ', '.join(batch)})

        body = json.dumps(payload).encode('utf-8')

        yield Request(
            url=UPLOAD_URL,
            method='POST',
            body=body,
            headers=headers,
            callback=self.handle_proxies_response,
            cb_kwargs={'proxies': batch},
        )


            # self.old_form_token = form_token
            # form_token = self.get_token()

            # if form_token == self.old_form_token:
            #     print('Old token is the new token')

    def handle_proxies_response(self, response: Response, proxies: list):
        print(response.text)
        if response.status == 200:
            save_id = json.loads(response.body).get('save_id')
            yield {
                save_id: proxies
            }
            self.log(f'Proxies uploaded successfully. Save ID: {save_id}',
                     level=logging.DEBUG)
        else:

            self.log(f'Failed to upload proxies: {response.status}',
                     level=logging.CRITICAL)

    def handle_upload_error(self, failure):
        self.log(f'Failed to upload proxies: {failure}',
                 level=logging.CRITICAL)
