import base64
import json


import scrapy
from dotenv import load_dotenv
from scrapy.http import Response, Request

from .constants import BASE_URL, TOKEN, UPLOAD_URL, BATCH_SIZE

load_dotenv()


class ProxiesScrapy(scrapy.Spider):
    name = 'proxies'
    proxies = []

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

        if page < 5:
            next_page_url = f'{BASE_URL}/proxylist/main/{page + 1}'
            yield scrapy.Request(
                next_page_url, callback=self.parse, cb_kwargs={'page': page + 1},
                meta={'proxy': self.settings.get('PROXY')})
        else:
            # with open('proxies.txt', 'w') as file:
            #     file.write(f'{self.proxies}\n')
            yield from self.upload_proxies_in_batches(self.proxies)

    def upload_proxies_in_batches(self, proxies=None):
        if proxies is None:
            self.log(f'Proxies have not been scraped from "{BASE_URL}')
        for i in range(0, len(proxies), BATCH_SIZE):
            batch = proxies[i:i + BATCH_SIZE]
            self.upload_proxies(batch)

    def upload_proxies(self, batch):
        payload = {
            'token': TOKEN,
            'proxies': ', '.join(batch).strip()
        }
        with ('payload.txt', 'w') as file:
            file.write(f'{payload}\n')
        body = json.dumps(payload).encode('utf-8')

        yield Request(
            url=UPLOAD_URL,
            method='POST',
            body=body,
            callback=self.handle_proxies_response,
            cb_kwargs={'proxies': batch},
            errback=self.handle_upload_error
        )

    def handle_proxies_response(self, response: Response, proxies: str):
        if response.status == 200:
            save_id = json.loads(response.body).get('save_id')
            yield {
                save_id: proxies.split(', ')
            }
            self.log(f'Proxies uploaded successfully. Save ID: {save_id}')
        else:
            self.log(f'Failed to upload proxies: {response.status}')

    def handle_upload_error(self, failure):
        self.log(f'Failed to upload proxies: {failure}')
