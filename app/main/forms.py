from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,  SubmitField, TextAreaField, DateTimeField
from wtforms_components import TimeField
from wtforms.validators import ValidationError, DataRequired,  Length
from app.models import User




class EditProfileForm(FlaskForm):
    """ 
    This class creates a form that allows user to edit their user_name and about 
    """
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators= [Length(min= 0, max=240)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs) :
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    def validate_username(self, username):
        if username.data !=self.original_username:
            user = User.query.filter_by(username= self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class addCourseForm(FlaskForm):
    course = StringField('Course', validators = [DataRequired()])
    building = StringField('Building', validators = [DataRequired()])
    time = TimeField('Course Time')
    submit = SubmitField('Add Course')

class DeleteProfileForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    submit = SubmitField('Delete Profile')

class EmptyForm(FlaskForm):
    #this form allows the user to do a one click to follow another user
    submit = SubmitField('Submit')
    
    
