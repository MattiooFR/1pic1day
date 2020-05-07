from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from app import photos


class CreateAlbumForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    photo = FileField(
        validators=[FileAllowed(photos, "Image Only!"), FileRequired("Choose a file!")]
    )
    submit = SubmitField("Create album")
