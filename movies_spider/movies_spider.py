import time
import re
import csv
import requests
from bs4 import BeautifulSoup

class Request:
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = self.headers

    def get(self, url):
        return self.session.get(url)

class Spider:
    base_url = f'https://movie.douban.com/top250'

    def __init__(self):
        self.req = Request()
        self.movies = [['title', 'rating', 'comments_count', 'comments_top5']]

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for item in soup.find_all('div', attrs={'class': 'item'}):
            title = item.find('span', attrs={'class': 'title'}).get_text()
            rating = item.find('span', attrs={'class': 'rating_num'}).get_text()
            comment_info = item.find('div', attrs={'class': 'star'}).find_all('span')[-1].get_text()
            comments_count = re.findall(r'\d+', comment_info)[0]

            movie_url = item.find('div', attrs={'class': 'hd'}).find('a').get('href')
            comments_resp = self.req.get(f'{movie_url}comments')
            comment_soup = BeautifulSoup(comments_resp.text, 'html.parser')

            comments_top5 = []
            for comment in comment_soup.find_all('div', attrs={'class': 'comment-item'})[:5]:
                content = comment.find('span', attrs={'class':'short'}).get_text()
                comments_top5.append(content)

            self.movies.append([title, rating, comments_count, comments_top5])

    def run(self):
        for page in range(10):
            response = self.req.get(f'{self.base_url}?start={page*25}')
            self.parse(response)
            time.sleep(2)

        with open('movies_data.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.movies)

spider = Spider()
spider.run()
