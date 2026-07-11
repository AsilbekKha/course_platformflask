from flask import Flask, request, render_template, redirect, url_for, session
from database import engine, Base, SessionLocal
from models import Course, Enrollment, CourseMaterial, User
from sqlalchemy import select, update
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload
import os
import uuid
Base.metadata.create_all(engine)
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "images")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

MATERIAL_UPLOAD_FOLDER = os.path.join(app.root_path, "static", "materials")
app.config["MATERIAL_UPLOAD_FOLDER"] = MATERIAL_UPLOAD_FOLDER

os.makedirs(app.config["MATERIAL_UPLOAD_FOLDER"], exist_ok=True)
ALLOWED_MATERIAL_EXTENSIONS = {
    "pdf",
    "txt",
    "doc",
    "docx",
    "ppt",
    "pptx",
    "zip",
    "rar",
    "mp4",
    "mp3",
    "png",
    "jpg",
    "jpeg"
}

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    )

def allowed_material(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_MATERIAL_EXTENSIONS
    )


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    db = SessionLocal()

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        username_taken = db.scalar(
            select(User).where(User.username == username)
        )

        if username_taken:
            db.close()
            return render_template(
                "register.html",
                error="Username already registered"
            )

        email_taken = db.scalar(
            select(User).where(User.email == email)
        )

        if email_taken:
            db.close()
            return render_template(
                "register.html",
                error="Email already registered"
            )

        password_hash = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role="student"
        )

        db.add(new_user)
        db.commit()
        db.close()

        return redirect(url_for("login"))

    db.close()
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    db = SessionLocal()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = db.scalar(
            select(User).where(User.username == username)
        )

        if not user:
            db.close()
            return render_template(
                "login.html",
                error="Invalid username or password"
            )

        if not check_password_hash(user.password_hash, password):
            db.close()
            return render_template(
                "login.html",
                error="Invalid username or password"
            )

        session["user_id"] = user.id

        db.close()
        return redirect(url_for("all_courses"))

    db.close()
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/all_courses")
def all_courses():
    db = SessionLocal()
    user_id = session.get("user_id")
    if user_id is None:
        db.close()
        return redirect(url_for("login"))

    user = db.get(User, user_id)

    role=user.role

    courses = (
        db.query(Course)
        .options(joinedload(Course.teacher))
        .all()
    )
    db.close()


    return render_template(
        "courses.html",
        courses=courses,
        role=role,
        user_id=user_id

    )

@app.route("/add_course", methods=["GET", "POST"])
def add_course():
    db = SessionLocal()

    user_id = session.get("user_id")

    if user_id is None:
        db.close()
        return redirect(url_for("login"))

    user = db.get(User, user_id)

    if user.role != "teacher":
        db.close()
        return "Only teachers can create courses.", 403

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]

        thumbnail = request.files.get("thumbnail")

        filename = None

        if thumbnail and thumbnail.filename != "":
            if not allowed_file(thumbnail.filename):
                db.close()
                return render_template(
                    "add_course.html",
                    error="Only PNG, JPG and JPEG images are allowed."
                )

            extension = thumbnail.filename.rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4()}.{extension}"

            thumbnail.save(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )

        course = Course(
            teacher_id=user.id,
            title=title,
            description=description,
            thumbnail=filename
        )

        db.add(course)
        db.commit()
        db.close()

        return redirect(url_for("all_courses"))

    db.close()
    return render_template("add_course.html")

@app.route("/enroll/<int:course_id>", methods=["POST"])
def enroll(course_id):
    db = SessionLocal()

    user_id = session.get("user_id")

    if user_id is None:
        db.close()
        return redirect(url_for("login"))

    user = db.get(User, user_id)

    if user.role != "student":
        db.close()
        return "Only students can enroll in courses.", 403

    existing = db.query(Enrollment).filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()

    if existing:
        db.close()
        return redirect(url_for("all_courses"))

    enrollment = Enrollment(
        user_id=user_id,
        course_id=course_id
    )

    db.add(enrollment)
    db.commit()
    db.close()

    return redirect(url_for("all_courses"))

@app.route("/edit_course/<int:course_id>", methods=["GET", "POST"])
def edit_course(course_id):
    db = SessionLocal()

    user_id = session.get("user_id")

    if user_id is None:
        db.close()
        return redirect(url_for("login"))

    user = db.get(User, user_id)

    if user.role not in ["teacher", "admin"]:
        db.close()
        return "Permission denied.", 403

    course_details = db.get(Course, course_id)

    if course_details is None:
        db.close()
        return "Course not found.", 404

    if user.role == "teacher" and course_details.teacher_id != user.id:
        db.close()
        return "You can only edit your own courses.", 403

    if request.method == "POST":
        course_details.title = request.form["title"]
        course_details.description = request.form["description"]

        thumbnail = request.files.get("thumbnail")

        if thumbnail and thumbnail.filename != "":
            if not allowed_file(thumbnail.filename):
                db.close()
                return render_template(
                    "edit_course.html",
                    course_details=course_details,
                    course_id=course_id,
                    error="Only PNG, JPG and JPEG images are allowed."
                )

            extension = thumbnail.filename.rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4()}.{extension}"

            thumbnail.save(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )

            # Delete the old thumbnail (optional)
            if course_details.thumbnail:
                old_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    course_details.thumbnail
                )
                if os.path.exists(old_path):
                    os.remove(old_path)

            # Save the new filename in the database
            course_details.thumbnail = filename

        db.commit()
        db.close()

        return redirect(url_for("all_courses"))

    return render_template(
        "edit_course.html",
        course_details=course_details,
        course_id=course_id
    )

@app.route("/delete_course/<int:course_id>", methods=["POST"])
def delete_course(course_id):
    db = SessionLocal()

    user_id = session.get("user_id")

    if user_id is None:
        db.close()
        return redirect(url_for("login"))

    user = db.get(User, user_id)

    if user.role not in ["teacher", "admin"]:
        db.close()
        return "Permission denied.", 403

    course = db.get(Course, course_id)

    if course is None:
        db.close()
        return "Course not found.", 404

    if user.role == "teacher" and course.teacher_id != user.id:
        db.close()
        return "You can only delete your own courses.", 403

    db.query(CourseMaterial).filter_by(course_id=course_id).delete()
    db.query(Enrollment).filter_by(course_id=course_id).delete()

    db.delete(course)
    db.commit()
    db.close()

    return redirect(url_for("all_courses"))

@app.route("/admin")
def admin_panel():
    db = SessionLocal()

    user_id = session.get("user_id")

    if user_id is None:
        db.close()
        return redirect(url_for("login"))

    user = db.get(User, user_id)

    if user.role != "admin":
        db.close()
        return "Access denied.", 403

    courses = db.query(Course).all()

    db.close()

    return render_template(
        "admin.html",
        courses=courses,
        role=user.role,
        user_id=user.id
    )

if __name__ == "__main__":
    app.run(debug=True, port=4200)