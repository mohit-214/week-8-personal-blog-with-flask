"""Smoke test for the blog application to identify runtime bugs."""
import sys
from app import create_app, db
from app.models import User, Category, Post, Comment

app = create_app()
app.config["TESTING"] = True
app.config["WTF_CSRF_ENABLED"] = False

results = []


def check(name, fn):
    try:
        fn()
        results.append(f"PASS: {name}")
    except Exception as e:
        results.append(f"FAIL: {name} -> {type(e).__name__}: {e}")


with app.app_context():
    db.drop_all()
    db.create_all()
    u = User(username="admin", email="admin@test.com")
    u.set_password("secret123")
    u.is_admin = True
    db.session.add(u)
    c = Category(name="Tech")
    db.session.add(c)
    db.session.commit()
    p = Post(
        title="Hello World", slug="hello-world", content="## Intro\n\nSome content.",
        user_id=u.id, category_id=c.id,
    )
    db.session.add(p)
    db.session.commit()

client = app.test_client()

# Register
def test_register():
    r = client.post("/register", data={
        "username": "newuser",
        "email": "new@test.com",
        "password": "secret123",
        "confirm_password": "secret123",
    }, follow_redirects=True)
    assert r.status_code == 200, r.status_code

check("register", test_register)


# Login
def test_login():
    r = client.post("/login", data={
        "email": "admin@test.com",
        "password": "secret123",
    }, follow_redirects=True)
    assert r.status_code == 200, r.status_code
    assert b"Hello World" in r.data or b"Recent Blog Posts" in r.data

check("login", test_login)


# Index page
def test_index():
    r = client.get("/")
    assert r.status_code == 200
    assert b"Recent Blog Posts" in r.data

check("index", test_index)


# View post
def test_view_post():
    r = client.get("/post/hello-world")
    assert r.status_code == 200, r.status_code
    assert b"Hello World" in r.data

check("view_post", test_view_post)


# RSS
def test_rss():
    r = client.get("/rss")
    assert r.status_code == 200
    assert b"rss" in r.data or b"xml" in r.data

check("rss", test_rss)


# About / Contact (GET)
def test_about():
    assert client.get("/about").status_code == 200

check("about", test_about)


def test_contact_get():
    assert client.get("/contact").status_code == 200

check("contact_get", test_contact_get)


# Comment
def test_add_comment():
    r = client.post("/post/hello-world/comment", data={"content": "Nice post!"},
                    follow_redirects=True)
    assert r.status_code == 200, r.status_code
    assert b"Nice post!" in r.data or b"comment" in r.data

check("add_comment", test_add_comment)


# New post (admin logged in)
def test_new_post():
    r = client.post("/post/new", data={
        "title": "Second Post",
        "content": "## More content here for the second post.",
        "excerpt": "",
        "category_id": str(Category.query.first().id),
        "is_published": "y",
    }, follow_redirects=True)
    assert r.status_code == 200, r.status_code

check("new_post", test_new_post)


# Profile page
def test_profile():
    r = client.get("/profile")
    assert r.status_code == 200, r.status_code

check("profile", test_profile)


# Public profile
def test_public_profile():
    r = client.get("/user/admin")
    assert r.status_code == 200
    assert b"admin" in r.data

check("public_profile", test_public_profile)


# Category page
def test_category():
    r = client.get("/category/Tech")
    assert r.status_code == 200
    assert b"Tech" in r.data

check("category", test_category)


# Logout
def test_logout():
    r = client.get("/logout", follow_redirects=True)
    assert r.status_code == 200

check("logout", test_logout)


print("\n".join(results))
failed = [r for r in results if r.startswith("FAIL")]
print(f"\n{'ALL PASSED' if not failed else f'{len(failed)} FAILURES'}")

# Check for any errors page rendering
def test_404():
    r = client.get("/nonexistent-page")
    assert r.status_code == 404

check("404", test_404)

print("\n--- MORE ---")
print("\n".join([r for r in results]))

