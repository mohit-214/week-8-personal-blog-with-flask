import os
import re
import uuid
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
    abort,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Post, Category, Tag, Comment
from app.posts.forms import PostForm, CategoryForm
from app.comments.forms import CommentForm

posts = Blueprint("posts", __name__)


def generate_slug(title):
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug or uuid.uuid4().hex[:8]


def ensure_unique_slug(slug):
    original = slug
    counter = 1
    while Post.query.filter_by(slug=slug).first():
        slug = f"{original}-{counter}"
        counter += 1
    return slug


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def save_image(file_storage):
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        return None
    filename = secure_filename(file_storage.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    file_storage.save(os.path.join(upload_dir, unique_name))
    return unique_name


@posts.route("/post/new", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            excerpt=form.excerpt.data,
            slug=ensure_unique_slug(generate_slug(form.title.data)),
            user_id=current_user.id,
            category_id=form.category_id.data or None,
            is_published=form.is_published.data,
        )
        image = save_image(form.image.data)
        if image:
            post.image = image
        db.session.add(post)
        db.session.commit()
        flash("Your post has been published!", "success")
        return redirect(url_for("posts.view_post", slug=post.slug))
    return render_template("posts/form.html", form=form, title="New Post")


@posts.route("/post/<slug>")
def view_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if not post.is_published and (not current_user.is_authenticated or post.user_id != current_user.id):
        abort(403)

    # Increment views
    post.views += 1
    db.session.commit()

    comment_form = CommentForm()
    comments = post.comments.filter_by(is_approved=True).order_by(Comment.timestamp.asc()).all()
    return render_template(
        "posts/view.html",
        post=post,
        comments=comments,
        comment_form=comment_form,
        title=post.title,
    )


@posts.route("/post/<slug>/edit", methods=["GET", "POST"])
@login_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if post.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.excerpt = form.excerpt.data
        post.category_id = form.category_id.data or None
        post.is_published = form.is_published.data
        image = save_image(form.image.data)
        if image:
            post.image = image
        db.session.commit()
        flash("Post updated successfully!", "success")
        return redirect(url_for("posts.view_post", slug=post.slug))
    return render_template("posts/form.html", form=form, post=post, title="Edit Post")


@posts.route("/post/<slug>/delete", methods=["POST"])
@login_required
def delete_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if post.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", "info")
    return redirect(url_for("main.index"))


@posts.route("/category/new", methods=["GET", "POST"])
@login_required
def new_category():
    if not current_user.is_admin:
        abort(403)
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash("Category added!", "success")
        return redirect(url_for("posts.new_category"))
    return render_template("posts/category_form.html", form=form, title="New Category")


@posts.route("/category/<name>")
def category_posts(name):
    category = Category.query.filter_by(name=name).first_or_404()
    page = request.args.get("page", 1, type=int)
    posts_ = (
        category.posts.filter_by(is_published=True)
        .order_by(Post.timestamp.desc())
        .paginate(page=page, per_page=5, error_out=False)
    )
    return render_template(
        "posts/category.html", category=category, posts=posts_, title=category.name
    )
