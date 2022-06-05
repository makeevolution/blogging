from flask import current_app, jsonify, request, url_for

from app.api.decorators import permission_required
from . import api
from .. import db
from ..models import User, Permission

@api.route("/users/<int:id>")
def get_user(id):
    user = db.session.query(User).get_or_404(id)
    return jsonify(user.to_json())

# Remember that URLs that return a collection of resources need to have a forward slash
# at the end
@api.route("/users/<int:id>/posts/")
def get_user_posts(id):
    page = request.args.get('page', 1, type=int)
    user = db.session.query(User).get_or_404(id)
    # paginate the posts since there's a lot of them
    paginate = user.posts.paginate(page,
                                    per_page = current_app.config["FLASKY_POSTS_PER_PAGE"],
                                    error_out = False)
    posts = paginate.items
    next = None
    prev = None
    if paginate.has_prev:
        prev = url_for("api.get_user_posts", page = page - 1)
    if paginate.has_next:
        next = url_for("api.get_user_posts", page = page + 1)
    return jsonify({"posts": [post.to_json() for post in posts],
                    "url_prev": prev,
                    "url_next": next,
                    "total_posts": paginate.total})