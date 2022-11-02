from flask import Blueprint, request, json
from flask_restful import Resource, Api

from datetime import datetime

from kupass_app.models import Article
from kupass_app import crawler

bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(bp)


class Summary(Resource):
    def get(self):
        return json.jsonify({'message': 'hello localhost'})

    def post(self):
        def is_valid_request():
            max_len = int(2e3)
            if request.headers.get('Content-Type') != 'application/json':
                return None
            try:
                data = request.get_json()['data']
                document = data.get('document')
                title = document['title']
                content = document['content']
            except KeyError:
                return None
            except Exception:
                return None
            if (len(content) == 0
                    or len(title) + len(content) > max_len):
                return None
            return title, content

        res = is_valid_request()
        if not res:
            return {'message': "bad request"}, 400
        title, content = res
        from kupass_app.gpus.main_gpus import keyword_producer
        summary = keyword_producer.get_keywords(content)
        return {'summary': summary}, 201

class Crawler(Resource):
    # 날짜 특정하지 않을 경우 에러. 잘못된 날짜 형식 에러.
    # 카테고리 지정하지 않으면 전체 카테고리 지정.
    categories_en = ['politics', 'economy', 'society', 'living_culture', 'world', 'IT_science', 'opinion']

    def post(self):

        def is_valid_day_format(day):
            # hmm... ;;
            return True
        def is_valid_request():
            if request.headers.get('Content-Type') != 'application/json':
                return None
            try:
                data = request.get_json()['data']
                now = datetime.now().strftime("%Y-%m-%d")
                #now = '2022-10-01'
                start_day = data.get('start_day', now)
                end_day = data.get('end_day', now)
                categories = data.get('categories', self.categories_en)
                print(f'start_day ~ end_day: {start_day} ~ {end_day}')
                print(f'categories: {categories}')
            except KeyError:
                return None
            except Exception:
                return None
            if (not is_valid_day_format(start_day)
                    or not is_valid_day_format(end_day)
                    or not all(e in self.categories_en for e in categories)):
                return None
            return start_day, end_day, categories

        res = is_valid_request()
        if not res:
            return {'message': "bad request"}, 400
        start_day, end_day, categories = res
        print(f'crawl starts')
        crawler.get_csv(start_day, end_day, categories)
        return {'message': "success"}, 201

class Extracter(Resource):

    def post(self):
        def is_valid_request(self):
            if request.headers.get('Content-Type') != 'application/json':
                return None
            return True

        res = is_valid_request()
        if not res:
            return {'message': "bad request"}, 400
        return {'message': "success"}, 201



api.add_resource(Summary, '/summary')
api.add_resource(Crawler, '/crawler')
api.add_resource(Extracter, '/extract')
