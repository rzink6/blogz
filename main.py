from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:cheese@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'M5xZxktelY'


class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Blog {name}>'.format(name=self.name)

@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    blogs = Blog.query.all()
    blog_id = request.args.get('id')

    if blog_id:
        blog = Blog.query.get(blog_id)
        return render_template('post.html',blog=blog)

    # if request.method == 'POST':
    #     title = request.form['title']
    #     body = request.form['body']


    # else:
    return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    #if request.method == 'GET':
        #blog_name = request.args.get('title')
        #blog_entry = request.args.get('body')
        #return render_template('newpost.html')
    blog_id = request.args.get('id')
    if blog_id:
        return redirect('/blog?id={{blog.id}}')

    if request.method == 'POST':
        blog_name = request.form['title']
        blog_entry = request.form['body']
        
        if blog_name == "" or blog_entry == "":
            flash("Oops! Looks like you forgot your title or blog entry!", 'error')
            return redirect('/newpost')
        else:
            new_blog = Blog(blog_name, blog_entry)
            db.session.add(new_blog)
            db.session.commit()
            blog_location = 'blog?id=' + str(new_blog.id)
            return redirect(blog_location)
    else:
        return render_template('/newpost.html')


if __name__ == '__main__':
    app.run()
        

