# Scraping task

This is the script to scrape 5 pages of proxy data
from the website called "free-proxy.cz". It then uploads to the website called "test-rg8.ddns.net"
to get save id. The result is saved in "results.json" file and entire script is also timed (time is saved to time.txt).

## Set up

Clone the repository:

```bash
git clone https://github.com/kirillkiselev-slim/foodgram/
```

Create and activate virtual environment:

```bash
python3 -m venv env
```

* If you have Linux/Mac

    ```bash
    source env/bin/activate
    ```

* If you have Windows

    ```bash
    source env/scripts/activate
    ```
#### Update pip
```bash
python3 -m pip install --upgrade pip
```

Download dependencies from requirements.txt:

```bash
cd scrapy_task
```

```bash
pip install -r requirements.txt
```

## Run the scraping script

```bash
scrapy crawl proxies -o results.json
```


### Used technologies

* Python 3.12
* Scrapy 2.11.2

### Author

[Кирилл Киселев](https://github.com/kirillkiselev-slim)
