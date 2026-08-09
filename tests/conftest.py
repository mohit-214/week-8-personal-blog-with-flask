import pytest
from app import create_app, db
from app.models import User, Category, Post


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()

        # Create dummy data
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        user.is_admin = True
        db.session.add(user)

        category = Category(name="Tech")
        db.session.add(category)
        db.session.commit()

        post = Post(
            title="Test Post",
            content="This is a test post content.",
            slug="test-post",
            user_id=user.id,
            category_id=category.id,
        )
        db.session.add(post)
        db.session.commit()

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
