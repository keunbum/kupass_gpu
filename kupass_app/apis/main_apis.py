from flask import Blueprint, request, json
from flask_restful import Resource, Api

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
        return {'summary': title + ": " + content}, 201

class Crawler(Resource):
    # 무슨 무슨 날짜에 특정 카테고리에 해당하는 기사들 크롤링 해줘.
    # 날짜 특정하지 않을 경우 에러. 잘못된 날짜 형식 에러.
    # 카테고리 지정하지 않으면 전체 카테고리 지정.
    def post(self):
        def is_valid_request():
            return True
            """
            if request.headers.get('Content-Type') != 'application/json':
                return None
            """
        res = is_valid_request()
        if not res:
            return {'message': "bad request"}, 400
        from kupass_app.gpus.main_gpus import insert_csv
        insert_csv()
        return {'message': "success"}, 201


api.add_resource(Summary, '/summary')
api.add_resource(Crawler, '/crawler')
