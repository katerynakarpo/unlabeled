from flask import request
from books.parser_workload import upload_book_gen
import json
from books.models import get_fragments_by_book, get_random_fragment


def init_views(app):
    @app.route("/")
    async def hello_world():
        return "This is books parser API!"

    @app.route("/upload", methods=['POST'])
    async def upload_book():
        file = request.files['file']
        res_gen = upload_book_gen(file)
        return res_gen

    @app.route("/one_book_fragments", methods=['GET'])
    async def get_books_fragments():
        return json.dumps(get_fragments_by_book())

    @app.route("/random_fragment", methods=['GET'])
    async def random_fragment():
        return json.dumps(get_random_fragment())
