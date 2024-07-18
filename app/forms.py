from datetime import datetime
from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField, DateTimeField
from wtforms.fields.numeric import FloatField, IntegerField
from wtforms.fields.simple import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Email, NumberRange
from app.models import Users


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=13, max=13)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    card_number = StringField('Card Number', validators=[DataRequired(), Length(min=16, max=16)])
    card_balance = FloatField('Card Balance', validators=[DataRequired(), NumberRange(min=0)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_card_number(self, card_number):
        if Users.query.filter_by(card_number=card_number.data).first():
            raise ValidationError('This card number is already in use.')

    def validate_email(self, email):
        if Users.query.filter_by(email=email.data).first():
            raise ValidationError('This email is already in use.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Invalid email')


class TransferForm(FlaskForm):
    recipient_card = StringField('Recipient Card', validators=[DataRequired(), Length(min=16, max=16)])
    balance = FloatField('Balance', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Transfer')

    def validate_balance(self, balance):
        if balance.data <= 0:
            raise ValidationError('Balance must be greater than 0.')

    def validate_recipient_card(self, recipient_card):
        recipient = Users.query.filter_by(card_number=recipient_card.data).first()
        if not recipient:
            raise ValidationError('This recipient card is unavailable.')

class ConfirmDeleteForm(FlaskForm):
    confirm = SubmitField('Delete Account')
    cancel = SubmitField('Cancel')


class TransferHistoryForm(FlaskForm):
    start_date = DateField('Start Date', format='%m/%d/%Y', validators=[DataRequired()])
    end_date = DateField('End Date', format='%m/%d/%Y', validators=[DataRequired()])
    submit = SubmitField('Show History')