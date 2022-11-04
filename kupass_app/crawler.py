from kupass_app.korea_news_crawler.articlecrawler import ArticleCrawler
import time

crawler = ArticleCrawler()


def crawl(start_day, end_day, *categories):
    crawler.set_category(*categories)
    crawler.set_date_range(start_day, end_day)
    crawler.start()


def start_crawl(start_day, end_day, categories):
    start_time = time.time()
    crawl(start_day, end_day, *categories)
    # print(f'It took {time.time() - start_time} seconds to crawl. from {start_day} to {end_day} for categories: {categories}')


if __name__ == "__main__":
    None
