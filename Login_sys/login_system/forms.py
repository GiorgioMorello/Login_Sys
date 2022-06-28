from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_wtf.file import FileField, FileAllowed

class Profile(FlaskForm):
    profile_pic = FileField('Upload Image ', validators=[FileAllowed(['jpg', 'png', 'gif'])])
    submit_p = SubmitField('Submit')