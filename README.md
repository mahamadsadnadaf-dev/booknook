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

#screenshots:
<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/aa69995b-ee05-45a3-b221-c069202cc9ce" />
<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/3de755b0-b6fc-40ac-ba69-cfcf0742fd42" />
<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/f6564f35-4ad3-4421-838e-d3731af69fc2" />
<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/508195c4-546d-45b2-a0d8-9e6e75e07b3e" />
<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/5249ca1e-5f24-43e0-94aa-92171e44c286" />





⭐ If you like this project, consider giving it a star!
