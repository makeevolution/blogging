from flask import Response, jsonify, request, g, url_for, current_app
from .. import db
from ..models import Post, Permission
from . import api
from .decorators import permission_required
from .errors import forbidden

@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api.get_post', id=post.id)}

@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type = int)
    paginate = db.session.query(Post).paginate(
        page, per_page = current_app.config["FLASKY_POSTS_PER_PAGE"],
        error_out = False
    )
    posts = paginate.items
    prev = None
    next = None
    if paginate.has_prev:
        prev = url_for("api.get_posts", page = page - 1)
    if paginate.has_next:
        next = url_for("api.get_posts", page = page + 1)
    return jsonify({"posts": [post.to_json() for post in posts],
                    "url_prev": prev,
                    "url_next": next,
                    'total_posts': paginate.total})

@api.route('/posts/<int:id>')
def get_post(id):
    post = db.session.query(Post).get_or_404(id)
    return jsonify(post.to_json())

@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE)
def edit_post(id):
    post = db.session.query(Post).get_or_404(id)
    # Check permission!
    if post.author != g.current_user._get_current_object() and \
        not g.current_user._get_current_object().can(Permission.ADMIN):
        return forbidden("You are not allowed to edit this post!")
    # .get() below attempts to get the value for key 'body', otherwise
    # use the default value, defined as post.body (so no changes made)
    new_body = request.json.get('body', post.body)
    post.body = new_body
    db.session.add(post.body)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api.get_post', id=post.id)}

