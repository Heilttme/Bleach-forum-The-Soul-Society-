from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    nickname = StringField('Введите никнейм', validators=[DataRequired()])
    name = StringField('Введите имя', validators=[DataRequired()])
    surname = StringField('Введите фамилию', validators=[DataRequired()])
    email = EmailField('Введите Email', validators=[DataRequired()])
    password = PasswordField('Введите пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Введите email', validators=[DataRequired()])
    password = PasswordField('Введите пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class Post(FlaskForm):
    title = StringField('Введите заголовок темы', validators=[DataRequired()])
    text = TextAreaField('Введите текст')
    submit = SubmitField('Опубликовать')


class AnswerFrom(FlaskForm):
    answer = TextAreaField('Оставить комментарий', validators=[DataRequired()])
    submit = SubmitField('Ответить')
