from korea_news_crawler.articlecrawler import ArticleCrawler

def crawl(*categories, start_day, end_day):
    Crawler = ArticleCrawler()
    Crawler.set_category(categories)
    Crawler.set_date_range(start_day, end_day)
    Crawler.start()

def main():
    None

if __name__ == "__main__":
    main()