from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class CommentForm(FlaskForm):
    content = TextAreaField(
        "Comment",
        validators=[DataRequired(), Length(min=2, max=2000)],
        render_kw={"placeholder": "Write a comment..."},
    )
    submit = SubmitField("Post Comment")
