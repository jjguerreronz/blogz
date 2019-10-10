from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:123456@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text())

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/')
def index():
    blogs = Blog.query.all()
    print(blogs)
    return render_template('blog.html', title="Build a Blog!", blogs=blogs)


@app.route('/blog', methods=['POST', 'GET'])
def show_blog():

    if request.args:
        blog_id = request.args.get('id')
        blogs = Blog.query.filter_by(id=blog_id).all()
        return render_template('single_post.html', blogs=blogs)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', title="Build a Blog!", blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def create_new_post():
    if request.method == 'GET':
        return render_template('new_post.html', title="New Blog Entry")

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_blog = Blog(blog_title, blog_body)

        title_error = ''
        body_error = ''

        if len(blog_title) == 0:
            title_error = "Please enter a title for your new post."
        if len(blog_body) == 0:
            body_error = "Please enter text for your new post."

        if not title_error and not body_error:
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={}'.format(new_blog.id))

        else:
            blogs = Blog.query.all()
            return render_template('new_post.html', title="Build a Blog!", blogs=blogs,
                                   blog_title=blog_title, title_error=title_error,
                                   blog_body=blog_body, body_error=body_error)


if __name__ == '__main__':
    app.run()
