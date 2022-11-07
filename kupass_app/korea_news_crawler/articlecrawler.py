# -*- coding: utf-8, euc-kr -*-

import platform
import calendar
import requests
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime

from kupass_app.korea_news_crawler.exceptions import *
from kupass_app.korea_news_crawler.articleparser import ArticleParser

from kupass_app.models import Article
from kupass_app.gpus.main_gpus import print_cur_state, text_summary, insert_one_article, get_last_create_date
from kupass_app import db


class ArticleCrawler(object):
    def __init__(self):
        self.categories = {'정치': 100, '경제': 101, '사회': 102, '생활문화': 103, '세계': 104, 'IT과학': 105, '오피니언': 110,
                           'politics': 100, 'economy': 101, 'society': 102, 'living_culture': 103, 'world': 104,
                           'IT_science': 105, 'opinion': 110}
        self.selected_categories = []
        self.date = {'start_year': 0, 'start_month': 0, 'start_day': 0, 'end_year': 0, 'end_month': 0, 'end_day': 0}
        self.user_operating_system = str(platform.system())
        self.last_create_dates = {'politics': None, 'economy': None, 'society': None, 'living_culture': None,
                                  'world': None, 'IT_science': None, 'opinion': None}
        print_cur_state(f'ArticleCrawler() has been created.')

    def set_last_create_date(self, category, last_create_date: datetime):
        self.last_create_dates[category] = last_create_date

    def set_category(self, *args):
        for key in args:
            if self.categories.get(key) is None:
                raise InvalidCategory(key)
        self.selected_categories = args

    def set_date_range(self, start_date: str, end_date: str):
        start = list(map(int, start_date.split("-")))
        end = list(map(int, end_date.split("-")))

        # Setting Start Date
        if len(start) == 1:  # Input Only Year
            start_year = start[0]
            start_month = 1
            start_day = 1
        elif len(start) == 2:  # Input Year and month
            start_year, start_month = start
            start_day = 1
        elif len(start) == 3:  # Input Year, month and day
            start_year, start_month, start_day = start

        # Setting End Date
        if len(end) == 1:  # Input Only Year
            end_year = end[0]
            end_month = 12
            end_day = 31
        elif len(end) == 2:  # Input Year and month
            end_year, end_month = end
            end_day = calendar.monthrange(end_year, end_month)[1]
        elif len(end) == 3:  # Input Year, month and day
            end_year, end_month, end_day = end

        args = [start_year, start_month, start_day, end_year, end_month, end_day]

        if start_year > end_year:
            raise InvalidYear(start_year, end_year)
        if start_month < 1 or start_month > 12:
            raise InvalidMonth(start_month)
        if end_month < 1 or end_month > 12:
            raise InvalidMonth(end_month)
        if start_day < 1 or calendar.monthrange(start_year, start_month)[1] < start_day:
            raise InvalidDay(start_day)
        if end_day < 1 or calendar.monthrange(end_year, end_month)[1] < end_day:
            raise InvalidDay(end_day)
        if start_year == end_year and start_month > end_month:
            raise OverbalanceMonth(start_month, end_month)
        if start_year == end_year and start_month == end_month and start_day > end_day:
            raise OverbalanceDay(start_day, end_day)

        for key, date in zip(self.date, args):
            self.date[key] = date
        print(self.date)

    @staticmethod
    def make_news_page_url(category_url, date):
        made_urls = []
        for year in range(date['start_year'], date['end_year'] + 1):
            if date['start_year'] == date['end_year']:
                target_start_month = date['start_month']
                target_end_month = date['end_month']
            else:
                if year == date['start_year']:
                    target_start_month = date['start_month']
                    target_end_month = 12
                elif year == date['end_year']:
                    target_start_month = 1
                    target_end_month = date['end_month']
                else:
                    target_start_month = 1
                    target_end_month = 12

            for month in range(target_start_month, target_end_month + 1):
                if date['start_month'] == date['end_month']:
                    target_start_day = date['start_day']
                    target_end_day = date['end_day']
                else:
                    if year == date['start_year'] and month == date['start_month']:
                        target_start_day = date['start_day']
                        target_end_day = calendar.monthrange(year, month)[1]
                    elif year == date['end_year'] and month == date['end_month']:
                        target_start_day = 1
                        target_end_day = date['end_day']
                    else:
                        target_start_day = 1
                        target_end_day = calendar.monthrange(year, month)[1]

                for day in range(target_start_day, target_end_day + 1):
                    if len(str(month)) == 1:
                        month = "0" + str(month)
                    if len(str(day)) == 1:
                        day = "0" + str(day)

                    # 날짜별로 Page Url 생성
                    url = category_url + str(year) + str(month) + str(day)

                    # totalpage는 네이버 페이지 구조를 이용해서 page=10000으로 지정해 totalpage를 알아냄
                    # page=10000을 입력할 경우 페이지가 존재하지 않기 때문에 page=totalpage로 이동 됨 (Redirect)
                    totalpage = ArticleParser.find_news_totalpage(url + "&page=10000")
                    for page in range(1, totalpage + 1):
                        made_urls.append(url + "&page=" + str(page))
        return made_urls

    @staticmethod
    def get_url_data(url, max_tries=5):
        remaining_tries = int(max_tries)
        while remaining_tries > 0:
            try:
                return requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            except requests.exceptions:
                sleep(1)
            remaining_tries -= 1
        raise ResponseTimeout()

    @staticmethod
    def is_valanced_content(content):
        return content.count("'") % 2 == 0

    def refine_content(self, content):
        content = content.replace("'' ", "").replace("' '", " ")
        if not self.is_valanced_content(content):
            return content[1:]
        return content

    def get_article_from_url(self, url_category, post_url, is_finished):
        print_cur_state(f"'{url_category}':", end=' ')
        print_cur_state(f'{post_url}')

        # 기사 HTML 가져옴
        request_content = self.get_url_data(post_url)

        try:
            document_content = BeautifulSoup(request_content.content, 'html.parser')
        except Exception:
            print_cur_state(f'document_content is None')
            return None
        try:
            # 기사 제목 가져옴
            tag_headline = document_content.find_all('h2', {'class': 'media_end_head_headline'})
            # print_cur_state(f"tag_headline's type: {type(tag_headline)}, len: {len(tag_headline)}")
            if len(tag_headline) < 1:
                print_cur_state(f'len(tag_headline) = 0', end='\n')
                return None
            # 뉴스 기사 제목 초기화
            title = ArticleParser.clear_headline(str(tag_headline[0].find_all(string=True)))
            # 공백일 경우 기사 제외 처리
            if not isinstance(title, str) or title is None:
                print_cur_state(f'title is None', end='\n')
                # print(tag_headline, add, type(add), sep=', ')
                return None
#            print_cur_state(f'title: "{title}"')
            # <div class="go_trans _article_content" id="dic_area">

            # 기사 본문 가져옴
            tag_content = document_content.find_all('div', {'id': 'dic_area'})
            if len(tag_content) < 1:
                print_cur_state(f'len(tag_content) = 0', end='\n')
                return None
            # 뉴스 기사 본문 초기화
            content = ArticleParser.clear_content(str(tag_content[0].find_all(string=True)))
            # 공백일 경우 기사 제외 처리
            if not isinstance(content, str) or content is None:
                print_cur_state(f'content is None', end='\n')
                #                        print(tag_content, add, type(add), sep=', ')
                return None
            content = self.refine_content(content)
            if content == "":
                print_cur_state(f'content == ""', end='\n')
                return None
#            print_cur_state(f'content: "{content}"\n')
            # 기사 요약함
            summary = text_summary.get_article_summary(content)
#            print_cur_state(f'summary: "{summary}"')

            # 기사 언론사 가져옴
            tag_content = document_content.find_all('meta', {'property': 'og:article:author'})
            # 언론사 초기화
            publisher = tag_content[0]['content'].split("|")[0]
            # 공백일 경우 기사 제외 처리
            if not isinstance(publisher, str) or publisher is None:
                print_cur_state(f'publisher is None', end='\n')
                # print(tag_content[0]['content'], add, type(add), sep=', ')
                return None
            publisher = publisher.strip()
            # print_cur_state(f'publisher: {publisher}')

            # 기사 시간대 가져옴
            create_date = document_content.find_all('span', {
                'class': "media_end_head_info_datestamp_time _ARTICLE_DATE_TIME"})[0]['data-date-time']
            print_cur_state(f'create_date: {create_date}')

            if self.last_create_dates[url_category] >= datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S"):
#                print(self.last_create_dates[url_category], datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S"), self.last_create_dates[url_category] >= datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S"))
                print_cur_state(f'last_article_datetime: {datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S")}', end='\n')
                is_finished[0] = True
                return None

            # Article object insert
            article_obj = Article(title=title, content=content, summary=summary, category=url_category,
                                  publisher=publisher,
                                  source=post_url, create_date=create_date)
            return article_obj
        # UnicodeEncodeError
        except Exception as ex:
            print_cur_state(f'ArticleCrawler.crawling():ex:[{ex}]')
            assert False
            return None

    def crawling(self, category):
        print_cur_state(f'last_create_date: {self.last_create_dates[category]}')

        # 기사 url 형식
        url_format = f'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1={self.categories.get(category)}&date='
        # start_year년 start_month월 start_day일 부터 ~ end_year년 end_month월 end_day일까지 기사를 수집합니다.
        target_urls = self.make_news_page_url(url_format, self.date)
        print_cur_state(f'{category} Urls are generated')

        print_cur_state(f'{category} is collecting ...')
        finished = [False]
        inserted_articles_count = 0
        for base_url in target_urls:
            # print_cur_state(f'url = {url}')
            request = self.get_url_data(base_url)
            document = BeautifulSoup(request.content, 'html.parser')

            # html - newsflash_body - type06_headline, type06
            # 각 페이지에 있는 기사들 가져오기
            temp_post = document.select('.newsflash_body .type06_headline li dl')
            temp_post.extend(document.select('.newsflash_body .type06 li dl'))

            # 각 페이지에 있는 기사들의 url 저장
            post_urls = []
            for line in temp_post:
                # 해당되는 page에서 모든 기사들의 URL을 post_urls 리스트에 넣음
                temp_url = line.a.get('href')
                same_url_cnt = Article.query.filter(Article.source == temp_url).count()
                if same_url_cnt > 0:
                    continue
                post_urls.append(temp_url)
            del temp_post

            # for content_url in post_urls[:1]:  # 기사 url
            # print_cur_state(content_url)
            # print_cur_state(f'urls count = {len(post_urls)}')

            for url in post_urls:
                article = self.get_article_from_url(category, url, finished)
                if finished[0]:
                    break
                if article is None:
                    continue
#                print_cur_state(f' has been inserted.')
                insert_one_article(article)
                inserted_articles_count += 1
            if finished[0]:
                break
        db.session.commit()
        return inserted_articles_count

    def start(self, start_day, end_day, categories):
        #        def test(category, test_url):
        #            self.set_last_create_date(category, get_last_create_date(category))
        #            article = self.get_article_from_url(category, test_url, False)
        #        test('정치', "https://n.news.naver.com/mnews/article/022/0003751270?sid=100")
        #        return None
        self.set_category(*categories)
        self.set_date_range(start_day, end_day)

        total_inserted_articles_count = 0

        # 크롤링 시작
        for category in self.selected_categories:
            print_cur_state(f'{category} has been started.')
            self.set_last_create_date(category, get_last_create_date(category))
            inserted_articles_count = self.crawling(category)
            print_cur_state(f'{category}: {inserted_articles_count} articles has been inserted.')
            total_inserted_articles_count += inserted_articles_count

        return total_inserted_articles_count

crawler = ArticleCrawler()


if __name__ == "__main__":
    None
