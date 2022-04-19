from flask import Flask, render_template, url_for, redirect
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_restful import Api
from sqlalchemy import update

import posts_resources
from data import db_session
from data.classes import User, Posts
from data.forms import RegisterForm, LoginForm, Post, AnswerFrom

# Инициализация приложения
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'gdrljnfbdln43nv9o34nrmf34mndrlgkjeroilvreiklhreklbrevrebbre0hbre439v34jkn3498vdghfdg8'
login_manager = LoginManager()  # LoginManager для авторизации пользователя
login_manager.init_app(app)


# Во всех функциях, которые используют render_template есть условие, которое провеяет
# если пользователь залогинин на сайте, и, в зависимости от этого возвращает функцию,
# у которой есть никнейм или нет.

# db_sess - это объект бд, с помощью которого производятся запросы.

# Главная страница сайта
@app.route('/')
def index_auth():
    if current_user.is_authenticated:
        return render_template('main_page.html', styles=url_for('static', filename='css/main_style.css'),
                               username=current_user.nickname)
    else:
        return render_template('main_page.html', styles=url_for('static', filename='css/main_style.css'))


# Страница форум
@app.route('/forum', methods=['POST', 'GET'])
def forum():
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).all()  # Темы обсуждений в главном разделе
    posts.reverse()
    hot_disscussed = posts.copy()  # Самые обсуждаемые темы
    hot_disscussed = hot_disscussed[:10]
    hot_disscussed.sort(key=lambda x: (len(x.answers.split(';'))))
    hot_disscussed.reverse()
    # Самые обсуждаемые темы выводятся по принципу количества ответов в ней.
    # Максимум в этом разделе может находиться 10 тем.
    if current_user.is_authenticated:
        return render_template('forum.html', styles=url_for('static', filename='css/forum.css'),
                               username=current_user.nickname, posts=posts, hot_disscussed=hot_disscussed)
    else:
        return render_template('forum.html', styles=url_for('static', filename='css/forum.css'),
                               posts=posts, hot_disscussed=hot_disscussed)


# Страница регистрации
@app.route('/sign_up', methods=['POST', 'GET'])
def register():
    # Возвращает на главное страницу, если пользователь авторизован.
    if current_user.is_authenticated:
        return redirect('/')
    # Форма регистрации
    form = RegisterForm()
    if form.is_submitted():
        db_sess = db_session.create_session()
        # Проверка различных случаев, при которых невозможно произвести регистрацию:
        # Проверка по никнейму.
        if db_sess.query(User).filter(User.nickname == form.nickname.data).all():
            message = 'Пользователь с таким никнеймом уже существует.'
            return render_template('sign_up.html', form=form, message=message,
                                   style=url_for('static', filename='css/login_signup_style.css'))

        # Проверка по электронной почте.
        if db_sess.query(User).filter(User.email == form.email.data).all():
            message = 'Пользователь с таким email уже существует.'
            return render_template('sign_up.html', form=form, message=message,
                                   style=url_for('static', filename='css/login_signup_style.css'))
        # Проверка совпадения пароля.
        if form.password.data != form.password_again.data:
            message = 'Пароли не сходятся.'
            return render_template('sign_up.html', form=form, message=message,
                                   style=url_for('static', filename='css/login_signup_style.css'))
        # Проверка длины пароля
        if len(form.password.data) <= 6:
            message = 'Слишком короткий пароль'
            return render_template('sign_up.html', form=form, message=message,
                                   style=url_for('static', filename='css/login_signup_style.css'))
        # Проверка длины никнейма
        if len(form.nickname.data) >= 12:
            message = 'Слишком длинный никнейм'
            return render_template('sign_up.html', form=form, message=message,
                                   style=url_for('static', filename='css/login_signup_style.css'))
        # В случае отсутствия ошибок создается модель пользователя и записывается в бд.
        user = User(nickname=form.nickname.data,
                    name=form.name.data,
                    surname=form.surname.data,
                    email=form.email.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/log_in')
    return render_template('sign_up.html', form=form,
                           style=url_for('static', filename='css/login_signup_style.css'))


# Страница входа
@app.route('/log_in', methods=['GET', 'POST'])
def login():
    # Возвращает на главное страницу, если пользователь авторизован.
    if current_user.is_authenticated:
        return redirect('/')
    # Форма входа
    form = LoginForm()
    if form.is_submitted():
        db_sess = db_session.create_session()
        # Проверка пользователя на существование
        if not db_sess.query(User).filter(User.email == form.email.data).all():
            message = 'Пользователя с таким email не существует.'
            return render_template('login.html', form=form, message=message,
                                       style=url_for('static', filename='css/login_signup_style.css'))

        user = db_sess.query(User).filter(User.email == form.email.data).first()
        # Проверка сходства пароля в форме и бд.
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)    # Функция авторизации пользователя
            return redirect('/')
        else:
            message = 'Введённый пароль неверен'
            return render_template('login.html', form=form, message=message,
                                   style=url_for('static', filename='css/login_signup_style.css'))
    return render_template('login.html', form=form, style=url_for('static', filename='css/login_signup_style.css'))


# Функция авторизации пользователя.
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# Страница на форуме для создания новой темы.
@app.route('/new_post', methods=['POST', 'GET'])
def new_post():
    form = Post()
    # Форма темы
    if form.is_submitted():
        db_sess = db_session.create_session()
        # Создание модели формы и занесение данных в бд
        post = Posts(title=form.title.data,
                     content=form.text.data,
                     user_id=current_user.id)
        db_sess.add(post)
        db_sess.commit()
        return redirect('/forum')
    if current_user.is_authenticated:
        return render_template('new_post.html', form=form, username=current_user.nickname,
                               styles=url_for('static', filename='css/login_signup_style.css'))
    else:
        return render_template('new_post.html', form=form,
                               styles=url_for('static', filename='css/login_signup_style.css'))


# Страница обсуждения. Id - идентификатор темы
@app.route('/topic<id>', methods=['GET', 'POST'])
def topic(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).filter(Posts.id == id).first()
    user = db_sess.query(User).filter(User.id == post.user_id).first()
    # Форма создания ответа на тему
    form = AnswerFrom()
    if form.is_submitted():
        # Из бд берётся столбец, в котором хранятся ответы на тему по типу 'Пользователь:ответ', разделённые
        # точкой с запятой, а потом к нему добавляется ответ из формы
        values = db_sess.query(Posts).filter(Posts.id == id).first().answers
        values += f';{current_user.nickname}:{form.answer.data}'
        db_sess.execute(update(Posts).where(Posts.id == id).values(answers=values))
        db_sess.commit()
    # Для отображения ответов из бд берутся данные и разделяются на два списка.
    answers = db_sess.query(Posts).filter(Posts.id == id).first().answers.split(';')[1:]
    users = []
    answ = []
    length = len(answers)
    for i in range(len(answers)):
        users.append(answers[i].split(':')[0])
        answ.append(answers[i].split(':')[1])
    if current_user.is_authenticated:
        return render_template('topic.html', form=form, user=user, post=post, username=current_user.nickname,
                               users=users, answ=answ, length=length,
                               styles=url_for('static', filename='css/topic_styles.css'))
    else:
        return render_template('topic.html', form=form, user=user, post=post, users=users, answ=answ, length=length,
                               styles=url_for('static', filename='css/topic_styles.css'))


# Функция выхода пользователя из системы.
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


# Запуск программы
if __name__ == '__main__':
    # Инициализания бд.
    db_session.global_init("db/forum.db")
    # Добавление api, которое даёт возможность получить все темы,
    # опубликованные на форуме, а так же каждую по отдельности.
    api.add_resource(posts_resources.PostResources, '/api/posts/<id>')
    api.add_resource(posts_resources.PostsListResource, '/api/posts')
    app.run()
