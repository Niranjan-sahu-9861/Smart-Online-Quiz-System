# Smart Online Quiz System

## 📌 Project Overview
Smart Online Quiz System is a web-based quiz application built using **Flask (Python), HTML, CSS, and JavaScript**. The system allows users to register, log in, and attempt quizzes, while an admin can create quizzes and view basic analytics.

This project demonstrates core concepts of web development, user authentication, and backend logic using Python.

---

## 🚀 Features

### 👨‍🎓 Student Features:
- Register with username and password  
- Login securely  
- View available quizzes  
- Attempt quizzes with a timer  
- Automatic evaluation of answers  
- View score and performance report  
- See leaderboard based on performance  

### 👨‍💼 Admin Features:
- Create new quizzes  
- Add multiple-choice questions  
- Set time limits and marks  
- View overall quiz analytics  

---

## 🛠️ Technologies Used

### Backend:
- Python  
- Flask Framework  

### Frontend:
- HTML  
- CSS  
- JavaScript  

### Data Handling:
- SQLite (or in-memory structures) -- can be extended as needed

---

## 📁 Project Structure (Basic)

```
Quiz_app/
│
├── app.py
├── database.db
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── quiz_list.html
│   ├── create_quiz.html
│   ├── add_question.html
│   └── take_quiz.html
│
└── static/
    └── style.css
```

---

## ▶️ How to Run the Project

1. Install required dependencies:
```
pip install flask
```

2. Run the application:
```
python app.py
```

3. Open browser and go to:
```
http://127.0.0.1:5000/
```

---

## 🔐 Default Admin Credentials (For Testing)

```
Username: admin  
Password: 123
```

---

## 🎯 Future Enhancements

- Connect to **SQLite / MySQL database** (if using in-memory now)
- Add **profile management**
- Implement **password encryption**
- Add **quiz categories**
- Add **result history for each student**
- Improve UI with animations and better design  

---

## 👨‍💻 Developed By

**Niranjan Sahu**  
B.Tech (CSIT)  
Aspiring Software Developer  

---

## ⭐ Acknowledgment

Thanks to Flask and open-source community for providing excellent learning resources.
