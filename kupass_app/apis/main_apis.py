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


api.add_resource(Summary, '/summary')
