from flask import Flask
import os
import sys
sys.path.append(os.getcwd())

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://katekarpo:123123asdA@localhost/unlabeled'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'development key'
from books.models import db

db.init_app(app)
with app.app_context():
    db.create_all()
from books.views import init_views
init_views(app)


def main(host='0.0.0.0', port=5002, debug=False, threaded=False):
    app.run(host=host, port=port, debug=debug, threaded=threaded)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-host', '--host', type=str, default='0.0.0.0')
    parser.add_argument('-p', '--port', type=str, default='5001')
    parser.add_argument('-d', '--debug', type=int, default=0, choices=[0, 1])
    parser.add_argument('-thr', '--threaded', type=int, default=1, choices=[0, 1])
    args = parser.parse_args()
    main(host=args.host, port=args.port, debug=bool(args.debug), threaded=bool(args.threaded))
    # main()
