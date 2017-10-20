from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzpass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'BdoJHNVFbhGqPr8FVMGH'

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40))
    body = db.Column(db.String(4000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    tasks = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/blog')
        else:
            flash('User password incorrect, or user does not exist', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        
        # TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email,password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            flash('Duplicate User', 'error')

    return render_template('signup.html')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    posts = Blog.query.all()
    return render_template('blog.html', posts=posts)
    
@app.route('/post', methods=['GET'])
def post():
    form_value = request.args.get('id')
    posts = Blog.query.filter_by(id=form_value)
    return render_template('post.html', posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    title = ""
    body = ""
    owner = User.query.filter_by(email=session['email']).first()
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if title and body:
            new_post = Blog(title, body, owner)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/post?id=' + str(new_post.id))
        else:
            flash("Please fill out both the title and body field to create your post", "error")

    return render_template('newpost.html', title=title, body=body)

@app.route('/myblog')
def myblog():
    owner = User.query.filter_by(email=session['email']).first()
    posts = Blog.query.filter_by(owner=owner).all()
    return render_template('singleUser.html', posts=posts)

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

if __name__ == '__main__':
    app.run()