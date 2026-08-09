from flask import Blueprint, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app import db
from app.models import Post, Comment
from app.comments.forms import CommentForm

comments = Blueprint("comments", __name__)


@comments.route("/post/<slug>/comment", methods=["POST"])
@login_required
def add_comment(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            post_id=post.id,
        )
        db.session.add(comment)
        db.session.commit()
        flash("Your comment has been posted!", "success")
    else:
        flash("Comment could not be added. It may be too short.", "danger")
    return redirect(url_for("posts.view_post", slug=post.slug))


@comments.route("/post/<slug>/comment/<int:parent_id>/reply", methods=["POST"])
@login_required
def reply_comment(slug, parent_id):
    post = Post.query.filter_by(slug=slug).first_or_404()
    parent = Comment.query.get_or_404(parent_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            post_id=post.id,
            parent_id=parent.id,
        )
        db.session.add(comment)
        db.session.commit()
        flash("Your reply has been posted!", "success")
    else:
        flash("Reply could not be added. It may be too short.", "danger")
    return redirect(url_for("posts.view_post", slug=post.slug))


@comments.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    post_slug = comment.post.slug
    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted.", "info")
    return redirect(url_for("posts.view_post", slug=post_slug))


@comments.route("/comment/<int:comment_id>/approve", methods=["POST"])
@login_required
def approve_comment(comment_id):
    if not current_user.is_admin:
        abort(403)
    comment = Comment.query.get_or_404(comment_id)
    comment.is_approved = True
    db.session.commit()
    flash("Comment approved.", "success")
    return redirect(url_for("posts.view_post", slug=comment.post.slug))
