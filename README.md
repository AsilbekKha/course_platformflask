# Course Management System

A full-stack course management web application built with **Flask**, **PostgreSQL**, and **SQLAlchemy**.

The project provides separate functionality for students, teachers, and administrators, including authentication, course management, enrollment, and an admin dashboard.

---

## Features

### Authentication

* User registration
* Secure password hashing
* User login/logout
* Session-based authentication

### Student Features

* Browse available courses
* Enroll in courses
* View enrolled courses
* Access course pages

### Teacher Features

* Create new courses
* Edit owned courses
* Delete owned courses
* Upload course thumbnails

### Administrator Features

* Access admin dashboard
* Manage all courses regardless of ownership

---

## Technologies Used

* Python 3
* Flask
* SQLAlchemy ORM
* PostgreSQL
* Jinja2
* HTML5
* CSS3
* Werkzeug Security
* Alembic (Database Migrations)

---

## Project Structure

```
FlaskProject/
│
├── app.py
├── database.py
├── models.py
├── requirements.txt
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── courses.html
│   ├── add_course.html
│   ├── edit_course.html
│   └── admin.html
│
├── static/
│   ├── images/
│   ├── courses.css
│   ├── login.css
│   ├── register.css
│   ├── add_course.css
│   └── edit_course.css
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```
Before running the application, make sure you have:

Python 3.12 or newer
PostgreSQL 15 or newer
Git
Database Setup

Create a PostgreSQL database:

CREATE DATABASE course_management;

Alternatively, from the terminal:

createdb course_management

Configure your database connection in a .env file:

DATABASE_URL=postgresql://username:password@localhost/course_management
SECRET_KEY=your_secret_key
Install Dependencies
pip install -r requirements.txt
Run the Application
flask run

The application will automatically create the required database tables on first launch.

User Roles

Newly registered users are assigned the Student role by default.

To test teacher or administrator functionality, promote an account manually using PostgreSQL.

Make a user a teacher:

UPDATE users
SET role = 'teacher'
WHERE username = 'your_username';

Make a user an administrator:

UPDATE users
SET role = 'admin'
WHERE username = 'your_username';


## Current Functionality

* User authentication
* Session management
* Teacher-only course creation
* Teacher-only course editing
* Teacher-only course deletion
* Student enrollment
* Course thumbnails
* Administrator panel
* PostgreSQL database integration

---

## Future Improvements

* Course materials and file uploads
* Search functionality
* Categories and tags
* Teacher qualification requests
* Student progress tracking
* Responsive mobile interface
* Profile management

---

## License

This project was created as a personal educational and portfolio project.
