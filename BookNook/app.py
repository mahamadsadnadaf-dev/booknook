from flask import Flask, render_template, request, redirect
import sqlite3
import google.generativeai as genai 
import os
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)
ai_cache = {}

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#gets cover for books
def get_book_cover(title, author):
    try:
        url = f"https://openlibrary.org/search.json?title={title}&author={author}&limit=5"
        response = requests.get(url)
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
def get_recommendations(book_name):
    prompt = f"Suggest 5 books similar to '{book_name}' with short reasons."

    response = model.generate_content(prompt)
    return response.text

#HomePage structure
@app.route('/')
def home():
    search = request.args.get('search', '')
    status = request.args.get('status','all')
    conn = sqlite3.connect('database.db')
    query = 'SELECT * FROM books WHERE 1=1'
    params = []
    if search:
        query+=" AND (title LIKE? OR author LIKE?)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")
    if status!='all':
        query+=" AND status = ?"
        params.append(status)

    books = conn.execute(query,params).fetchall()
    conn.close()
    return render_template('index.html', books=books, search=search, status=status)

#Adding book
@app.route('/add',methods=['POST'])
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
    conn = sqlite3.connect('database.db')
    conn.execute(
        'INSERT INTO books(title, author, status, image) VALUES (?,?,?,?)',
        (title, author, 'unread', image_path)
    )
    conn.commit()
    print("Inserted successfully!")

    books = conn.execute('SELECT * FROM books').fetchall()
    print("Books in DB:", books)
    conn.close()
    return redirect('/')

#Deleting the book
@app.route('/delete/<int:id>')
def delete_book(id):
    conn = sqlite3.connect('database.db')
    conn.execute('DELETE FROM books WHERE id = ?',(id,))
    conn.commit()
    conn.close()
    return redirect('/')

#Toggle book status(read/unread)
@app.route('/toggle/<int:id>')
def toggle_status(id):

    conn = sqlite3.connect('database.db')
    book = conn.execute('SELECT status FROM books WHERE id = ?',(id,)).fetchone()
    new_status='read' if book[0] == 'unread' else 'unread'
    conn.execute('UPDATE books SET status = ? WHERE id = ?',(new_status, id))
    conn.commit()
    conn.close()
    return redirect('/')

#get book recommendation
@app.route("/recommend", methods=["POST"])
def recommend():
    book = request.form["book"]

    try:
        result = get_recommendations(book)
        recommendations = []
        lines = result.split("\n")
        current_title = None
        for line in lines:
            line = line.strip()

            #detect numbered list
            if line and line[0].isdigit() and '.' in line:
                title_part = line.split('.', 1)[1].strip()
                recommendations.append({"title": title_part, "reason": ""})
            elif line.startswith("Reason:") and recommendations:
                reason_part = line.split(':', 1)[1].strip()
                recommendations[-1]["reason"] = reason_part
        return render_template("index.html", recommendations=recommendations)

    except Exception as e:
        return f"ERROR: {e}"
    
@app.route('/book/<int:id>')
def get_book(id):
    print(f"[REQUEST] Book API called with id: {id}")
    conn = sqlite3.connect('database.db')
    book = conn.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()
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

            # Clean up the response - remove markdown code blocks if present
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


