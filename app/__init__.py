from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User, Post, Comment, Category, Tag

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from app.auth.routes import auth
    from app.main.routes import main
    from app.posts.routes import posts
    from app.comments.routes import comments

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(posts)
    app.register_blueprint(comments)

    # Error handlers
    from app.errors import (
        register_error_handlers,
    )

    register_error_handlers(app)

    with app.app_context():
        db.create_all()

# Register markdown filter
    from app.markdown_filter import markdown_filter

    app.jinja_env.filters["markdown"] = markdown_filter

    # Context processor for inherited data
    @app.context_processor
    def inject_globals():
        from app.models import Category, Post

        categories = Category.query.order_by(Category.name).all()
        recent_posts = Post.query.order_by(Post.timestamp.desc()).limit(5).all()
        return {"all_categories": categories, "recent_posts": recent_posts}

    return app
