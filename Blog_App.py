#Course Project

from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug.security import check_password_hash
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = 'IS211_CourseProject'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('blog_db',detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view(**kwargs)

    return wrapped_view

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM Users WHERE username = ?', (username,)).fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            return redirect(url_for('dashboard'))
        else:
            error = 'Incorrect username or password'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    posts = db.execute(
        'SELECT * FROM Posts WHERE author_id = ? ORDER BY date_published DESC',
        (session['user_id'],)
    ).fetchall()
    return render_template('dashboard.html', posts=posts)

@app.route('/post/add', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author_id = session['user_id']

        db = get_db()
        db.execute('INSERT INTO Posts (title, content, author_id) VALUES (?, ?, ?)', (title, content, author_id))
        db.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_post.html')

@app.route('/post/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    db = get_db()
    post = db.execute('SELECT * FROM Posts WHERE post_id = ?', (id,)).fetchone()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        db.execute('UPDATE Posts SET title = ?, content = ? WHERE post_id = ?', (title, content, id))
        db.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_post.html', post=post)

@app.route('/post/delete/<int:id>', methods=['POST'])
@login_required
def delete_post(id):
    db = get_db()
    db.execute('DELETE FROM Posts WHERE post_id = ?', (id,))
    db.commit()
    return redirect(url_for('dashboard'))

@app.route('/post/<int:id>')
def post(id):
    db = get_db()
    post = db.execute('SELECT * FROM Posts WHERE post_id = ?', (id,)).fetchone()
    comments = db.execute('SELECT * FROM Comments WHERE post_id = ? ORDER BY date_commented DESC', (id,)).fetchall()
    return render_template('post.html', post=post, comments=comments)

@app.route('/comment/add/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    content = request.form['content']
    author_id = session.get('user_id')
    if author_id:
        db = get_db()
        db.execute('INSERT INTO Comments (post_id, author_id, content) VALUES (?, ?, ?)', (post_id, author_id, content))
        db.commit()
    return redirect(url_for('post', id=post_id))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/')
def index():
    db = get_db()
    posts = db.execute('SELECT * FROM Posts ORDER BY date_published DESC').fetchall()
    return render_template('index.html', posts=posts)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()


if __name__ == '__main__':
    app.run(debug=True)