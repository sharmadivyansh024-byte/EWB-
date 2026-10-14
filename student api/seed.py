"""Load dummy (fake) students for testing. Run: python seed.py"""
from datetime import date

from app import crud
from app.database import init_db

DUMMY = [
    ("Aarav Sharma", "2004-03-15", "aarav@example.com", "9876500001", "Python Backend", "2024-06-01"),
    ("Diya Patel", "2005-07-22", "diya@example.com", "9876500002", "Data Science", "2024-06-01"),
    ("Rohan Mehta", "2006-01-09", "rohan@example.com", None, "Python Backend", "2024-07-10"),
    ("Sneha Iyer", "2003-11-30", "sneha@example.com", "9876500004", "Web Development", "2023-08-15"),
    ("Kabir Singh", "2007-05-18", None, "9876500005", "Data Science", "2025-01-05"),
]

if __name__ == "__main__":
    init_db()
    for name, dob, email, phone, course, enrolled in DUMMY:
        try:
            crud.create_student({"name": name, "date_of_birth": date.fromisoformat(dob),
                                 "email": email, "phone": phone, "course": course,
                                 "enrollment_date": date.fromisoformat(enrolled)})
            print("Added", name)
        except crud.IntegrityError:
            print("Skipped (already exists):", name)
