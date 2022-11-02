# coding: utf-8
import os
import pandas as pd
import time

from kupass_app.models import Article, Keyword
from konlpy.tag import Okt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

#BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
start = time.time()

os.environ['JAVA_HOME'] = r"C:\Users\woqkf\.jdks\openjdk-17.0.2\bin\server"

def get_cur_time():
    return time.time() - start


def change_day_format(day):
    return day.replace("-", "")


def print_cur_state(suffix):
    print(f'{get_cur_time():.3f} seconds: ' + suffix)


def print_ith_result(qq, i, list_size, suffix=''):
    if i > 0 and i % qq == 0:
        j = i // qq - 1
        print_cur_state(f'{j * qq} ~ {j * qq + (qq - 1)}' + suffix)
    if i == list_size - 1:
        j = i // qq
        print_cur_state(f'{j * qq} ~ {j * qq + i % qq}' + suffix)


def read_data_frames(start_day, end_day, file_dir, categories=['politics', 'economy', 'society', 'living_culture', 'world', 'IT_science', 'opinion']):
    start_day = change_day_format(start_day)
    end_day = change_day_format(end_day)
    categories_kr = ['정치', '경제', '사회', '생활문화', '세계', 'IT과학', '오피니언']
    column_names = ['time', 'category', 'company', 'title', 'content', 'link']
    dfs = pd.DataFrame()
    for category_kr in categories_kr:
        file_name = f'Article_{category_kr}_{start_day}_{end_day}.csv'
        file_full_name = f'{file_dir}\{file_name}'
        print_cur_state(f'reads data frames from {file_name}')
        df = pd.read_csv(file_full_name, names=column_names,
                         encoding='CP949')
        dfs = pd.concat([dfs, df], ignore_index=True)
    return dfs

ARTICLE_LIST_SIZE = 30

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
#    title_max_len = 0
#    content_max_len = 0
#    summary_max_len = 0
    for i, article in dfs.iterrows():
        if i == ARTICLE_LIST_SIZE:
            break
        create_date, category, publisher, title, content, source = [article[key].strip() for key in article.keys()]
        summary = textrank.summarize(content, 3, verbose=False)
        summary = ''.join(summary)
#        title_max_len = max(title_max_len, len(title))
#        content_max_len = max(content_max_len, len(content))
#        summary_max_len = max(summary_max_len, len(summary))
        #        print(title, content, summary, category, publisher, source, create_date, sep='\n')
        article_list.append(
            Article(title=title, content=content, summary=summary, category=category, publisher=publisher,
                    source=source, create_date=create_date))
#        print_ith_result(10, i, len(dfs), 'articles have been appended.')
        print_ith_result(10, i, ARTICLE_LIST_SIZE, 'th articles: summary was extracted.')
#    print(f'title_max_len = {title_max_len}')
#    print(f'content_max_len = {content_max_len}')
#    print(f'summary_max_len = {summary_max_len}')
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
    print_cur_state(f'file_dir={file_dir}')
    from kupass_app import db
    dfs = read_data_frames(start_day, end_day, file_dir)
    print_cur_state(f'reads all data frames.')
    print_cur_state(f'data frames(articles) size = {len(dfs)}')

    print_cur_state(f'Limit the number of extracted articles to {ARTICLE_LIST_SIZE}')

    article_list = get_article_list(dfs)
    print_cur_state(f'appends all articles.')
    print_cur_state(f'article_list size = {len(article_list)}')

    for i, article in enumerate(article_list):
        if i == ARTICLE_LIST_SIZE:
            break
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
#        print_ith_result(10, i, len(article_list), 'th articles have been inserted.')
        print_ith_result(10, i, ARTICLE_LIST_SIZE, 'th articles: keywords were extracted.')
    before_commit = get_cur_time()
    db.session.commit()
    after_commit = get_cur_time()
    print_cur_state(f'took {(after_commit - before_commit):.3f} seconds for db.session.commit()')
    # try:

    # except exc.IntegrityError:
    #    print("ERROR!!!")
    print_cur_state(f'all articles committed')


def main():
    None


if __name__ == '__main__':
    main()
