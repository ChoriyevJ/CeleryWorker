# feedback/forms.py
import logging
import os
import time
import asyncio
import aiohttp

from bs4 import BeautifulSoup
import requests
import json

logger = logging.getLogger(__name__)

categories = [
    {
        'category': 'nedvizhimost',
        'sub_category': 'kvartiry'
    },
    {
        'category': 'elektronika',
        'sub_category': 'telefony'
    }
]


class Parser:
    def __init__(self, category, sub_category, default=True):
        self.url = 'https://www.olx.uz'
        self.category = category
        self.sub_category = sub_category
        self.default = default

    def get_soup(self, url, page=None):

        if page:
            url = f"{url}/?page={page}"
        try:
            html = requests.get(url).text
            soup = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            raise Exception(e)

        return soup

    def get_json_data(self):
        data: dict = dict()

        url: str = f"{self.url}/{self.category}/{self.sub_category}"
        total_pages: str = self.get_total_pages(soup=self.get_soup(url))
        print("total_pages =", total_pages)
        if total_pages.isdigit():
            total_pages = int(total_pages)
        else:
            raise Exception("Page number must be an integer")

        for page_number in range(1, total_pages + 1):
            page_data = self.get_page_data(page_number, url=url)
            data[f'page_{page_number}'] = page_data
        return data

    def get_page_data(self, page_number: int, url: str) -> tuple:
        page_data: list = []

        soup = self.get_soup(url=url, page=page_number)
        list_card = soup.find_all('div', attrs={'data-cy': 'l-card'})

        for index, card in enumerate(list_card):
            try:
                card = card.div.div.find_all('div', attrs={'type': 'list'})
                link = self.url + card[0].a['href']
                images = self.get_images(link)
                title = card[2].div.a.h6.get_text(strip=True)
                price = ''.join(tuple(card[2].div.p.get_text(strip=True).split(' ')[:-1]))
            except Exception as e:
                raise Exception(e)
            page_data.append({
                'title': title,
                'price': price,
                'images': images
            })
        return tuple(page_data)

    def get_total_pages(self, soup, page='5') -> str:
        pagination = soup.find_all('li', class_="pagination-item")[-1]
        return pagination.get_text(strip=True) if not self.default else page

    def get_images(self, url: str) -> tuple:
        images = []
        soup = self.get_soup(url)
        image_divs = soup.find_all('div', class_="swiper-zoom-container")
        for index, image_div in enumerate(image_divs):
            try:
                image = image_div.img['src']
                images.append(image)
            except Exception as e:
                raise Exception(f'{e}, index={index + 1}')

        return tuple(images)

    def run(self):
        json_data = self.get_json_data()
        dir_name = 'json_files'
        os.makedirs(f'{dir_name}/', exist_ok=True)
        file_path = f'{self.__class__.__name__}_{self.category}_{self.sub_category}'
        with open(f'{dir_name}/{file_path}.json', mode='w', encoding='utf-8') as json_data_file:
            json.dump(json_data, json_data_file, ensure_ascii=False, indent=4)


class AsyncParser:
    def __init__(self, category, sub_category, default=False):
        self.url = 'https://www.olx.uz'
        self.category = category
        self.sub_category = sub_category
        self.default = default

    async def get_soup(self, url, page=None):
        if page:
            url = f"{url}/?page={page}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            raise Exception(e)

        return soup

    async def get_json_data(self):
        data: dict = dict()

        url = f"{self.url}/{self.category}/{self.sub_category}"
        total_pages: str = await self.get_total_pages(soup=await self.get_soup(url))
        print("total_pages =", total_pages)
        if total_pages.isdigit():
            total_pages = int(total_pages)
        else:
            raise Exception("Page number must be an integer")

        tasks = [self.get_page_data(page_number, url=url) for page_number in range(1, total_pages + 1)]
        page_data = await asyncio.gather(*tasks)
        for page_number, data_per_page in enumerate(page_data, start=1):
            data[f'page_{page_number}'] = data_per_page

        return data

    async def get_page_data(self, page_number: int, url: str) -> tuple:
        page_data: list = []

        soup = await self.get_soup(url=url, page=page_number)
        list_card = soup.find_all('div', attrs={'data-cy': 'l-card'})

        for index, card in enumerate(list_card):
            try:
                card = card.div.div.find_all('div', attrs={'type': 'list'})
                link = self.url + card[0].a['href']
                images = await self.get_images(link)
                title = card[2].div.a.h6.get_text(strip=True)
                price = ''.join(tuple(card[2].div.p.get_text(strip=True).split(' ')[:-1]))
            except Exception as e:
                raise Exception(e)
            page_data.append({
                'title': title,
                'price': price,
                'images': images,
                'link': link,
            })
        return tuple(page_data)

    async def get_total_pages(self, soup, page='5') -> str:
        pagination = soup.find_all('li', class_="pagination-item")[-1]
        return pagination.get_text(strip=True) if not self.default else page

    async def get_images(self, url: str) -> tuple:
        images = []
        soup = await self.get_soup(url)
        image_divs = soup.find_all('div', class_="swiper-zoom-container")

        for index, image_div in enumerate(image_divs):
            try:
                image = image_div.img['src']
                images.append(image)
            except Exception as e:
                raise Exception(f'{e}, index={index + 1}')

        return tuple(images)

    async def run(self):
        json_data = await self.get_json_data()
        dir_name = 'json_files'
        os.makedirs(f'{dir_name}/', exist_ok=True)
        file_path = f'{self.__class__.__name__}_{self.category}_{self.sub_category}'
        with open(f'{dir_name}/{file_path}.json', mode='w', encoding='utf-8') as json_data_file:
            json.dump(json_data, json_data_file, ensure_ascii=False, indent=4)


async def async_main():
    st_time = time.perf_counter()
    parser = AsyncParser(categories[0]['category'], categories[0]['sub_category'], default=False)
    await parser.run()
    end_time = time.perf_counter()
    print(f'Full time: {end_time - st_time} seconds.')


def sync_main():
    st_time = time.perf_counter()
    parser = Parser(categories[0]['category'], categories[0]['sub_category'], default=False)
    parser.run()
    end_time = time.perf_counter()
    print(f'Full time: {end_time - st_time} seconds.')


if __name__ == '__main__':
    # sync_main()
    asyncio.run(async_main())
    # image_url = f"https://frankfurt.apollo.olxcdn.com:443/v1/files/pul4upt3h4f8-UZ/image;s=1488x1984"



