from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'M5xZxktelY'


class User(db.Model):

    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(120))
    password=db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Blog {name}>'.format(name=self.name)

@app.before_request
def requre_login():
    allowed_routes = ['signup', 'login', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        flash('You must log in to continue')
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():

    users = User.query.all()
    owner_id = request.args.get('id')

    if owner_id:
        owner = User.query.get(owner_id)
        # owner = User.query.filter_by(user).first()
        if owner:
            blogs = Blog.query.filter_by(owner=owner).all()
            blog_id = request.args.get('id')
            return render_template('blog.html', owner=owner)
            

    return render_template('index.html', users=users)

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    blogs = Blog.query.all()
    blog_id = request.args.get('id')
    blog_user = request.args.get('user')

    # owner = User.query.filter_by(username=session['username']).first()
    
    # if owner:
    #     blogs = Blog.query.filter_by(owner=owner).all()
    #     blog_id = request.args.get('id')


    if blog_user:
        blogs = Blog.query.filter_by(owner_id=blog_user).all()
    if blog_id:
        blogs = Blog.query.get(blog_id)
        return render_template('post.html', blogs=blogs)

    return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()

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
            new_blog = Blog(blog_name, blog_entry, owner)
            db.session.add(new_blog)
            db.session.commit()
            blog_location = 'blog?id=' + str(new_blog.id)
            return redirect(blog_location)
    else:
        return render_template('/newpost.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    username = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == "" or len(username) <= 3 or len(username) > 20:
            flash('Please enter a valid username')
        if password == "":
            flash('You forgot your password!')
        elif verify == "":
            flash('Please verify password')
        elif verify != password:
            flash('Passwords do not match')
        # return render_template('signup.html', username=username)

        else:        
            existing_user = User.query.filter_by(username=username).first()

            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/blog')
            else:
                flash('Oops! Looks like you already have an account!')
                return redirect('/login')

    return render_template('signup.html', username=username)

@app.route('/login', methods=['POST', 'GET'])
def login():

    username = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Welcome Back!')
            return redirect('/blog')
        elif username == "":
            flash('You forgot your username!')
        elif password == "":
            flash('Please enter a valid password')
        elif user.password != password:
            flash('User password incorrect', 'error')
    return render_template('/login.html', username=username)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


if __name__ == '__main__':
    app.run()
        

