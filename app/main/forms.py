from collections import Iterable

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField
from werkzeug.datastructures import FileStorage
from wtforms.validators import InputRequired, StopValidation, DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed

# from app import photos


class MultiFileAllowed(object):
    def __init__(self, upload_set, message=None):
        self.upload_set = upload_set
        self.message = message

    def __call__(self, form, field):

        if not (
            all(isinstance(item, FileStorage) for item in field.data) and field.data
        ):
            return

        for data in field.data:
            filename = data.filename.lower()

            if isinstance(self.upload_set, Iterable):
                if any(filename.endswith("." + x) for x in self.upload_set):
                    return

                raise StopValidation(
                    self.message
                    or field.gettext(
                        "File does not have an approved extension: {extensions}"
                    ).format(extensions=", ".join(self.upload_set))
                )

            if not self.upload_set.file_allowed(field.data, filename):
                raise StopValidation(
                    self.message
                    or field.gettext("File does not have an approved extension.")
                )


class CreateAlbumForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    photo = MultipleFileField(
        validators=[MultiFileAllowed(["jpg", "png"], "Image Only!"), InputRequired()]
    )
    submit = SubmitField("Create album")


class EditAlbumNameForm(FlaskForm):
    name = StringField("Album title", validators=[DataRequired()])
    submit = SubmitField("New title")
