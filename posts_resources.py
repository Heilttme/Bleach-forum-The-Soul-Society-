from flask import jsonify
from flask_restful import Resource, abort, reqparse

from data import db_session
from data.classes import Posts

parser = reqparse.RequestParser()
parser.add_argument('id', required=True, type=int)
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('created_date', required=True)
parser.add_argument('user_id', required=True)
parser.add_argument('answers', required=True)


# Функция, обрабатывающая ошибку несуществующего id
def abort_if_post_not_found(id):
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).get(id)
    if not posts:
        abort(404, message=f'Post {id} is not fount')


# Api для получения темы по id
class PostResources(Resource):
    def get(self, id):
        abort_if_post_not_found(id)
        db_sess = db_session.create_session()
        posts = db_sess.query(Posts).get(id)
        return jsonify({'posts': posts.to_dict(only=('id', 'title', 'content', 'created_date', 'user_id', 'answers'))})


# Api для получения всех тем
class PostsListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        posts = db_sess.query(Posts).all()
        return jsonify({'posts': [item.to_dict(
            only=('id', 'title', 'content', 'created_date', 'user_id', 'answers')) for item in posts]})
