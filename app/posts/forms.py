from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length
from app.models import Category


class PostForm(FlaskForm):
    title = StringField(
        "Title", validators=[DataRequired(), Length(min=3, max=200)]
    )
    content = TextAreaField(
        "Content", validators=[DataRequired(), Length(min=10)]
    )
    excerpt = TextAreaField(
        "Excerpt (optional)", validators=[Length(max=400)]
    )
    category_id = SelectField("Category", coerce=int)
    image = FileField(
        "Featured Image",
        validators=[FileAllowed(["png", "jpg", "jpeg", "gif", "webp"], "Images only!")],
    )
    is_published = BooleanField("Publish now", default=True)
    submit = SubmitField("Save Post")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category_id.choices = [
            (c.id, c.name) for c in Category.query.order_by(Category.name).all()
        ]


class CategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired(), Length(min=2, max=80)])
    submit = SubmitField("Add Category")
