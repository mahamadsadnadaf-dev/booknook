from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
import google.generativeai as genai
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from urllib.parse import quote
from functools import wraps

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
ai_cache = {}

DATABASE_PATH = 'database.db'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_db_connection():
    return sqlite3.connect(DATABASE_PATH)


def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'unread',
            image TEXT,
            user_id INTEGER
        )
    ''')
    columns = [row[1] for row in conn.execute("PRAGMA table_info(books)").fetchall()]
    if 'user_id' not in columns:
        conn.execute('ALTER TABLE books ADD COLUMN user_id INTEGER')
    conn.commit()
    conn.close()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped_view


init_db()

#gets cover for books
def get_book_cover(title, author):
    try:
        url = f"https://openlibrary.org/search.json?title={quote(title)}&author={quote(author)}&limit=5"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        for book in data.get("docs", []):
            cover_id = book.get("cover_i")
            if cover_id:
                return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

    except Exception as e:
        print("Error fetching cover:", e)

    return None

#API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def get_recommendations(user_id):
    conn = get_db_connection()
    books = conn.execute('SELECT title, author FROM books WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()

    if not books:
        return []

    book_list = "\n".join([f"- {title} by {author}" for title, author in books])
    prompt = f"""Based on this user's book library:

                    {book_list}

                    Suggest 5 books they would enjoy. For each recommendation, provide the book title and a brief reason why.

                    Format your response as a numbered list with this exact format:
                    1. Title: [Book Title]
                    Reason: [Why they would enjoy it]

                    2. Title: [Book Title]
                    Reason: [Why they would enjoy it]

                    And so on."""

    response = model.generate_content(prompt)
    recommendations = []
    lines = response.text.strip().split("\n")

    current_rec = None
    for line in lines:
        line = line.strip()
        if line.startswith("Title:"):
            if current_rec and "title" in current_rec:
                recommendations.append(current_rec)
            title = line.replace("Title:", "").strip()
            current_rec = {"title": title, "reason": ""}
        elif line.startswith("Reason:") and current_rec:
            reason = line.replace("Reason:", "").strip()
            current_rec["reason"] = reason

    if current_rec and "title" in current_rec:
        recommendations.append(current_rec)

    return recommendations[:5]

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if not username or not password:
            flash('Username and password are required.')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                         (username, hashed_password))
            conn.commit()
            user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
            session['user_id'] = user[0]
            session['username'] = username
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose another.')
            return redirect(url_for('signup'))
        finally:
            conn.close()

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT id, password FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            return redirect(url_for('home'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


#HomePage structure

@app.route('/')
def home():
    search = request.args.get('search', '')
    status = request.args.get('status','all')
    books = []

    if 'user_id' in session:
        conn = get_db_connection()
        query = 'SELECT * FROM books WHERE user_id = ?'
        params = [session['user_id']]
        if search:
            query += " AND (title LIKE ? OR author LIKE ? )"
            params.append(f"%{search}%")
            params.append(f"%{search}%")
        if status != 'all':
            query += " AND status = ?"
            params.append(status)

        books = conn.execute(query, params).fetchall()
        conn.close()

    return render_template('index.html', books=books, search=search, status=status, username=session.get('username'))

#Adding book
@app.route('/add',methods=['POST'])
@login_required
def add_book():
    title = request.form['title']
    author = request.form['author']
    file = request.files.get('image')

    image_path = None

    if file and file.filename != '':
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        image_path = filepath  # store this in DB
    else:
        image_path = get_book_cover(title,author)
    print("Received : ", title, author)
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO books(title, author, status, image, user_id) VALUES (?,?,?,?,?)',
        (title, author, 'unread', image_path, session['user_id'])
    )
    conn.commit()
    print("Inserted successfully!")

    books = conn.execute('SELECT * FROM books').fetchall()
    print("Books in DB:", books)
    conn.close()
    return redirect('/')

#Deleting the book
@app.route('/delete/<int:id>')
@login_required
def delete_book(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ? AND user_id = ?',(id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/')

#Toggle book status(read/unread)
@app.route('/toggle/<int:id>')
@login_required
def toggle_status(id):

    conn = get_db_connection()
    book = conn.execute('SELECT status FROM books WHERE id = ? AND user_id = ?',(id, session['user_id'])).fetchone()
    if book:
        new_status='read' if book[0] == 'unread' else 'unread'
        conn.execute('UPDATE books SET status = ? WHERE id = ? AND user_id = ?',(new_status, id, session['user_id']))
        conn.commit()
    conn.close()
    return redirect('/')

#get book recommendation
@app.route("/recommend", methods=["POST"])
@login_required
def recommend():
    try:
        recommendations = get_recommendations(session['user_id'])
        conn = get_db_connection()
        books = conn.execute('SELECT * FROM books WHERE user_id = ?', (session['user_id'],)).fetchall()
        conn.close()
        return render_template("index.html", books=books, recommendations=recommendations, search='', status='all', username=session.get('username'))

    except Exception as e:
        print(f"Recommendation error: {e}")
        flash('Unable to generate recommendations at this time. API limit reached.')
        return redirect(url_for('home'))
    
@app.route('/book/<int:id>')
@login_required
def get_book(id):
    print(f"[REQUEST] Book API called with id: {id}")
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ? AND user_id = ?', (id, session['user_id'])).fetchone()
    conn.close()

    if not book :
        print("[ERROR] Book not found")
        return {"error": "Book not found"}, 404

    title = book[1]
    author = book[2]

    key = f"{title.strip().lower()}_{author.strip().lower()}" 

    if key in ai_cache:
        print("[CACHE] Serving from cache")
        return ai_cache[key]
        

    try:
        prompt = f"""
        Provide detailed information about the book '{title}' by {author}.
        
        Return ONLY a valid JSON object with exactly these three keys:
        {{
          "description": "A brief summary of the book's plot",
          "characters": "Main characters in the book",
          "genre": "The primary genre of the book"
        }}
        
        Do not include any other text, explanations, or formatting. Just the JSON.
        """

        response = model.generate_content(prompt)
        print("[AI] Response received")

        import json

        try:
            raw = response.text.strip()
            print("[AI RAW]:", raw)   

            if raw.startswith('```json'):
                raw = raw[7:]
            if raw.startswith('```'):
                raw = raw[3:]
            if raw.endswith('```'):
                raw = raw[:-3]
            raw = raw.strip()

            ai_data = json.loads(raw)

        except Exception as e:
            print("Gemini parse error:", e)
            print("Raw response:", repr(raw))

            ai_data = {
                "description": "Could not parse AI response",
                "characters": "-",
                "genre": "-"
            }

    except Exception as e:
        print("Gemini error:", e)

        ai_data = {
            "description": "Error",
            "characters": "Error",
            "genre": "Error"
        }

    result = {
        "title": title,
        "author": author,
        "image": book[4],
        "details": ai_data
    }

    ai_cache[key] = result
    print("[DONE] Sending response to frontend\n")
    return result

if __name__=='__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)


