# 📅 MINDSET ARCHITECTURE

## 📝 Overview of the Project

A lightweight web application built with Python's Flask framework designed to provide users with a dual-purpose tool: managing mental health and monitoring mental wellness. It uses a simple SQLite database for persistence, making it easy to run locally.
## ✨ Features
User Authentication: Secure login and registration for patients.

Project Dashboard: Secure first interaction page.

Resource Hub: Packages like flask, sqlalachemy and env file for secure transmission.

Collaboration Tools: Integrated Open AI tool.

Progress Tracking: Helps users to track their progress on their mental health.

**History:** View all past wellness entries on the tracker page.

## 💻 Technologies/Tools Used

**Backend Framework:** Flask (Python)

**Database:** SQLite (*Managed via SQLAlchemy*)

**ORM:** Flask-SQLAlchemy

**Templating:** HTML templates (index.html, home.html, login.html, exercises.html).

## ⚙️ Steps to Install & Run the Project

Follow these steps to get the application running on your local machine.

Prerequisites

Python 3.8+

### 1. Clone the Repository

git clone(https://github.com/Priyansh-Shadowcoder/innovit.git


### 2. Create and Activate a Virtual Environment

**Create environment**
python -m venv venv

**Activate on macOS/Linux**
source venv/bin/activate

**Activate on Windows (Command Prompt)**
venv\Scripts\activate


### 3. Install Dependencies

pip install Flask Flask-SQLAlchemy


### 4. Run the Application

The database (health.db) and tables will be created automatically on the first run.

python app.py

