from multiprocessing import cpu_count
from multiprocessing.dummy import Pool

import discord
import requests
from bs4 import BeautifulSoup


class Scraper:
    def scrape_url(self, url):
        response = requests.get(url)
        return self.check_response(response)

    def check_response(self, response):
        if 200 <= response.status_code <= 299:
            return response
        else:
            raise f"Something went wrong - Status code: {response.status_code}"


class Darklegacy(Scraper):
    def __init__(self):
        self.base_url = 'https://www.darklegacycomics.com'

    def _get_metadata(self):
        archive_url = f'{self.base_url}/archive'
        content = self.scrape_url(archive_url).content
        parser = BeautifulSoup(content, 'html.parser')
        comic_blocks = parser.find_all('div', {'class': 'archive_link'})

        comics = []
        for block in comic_blocks:
            index = block.find('span', {'class', 'index'})
            name = block.find('span', {'class', 'name'})
            date = block.find('span', {'class', 'date'})
            characters = block.find('span', {'class', 'characters'})
            tags = block.find('span', {'class', 'tags'})
            comic = {
                'index': index.text,
                'name': name.text,
                'date': date.text.replace(' c', ''),
                'characters': characters.text,
                'tags': tags.text,
                'url': f'{self.base_url}/{index.text}'
            }
            if comic not in comics:
                comics.append(comic)
        return comics

    def _add_comic_url(self, comic):
        content = self.scrape_url(comic['url']).content
        parser = BeautifulSoup(content, 'html.parser')
        blocks = parser.find_all('div', {'class': 'comic'})
        urls = [f'{self.base_url}/{b.find("img")["src"]}' for b in blocks]
        if len(urls) == 1:
            comic['img_src'] = urls[0]
        return comic

    def embed(self, comic):
        content = discord.Embed(url=comic['url'])
        content.add_field(
            name='Issue',
            value=comic['index'],
        )
        content.add_field(
            name='Title',
            value=comic['name'],
        )
        content.add_field(
            name='Date',
            value=comic['date'],
        )
        content.add_field(
            name='Characters',
            value=comic['characters'],
        )
        content.add_field(
            name='URL',
            value=comic['url'],
        )
        content.add_field(
            name='Tags',
            value=comic['tags'],
            inline=False
        )
        content.set_image(url=comic['img_src'])
        return content

    def get_latest_comic(self):
        comic = self._get_metadata()[-1]
        comic = self._add_comic_url(comic)
        return comic

    def get_all_comics(self):
        comics = self._get_metadata()
        pool = Pool(cpu_count())
        pool.map(self._add_comic_url, comics)
        return comics
