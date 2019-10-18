from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
import traceback

app = Flask(__name__)
app.config['DEBUG'] = True
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://blogzz:123456@localhost:3306/blogzz'
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    body = db.Column(db.String(120))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, name, body, author_id):
        self.name = name
        self.body = body
        self.author_id = author_id


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40), unique=True)
    username = db.Column(db.String(40))
    password = db.Column(db.String(40))
    blogs = db.relationship("Blog", backref="author")
    logged_in = db.Column(db.Boolean())

    def __init__(self, username, password, email):
        self.email = email
        self.username = username
        self.password = password


@app.route("/", methods=['GET', 'POST'])
def index():
    blogs = None
    all_blogs = Blog.query.all()

    data_tuples = []

    user = None
    try:
        if session['logged_in']:
            blogs = Blog.query.filter(User.id == session["author_id"])
        else:
            pass
    except KeyError:
        pass

    for blog in all_blogs:

        author_object = User.query.get(blog.author_id)
        author_username = author_object.username
        object_tuple = (blog.name, blog.id, author_username)
        data_tuples.append(object_tuple)
    return render_template('blogs.html', title="Blogz assignment", blogs=blogs, user=user, data_tuples=data_tuples)


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter(User.username == username).first()
        print(user)
        print(user.password)
        print(password)
        if user.password == password:
            session['logged_in'] = True
            session['author_id'] = user.id
            print(session)
            flash('Welcome')

            return render_template("blogs.html", user=user)
        else:
            flash("Error: Try again because you do not have login or account sucka")
            return render_template('login.html', error=error)

    return render_template('login.html', error=error)


@app.route('/signup', methods=['POST', 'GET'])
def register():

    password_error = None
    username_error = None
    email_error = None

    if request.method == 'POST':
        print(type(request.form))
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        username = request.form['username']
        existing_user = User.query.filter_by(email=email).first()
        existing_username = User.query.filter_by(username=username).first()
        print(existing_user)
        print(existing_username)
        if not existing_user and not existing_username:
            new_user = User(username, password, email)
            db.session.add(new_user)
            db.session.commit()
            print(new_user)
            return redirect('/login')
        else:
            return "<h1>Duplicate user</h1>"

    return render_template('signup.html', password_error=password_error, username_error=username_error, email_error=email_error)


@app.route("/newblog", methods=['POST', 'GET'])
def index3():
    title_error = None
    body_error = None

    if request.method == 'POST':

        title = request.form['blog_name']
        body = request.form['blog']
        print(body)

        if title.strip(' ') == "":
            title_error = "Please enter a title"

        if body.strip(' ') == "":
            body_error = "Please type a blog"

        if not title_error and not body_error:

            blog_body = request.form['blog']
            blog_name = request.form['blog_name']

            new_blog = Blog(blog_name, blog_body,
                            author_id=session['author_id'])
            db.session.add(new_blog)
            db.session.commit()

            newblog_id = new_blog.id

            blogs = Blog.query.filter(User.id == session["author_id"])
            user = User.query.get(session['author_id'])
            return render_template('blogs.html', title="{0} Safe Space".format(user.username), blogs=blogs, user=user)

        else:

            return render_template('newblog.html', title="Huh??", title_error=title_error,
                                   body_error=body_error)

    else:

        return render_template('newblog.html', title="New Hotness", title_error=title_error,
                               body_error=body_error)


@app.route("/logout", methods=['GET'])
def logout():
    session.pop('logged_in', None)
    return render_template("blogs.html")


@app.route("/blog/<blog_id>/", methods=['GET'])
def individual_entry(blog_id):
    blog = Blog.query.filter(blog_id).first()
    user = User.query.get(session['author_id'])

    return render_template("individual_entry.html", blog=blog, user=user)


app.secret_key = 'key 3143275434'


if __name__ == '__main__':
    app.run()
