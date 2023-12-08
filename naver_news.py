import datetime
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup as BS
from tqdm import tqdm


class NaverNewsCrawler:
    def __init__(self):
        super().__init__()

    def _crawl(self, url: str) -> BS:
        """
        Given a url, return the BeautifulSoup object.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/39.0.2171.95 Safari/537.36"
        }
        try:
            res = requests.get(url, headers=headers)
        except:
            time.sleep(300)
            res = requests.get(url, headers=headers)
        soup = BS(res.text, features="html.parser")
        return soup

    def get_urls(self, keyword: str, start_date: str, end_date: str) -> set[str]:
        """
        Return result as dictionary
        start_date and end_date must be in the format of YYYY.MM.DD
        i.e. 2022-04-25
        """
        print("Collecting news url list")
        date_list = list(
            map(
                lambda x: x.strftime("%Y.%m.%d"),
                pd.date_range(start=start_date, end=end_date),
            )
        )
        urls = set()

        # iterate over date list
        # naver provides maximum 400 pages for each date
        last_page = 400
        for date in date_list:
            print(f"Start crawling for {date}, current url: {len(urls)}", end="\r")

            url_count = 0
            for page in range(0, last_page + 1):
                page_url = (
                    "https://search.naver.com/search.naver?"
                    f"where=news&sm=tab_jum&query={keyword}"
                    f"&ds={date}&de={date}&start={page * 10 + 1}"
                    f"&nso=so%3Ar%2Cp%3Afrom{date.replace('.','')}"
                    f"to{date.replace('.','')}"
                )

                soup = self._crawl(page_url)

                if "검색결과가 없습니다" in soup.text:
                    break

                for article in soup.find_all("a"):
                    if article.text == "네이버뉴스" and "sports" not in article["href"]:
                        urls.add(article["href"])
                        url_count += 1

                last_page_elem = soup.select_one(
                    "#main_pack > div.api_sc_page_wrap > div > a.btn_next"
                )
                if last_page_elem is None or (
                    last_page_elem["aria-disabled"] == "true"
                ):
                    break
                time.sleep(10)
            time.sleep(10)
        return urls

    def _get_news_data(self, url: str) -> dict:
        """
        Return single news data as a dictionary.
        The dict has the following keys: url, text, title, and media.
        """
        soup = self._crawl(url)

        body_selector = "#newsct_article"
        tag = soup.select_one(body_selector)

        if tag is None:
            return {}
        body_text = tag.text.strip().replace("\n", "").replace("\t", "")

        title_selector = (
            "#ct > div.media_end_head.go_trans > div.media_end_head_title > h2"
        )
        title = soup.select_one(title_selector).text

        media = soup.select_one(
            "#ct > div.media_end_head.go_trans > div.media_end_head_top > a > img.media_end_head_top_logo_img.light_type"
        )["title"]
        date = soup.select_one(
            "#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div:nth-child(1) > span"
        )["data-date-time"]

        return {
            "url": url,
            "text": body_text,
            "title": title,
            "media": media,
            "date": datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime(
                "%Y-%m-%d"
            ),
        }

    def run(self, keyword: str, start_date: str, end_date: str) -> pd.DataFrame | None:
        """
        From the set of urls, scraping news data and return a pandas dataframe.
        First, scrape urls for each date. Second, iterate over urls to get data.

        Raise:
            ValueError: if the set of urls is empty.
            Exception: if unknown excpetion occurs.
        """

        self.urls = self.get_urls(keyword, start_date, end_date)

        with open(f"{keyword}_urls_{start_date}_{end_date}.txt", "w") as f:
            for url in self.urls:
                f.write(f"{url}\n")

        # with open("마이데이터_urls_2017-06-19_2023-07-30.txt", "r") as f:
        #     self.urls = set(f.readlines())

        print(f"Crawling started from collected {len(self.urls)} urls")

        self.data = []
        urls = list(self.urls)
        pbar = tqdm(total=len(urls))
        while urls:
            url = urls.pop()
            _data = self._get_news_data(url)
            if _data:
                self.data.append(_data)
                pbar.update(1)
            else:
                urls.append(url)
            print(f"Progress: {len(self.data)} / {len(self.urls)}", end="\r")
            time.sleep(10)

        print("Crawling finished")
        return self.data
