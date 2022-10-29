# coding: utf-8
import os
import pandas as pd
import time

from kupass_app.models import Article, Keyword
from konlpy.tag import Okt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from kupass_app import crawler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

start = time.time()


def get_cur_time():
    return time.time() - start


def change_day_format(day):
    return day.replace("-", "")


def read_data_frames(start_day, end_day, file_dir):
    start_day = change_day_format(start_day)
    end_day = change_day_format(end_day)
    # categories = ['politics', 'economy', 'society', 'culture', 'world', 'IT_science', 'opinion']
    categories_kr = ['정치', '경제', '사회', '생활문화', '세계', 'IT과학', '오피니언']
    column_names = ['time', 'category', 'company', 'title', 'content', 'link']
    dfs = pd.DataFrame()
    for category_kr in categories_kr:
        df = pd.read_csv(f'{file_dir}\Article_{category_kr}_{start_day}_{end_day}.csv', names=column_names,
                         encoding='CP949')
        dfs = pd.concat([dfs, df], ignore_index=True)
    return dfs


def get_article_list(dfs):
    from typing import List
    from textrankr import TextRank
    from konlpy.tag import Okt

    class OktTokenizer:
        okt: Okt = Okt()

        def __call__(self, text: str) -> List[str]:
            tokens: List[str] = self.okt.phrases(text)
            return tokens

    mytokenizer: OktTokenizer = OktTokenizer()
    textrank: TextRank = TextRank(mytokenizer)

    article_list = []
    title_max_len = 0
    content_max_len = 0
    summary_max_len = 0
    for i, article in dfs.iterrows():
        create_date, category, publisher, title, content, source = [article[key].strip() for key in article.keys()]
        summary = textrank.summarize(content, 3, verbose=False)
        summary = ''.join(summary)
        title_max_len = max(title_max_len, len(title))
        content_max_len = max(content_max_len, len(content))
        summary_max_len = max(summary_max_len, len(summary))
        #        print(title, content, summary, category, publisher, source, create_date, sep='\n')
        article_list.append(
            Article(title=title, content=content, summary=summary, category=category, publisher=publisher,
                    source=source, create_date=create_date))
        qq = 10
        if i > 0 and i % qq == 0:
            j = i // qq - 1
            print(f'{get_cur_time()}: {j * qq} ~ {j * qq + (qq - 1)}th articles have been appended.')
        if i == len(dfs) - 1:
            j = i // qq
            print(f'{get_cur_time()}: {j * qq} ~ {j * qq + i % qq}th articles have been appended.')
    print(f'title_max_len = {title_max_len}')
    print(f'content_max_len = {content_max_len}')
    print(f'summary_max_len = {summary_max_len}')
    return article_list


class KeywordsProducer:
    def __init__(self):
        self.stop_words = "기자 앵커 일보 신문 뉴스 재판매 조선일보 서울신문 한국일보 세계일보 한겨레 동아일보 중앙일보 국민일보 연합뉴스 뉴시스 오마이뉴스 지디넷코리아 디지털데일리 블로터 " \
                          "프레시안 노컷뉴스 미디어오늘 디지털타임스 더팩트 데일리안 전자신문 여성신문 동아사이언스 코리아중앙데일리 기자협회보 코메디닷컴 농민신문 코리아헤럴드 헬스조선 " \
                          "뉴스타파 주간동아 월간산 주간경향 시사저널 매경이코노미 주간조선 이코노미스트 한경비즈니스 비즈니스워치 이데일리 조세일보 헤럴드경제 아시아경제 매일경제 머니투데이 " \
                          "서울경제 서울비즈 파이낸셜뉴스 국제신문 강원일보 강원도민일보 부산일보 대전일보 매일신문 "
        self.stop_words = set(self.stop_words.split())
        self.okt = Okt()
        self.n_gram_range = (1, 1)
        self.model = SentenceTransformer('sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens')
        self.top_n = 5

    def get_keywords(self, content):
        assert isinstance(content, str)
        # create_date, category, publisher, title, content, source = [article[key] for key in article.keys()]
        tokenized_doc = self.okt.pos(content)
        tokenized_nouns = ' '.join(
            [word[0] for word in tokenized_doc if
             word[1] == 'Noun' and not word[0] in self.stop_words and len(word[0]) > 1])

        count = CountVectorizer(ngram_range=self.n_gram_range).fit([tokenized_nouns])
        candidates = count.get_feature_names_out()

        doc_embedding = self.model.encode([content])
        candidate_embeddings = self.model.encode(candidates)

        distances = cosine_similarity(doc_embedding, candidate_embeddings)
        keywords = [candidates[index] for index in distances.argsort()[0][-self.top_n:]]
        return keywords


keyword_producer = KeywordsProducer()


def insert_csv(start_day, end_day, categories, file_dir=f'{BASE_DIR}\output'):
    from kupass_app import db
    print(f'crawl starts')
    crawler.get_csv(start_day, end_day, categories)
    print(f'crawl ends')
    dfs = read_data_frames(start_day, end_day, file_dir)
    print(f'{get_cur_time()}: read data frames.')
    print(f'dfs size = {len(dfs)}')

    article_list = get_article_list(dfs)
    print(f'{get_cur_time()}: append articles.')
    print(f'article_list size = {len(article_list)}')

    for i, article in enumerate(article_list):
        keywords = keyword_producer.get_keywords(article.content)
        db.session.add(article)
        for keyword in keywords:
            _keyword = Keyword(keyword=keyword)
            kw = Keyword.query.filter(Keyword.keyword == keyword).all()
            if kw:
                article.keyword.append(kw[0])
            else:
                db.session.add(_keyword)
                article.keyword.append(_keyword)

        qq = 10
        if i > 0 and i % qq == 0:
            j = i // qq - 1
            print(f'{get_cur_time()}: {j * qq} ~ {j * qq + (qq - 1)}th articles have been inserted.')
        if i == len(article_list) - 1:
            j = i // qq
            print(f'{get_cur_time()}: {j * qq} ~ {j * qq + i % qq}th articles have been inserted.')
    before_commit = get_cur_time()
    db.session.commit()
    after_commit = get_cur_time()
    print(f'took {after_commit - before_commit} seconds for db.session.commit()')
    # try:

    # except exc.IntegrityError:
    #    print("ERROR!!!")
    print(f'all articles committed')


def main():
    None


if __name__ == '__main__':
    main()
