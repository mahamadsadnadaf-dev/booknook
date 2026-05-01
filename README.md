# 📚 BookNook

A full-stack web application for managing your personal reading list with AI-powered book insights and recommendations.

---

✨ Features

🔐 Authentication
- User signup and login system
- Session-based authentication
- Protected routes for user-specific data

📖 Book Management
- Add and delete books
- Toggle reading status (Read / Unread)
- Instant book search

🤖 AI Integration (Gemini API)
- Click on a book to get AI-generated insights
- Personalized book recommendations
- Intelligent responses based on user activity

🎨 UI/UX
- Clean, responsive design
- Dark mode / Light mode toggle
- Interactive book cards

---

## 🧠 How It Works

1. User logs in
2. Adds books to their collection
3. Clicking a book triggers AI-generated information
4. Recommendation system suggests books based on context
5. Data is dynamically rendered per user

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask (Python) |
| Frontend | HTML, CSS, Tailwind CSS, JavaScript |
| Database | SQLite |
| AI | Google Gemini API |

---

## ⚙️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/mahamadsadnadaf-dev/booknook.git
cd booknook
```

### 2. Create a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add environment variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_api_key_here
```

### 5. Run the app
```bash
python app.py
```

---

## 📁 Project Structure

```
booknook/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
└── static/
    ├── css/
    └── uploads/
```

---

## ⚠️ Note on AI Usage

- The app uses the Gemini API (free tier)
- The API has limited daily requests
- If the limit is reached, fallback messages are shown

---

## 🔥 Future Improvements

- Persistent recommendation storage (DB caching)
- Better rate-limit handling for AI
- Enhanced UI animations

---

## 📣 Author

**Mahamadsad Nadaf**

---

## 💡 Project Purpose

This project demonstrates:
- Full-stack development
- Authentication systems
- CRUD operations
- API integration
- Real-world problem solving

---

⭐ If you like this project, consider giving it a star!
