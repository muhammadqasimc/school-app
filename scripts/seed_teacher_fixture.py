from datetime import datetime

from app import app, db, User, UserTeacherAssignment


def seed():
    with app.app_context():
        user = User.query.filter_by(educator_id="TCH001").first()
        if not user:
            user = User(
                username="teacher_tch001",
                password_hash="pbkdf2:placeholder",
                first_login=True,
                is_teacher=True,
                educator_id="TCH001",
                teacher_role="Teacher",
                teacher_status="Active",
            )
            db.session.add(user)
            db.session.commit()
        existing = UserTeacherAssignment.query.filter_by(
            user_id=user.id, class_id="GRADE9A", subject="Mathematics", academic_year=str(datetime.now().year)
        ).first()
        if not existing:
            db.session.add(UserTeacherAssignment(
                user_id=user.id,
                class_id="GRADE9A",
                grade="9",
                subject="Mathematics",
                academic_year=str(datetime.now().year),
                is_active=True,
            ))
            db.session.commit()
        print("Teacher fixture ready:", user.id)


if __name__ == "__main__":
    seed()
