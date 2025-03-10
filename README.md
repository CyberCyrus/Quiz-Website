# Quiz Website 🎯

A complete quiz platform where **users** can take quizzes and view their scores, and **admins** can create, manage quizzes, and view all user scores.

---

## 🚀 Features
### ✅ User Features:
- Register & Login securely.
- Select & attempt quizzes.
- View past scores.

### ✅ Admin Features:
- Create & manage quizzes.
- Add questions to quizzes.
- View user quiz scores.

---

## 📌 Installation Steps
Follow these steps to set up the project on your local system.

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/quiz-website.git
cd quiz-website
```

### 2️⃣ Install Dependencies
Make sure you have **Python 3.10+** installed.

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Database
Create a **MySQL Database** named `quiz_db` and run the following SQL commands:

```sql
CREATE DATABASE quiz_db;

USE quiz_db;

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE quiz (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL
);

CREATE TABLE question (
    id INT AUTO_INCREMENT PRIMARY KEY,
    quiz_id INT NOT NULL,
    question_text VARCHAR(500) NOT NULL,
    option_1 VARCHAR(200) NOT NULL,
    option_2 VARCHAR(200) NOT NULL,
    option_3 VARCHAR(200) NOT NULL,
    option_4 VARCHAR(200) NOT NULL,
    correct_option VARCHAR(200) NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quiz(id) ON DELETE CASCADE
);

CREATE TABLE user_score (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    quiz_id INT NOT NULL,
    score INT NOT NULL,
    date_taken DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (quiz_id) REFERENCES quiz(id) ON DELETE CASCADE
);
```

### 4️⃣ Configure `app.py`
Update your database credentials in `app.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://yourusername:yourpassword@localhost/quiz_db'
```

### 5️⃣ Run the Application
```bash
python app.py
```
The app will start on `http://127.0.0.1:5000`.

---

## 🛠️ Default Admin Credentials
- **Username:** `admin`
- **Password:** `admin123`

You can log in as an **admin** to manage quizzes.

---

## ❓ Troubleshooting
1️⃣ **Getting `ModuleNotFoundError`?**  
Ensure you installed all dependencies using:
```bash
pip install -r requirements.txt
```

2️⃣ **Database Connection Issue?**  
- Make sure MySQL is running.
- Check database credentials in `app.py`.

3️⃣ **Admin Panel Not Loading?**  
Try clearing browser cache or restarting the Flask server.

---

## 📜 License
This project is open-source and available under the **MIT License**.

---
