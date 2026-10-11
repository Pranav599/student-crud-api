"""Students Database CRUD API - FastAPI + SQLite."""
import sqlite3
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, model_validator

DB_PATH = "students.db"
app = FastAPI(title="Students CRUD API")


# ---------- Database helpers ----------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us read rows like dictionaries
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                course TEXT,
                address TEXT,
                enrollment_date TEXT
            )"""
        )


init_db()


# ---------- Data models (validation) ----------
EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
PHONE_PATTERN = r"^\+?[0-9\- ]{7,15}$"


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    date_of_birth: date  # format: YYYY-MM-DD
    email: Optional[str] = Field(default=None, pattern=EMAIL_PATTERN)
    phone: Optional[str] = Field(default=None, pattern=PHONE_PATTERN)
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None

    @model_validator(mode="after")
    def need_contact(self):
        if not self.email and not self.phone:
            raise ValueError("Provide at least an email or a phone number")
        return self


class StudentUpdate(BaseModel):
    """All fields optional, so you can update just one thing."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[str] = Field(default=None, pattern=EMAIL_PATTERN)
    phone: Optional[str] = Field(default=None, pattern=PHONE_PATTERN)
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None


class Student(StudentCreate):
    id: int


# ---------- Endpoints ----------
@app.post("/students", response_model=Student, status_code=201)
def create_student(student: StudentCreate):
    data = student.model_dump(mode="json")  # dates become "YYYY-MM-DD" strings
    cols = ", ".join(data)
    marks = ", ".join("?" for _ in data)
    try:
        with get_conn() as conn:
            cur = conn.execute(
                f"INSERT INTO students ({cols}) VALUES ({marks})", list(data.values())
            )
            new_id = cur.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email already exists")
    return {"id": new_id, **data}


@app.get("/students", response_model=list[Student])
def list_students(
    name: Optional[str] = Query(None, description="Partial name match"),
    course: Optional[str] = None,
    born_after: Optional[date] = Query(None, description="YYYY-MM-DD"),
):
    query, params = "SELECT * FROM students WHERE 1=1", []
    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
    if course:
        query += " AND course = ?"
        params.append(course)
    if born_after:
        query += " AND date_of_birth > ?"
        params.append(born_after.isoformat())
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return dict(row)


@app.patch("/students/{student_id}", response_model=Student)
def update_student(student_id: int, changes: StudentUpdate):
    data = changes.model_dump(mode="json", exclude_unset=True)  # only sent fields
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    sets = ", ".join(f"{k} = ?" for k in data)
    try:
        with get_conn() as conn:
            cur = conn.execute(
                f"UPDATE students SET {sets} WHERE id = ?", [*data.values(), student_id]
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Student not found")
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email already exists")
    return get_student(student_id)


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": f"Student {student_id} deleted"}
