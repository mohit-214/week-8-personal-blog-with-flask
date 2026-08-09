from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    Response,
)
from app import db
from app.models import Post, User, Comment, Category
from app.main.forms import SearchForm, ContactForm, NewsletterForm
from config import Config

main = Blueprint("main", __name__)


@main.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    category = request.args.get("category")
    query = request.args.get("q")

    posts_query = Post.query.filter_by(is_published=True)

    if category:
        posts_query = posts_query.filter(
            Post.category.has(Category.name == category)
        )

    if query:
        posts_query = posts_query.filter(
            Post.title.ilike(f"%{query}%") | Post.content.ilike(f"%{query}%")
        )

    posts = posts_query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=Config.POSTS_PER_PAGE, error_out=False
    )

    # Stats
    total_posts = Post.query.filter_by(is_published=True).count()
    total_comments = Comment.query.count()
    total_users = User.query.count()
    most_viewed = (
        Post.query.order_by(Post.views.desc())
        .filter_by(is_published=True)
        .first()
    )
    active_users = (
        User.query.join(Post)
        .group_by(User.id)
        .order_by(Post.__table__.c.timestamp.desc())
        .limit(5)
        .all()
    )

    newsletter_form = NewsletterForm()

    return render_template(
        "main/index.html",
        posts=posts,
        total_posts=total_posts,
        total_comments=total_comments,
        total_users=total_users,
        most_viewed=most_viewed,
        active_users=active_users,
        newsletter_form=newsletter_form,
    )


@main.route("/about")
def about():
    return render_template("main/about.html", title="About")


@main.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # In production, send email here. For now, just flash a success message.
        flash(
            "Thank you for your message! We'll get back to you soon.", "success"
        )
        return redirect(url_for("main.contact"))
    return render_template("main/contact.html", form=form, title="Contact")


@main.route("/newsletter", methods=["POST"])
def newsletter():
    form = NewsletterForm()
    if form.validate_on_submit():
        flash(f"Subscribed with {form.email.data}. Welcome aboard!", "success")
    else:
        flash("Please enter a valid email address.", "danger")
    return redirect(url_for("main.index"))


@main.route("/rss")
def rss():
    from xml.etree.ElementTree import Element, SubElement, tostring
    from xml.dom import minidom

    posts = (
        Post.query.filter_by(is_published=True)
        .order_by(Post.timestamp.desc())
        .limit(20)
        .all()
    )

    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = "My Personal Blog"
    SubElement(channel, "link").text = url_for("main.index", _external=True)
    SubElement(channel, "description").text = "Latest blog posts"

    for post in posts:
        item = SubElement(channel, "item")
        SubElement(item, "title").text = post.title
        SubElement(item, "link").text = url_for(
            "posts.view_post", slug=post.slug, _external=True
        )
        SubElement(item, "description").text = post.short_content
        SubElement(item, "pubDate").text = post.timestamp.strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )

    xml_str = minidom.parseString(tostring(rss)).toprettyxml(indent="  ")
    return Response(xml_str, mimetype="application/rss+xml")
