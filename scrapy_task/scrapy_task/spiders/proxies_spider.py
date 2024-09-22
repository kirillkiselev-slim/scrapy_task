import base64
import json
import logging
from http.cookies import SimpleCookie

import requests
import scrapy
from dotenv import load_dotenv
from scrapy.http import Response, Request

from .constants import (BASE_URL, UPLOAD_URL, BATCH_SIZE, PAYLOAD_POST_PROXIES,
                        HEADERS_GET_TOKEN, TOKEN_URL, TOKEN, PAGES_TO_SCRAPE)

load_dotenv()


class ProxiesScrapy(scrapy.Spider):
    name = 'proxies'

    proxies = []
    batches = None
    possible_batches = None
    current_batch_index = 0

    def start_requests(self):
        urls = [BASE_URL]
        for url in urls:
            yield scrapy.Request(
                url, meta={'proxy': self.settings.get('PROXY')})

    def parse(self, response: Response, page: int = 1, **kwargs):
        for row in response.css('#proxy_list tbody tr'):
            script_text = row.css('td.left script::text').get()
            port = row.css('td span.fport::text').get()
            if script_text is None or port is None:
                continue

            ip_encoded = script_text.split('"')[1]
            decoded_ip = base64.b64decode(ip_encoded).decode()
            self.proxies.append(f'{decoded_ip}:{port}')

        if page < PAGES_TO_SCRAPE:
            next_page_url = f'{BASE_URL}/proxylist/main/{page + 1}'
            yield scrapy.Request(
                next_page_url, callback=self.parse, cb_kwargs={'page': page + 1},
                meta={'proxy': self.settings.get('PROXY')})
        else:
            self.possible_batches = len(self.proxies) // BATCH_SIZE
            yield from self.upload_proxies_by_batch(proxies=self.proxies)

    def parse_token_response(self, response: Response, batch=None):
        if response.status != 200:
            self.log(
                f'Cannot get token from "{TOKEN_URL}"')

        set_cookie_header = response.headers.get('Set-Cookie')
        cookie = SimpleCookie(set_cookie_header.decode('utf-8'))
        form_token = cookie.get('form_token').value
        yield from self.upload_proxies(form_token=form_token, batch=batch)

    def upload_proxies(self, batch=None, form_token=None):
        if form_token is None:
            self.log(f'Form token is missing.', level=logging.CRITICAL)

        payload = PAYLOAD_POST_PROXIES.copy()
        payload.update({'len': len(batch), 'proxies': ', '.join(batch)})
        headers = HEADERS_GET_TOKEN.copy()
        headers['Cookie'] = f'x-user_id={TOKEN}; form_token={form_token}'
        body = json.dumps(payload).encode('utf-8')

        with open('proxies_batches.txt', 'a') as f:
            f.write(f'TOKEN: {form_token}, proxies: {batch}\n')

        yield Request(
            url=UPLOAD_URL, method='POST', body=body, headers=headers,
            callback=self.handle_proxies_response,
            cb_kwargs={'proxies': batch},
            meta={'proxy': self.settings.get('PROXY')},
            dont_filter=True
        )

    def upload_proxies_by_batch(self, proxies=None):
        if proxies is None:
            self.log(f'Proxies are missing.', level=logging.CRITICAL)

        self.batches = [proxies[i: i + BATCH_SIZE]
                        for i in range(0, len(proxies), BATCH_SIZE)]
        yield from self.process_next_batch()

    def process_next_batch(self):
        print(self.possible_batches, self.current_batch_index)
        if self.current_batch_index <= self.possible_batches:
            batch = self.batches[self.current_batch_index]
            self.current_batch_index += 1
            yield scrapy.Request(
                url=TOKEN_URL,
                callback=self.parse_token_response,
                cb_kwargs={'batch': batch},
                meta={'proxy': self.settings.get('PROXY')},
                dont_filter=True,
            )

    def handle_proxies_response(self, response: Response, proxies: list):
        print(response.text)
        if response.status == 200:
            save_id = json.loads(response.body).get('save_id')
            yield {
                save_id: proxies
            }
            self.log(f'Proxies uploaded successfully. Save ID: {save_id}',
                     level=logging.DEBUG)
            yield from self.process_next_batch()
        else:

            self.log(f'Failed to upload proxies: {response.status}',
                     level=logging.CRITICAL)

    def handle_upload_error(self, failure):
        self.log(f'Failed to upload proxies: {failure}',
                 level=logging.CRITICAL)

    def closed(self, reason):
        start_time = self.crawler.stats.get_value('start_time')
        finish_time = self.crawler.stats.get_stats()
        print(finish_time)
        # with open('time.txt', 'a') as file:
        #     result = (finish_time - start_time).strftime('%H:%M:%S')
        #     file.write(f'{result}\n')
