# Students Database CRUD API

A backend app to manage student records, built with **Python, FastAPI and SQLite**.

## Prerequisites
- Python 3.9+

## Installation
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run
```bash
uvicorn main:app --reload
```
The API runs at http://127.0.0.1:8000. The SQLite file `students.db` is created automatically.

## Test the API
Open **http://127.0.0.1:8000/docs** (interactive Swagger UI) and try each endpoint, or use curl:

```bash
# Create
curl -X POST http://127.0.0.1:8000/students -H "Content-Type: application/json" \
  -d '{"name":"Asha Rao","date_of_birth":"2005-03-14","email":"asha@example.com","course":"Python"}'

# List / filter
curl http://127.0.0.1:8000/students
curl "http://127.0.0.1:8000/students?course=Python&born_after=2004-01-01"

# View one
curl http://127.0.0.1:8000/students/1

# Update
curl -X PATCH http://127.0.0.1:8000/students/1 -H "Content-Type: application/json" \
  -d '{"course":"FastAPI"}'

# Delete
curl -X DELETE http://127.0.0.1:8000/students/1
```

## Endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| POST | /students | Create a student |
| GET | /students | List / filter (`name`, `course`, `born_after`) |
| GET | /students/{id} | View a student |
| PATCH | /students/{id} | Update details |
| DELETE | /students/{id} | Delete a student |

## Validation & errors
- Name and date of birth required; at least one of email/phone required
- 404 if the student doesn't exist, 409 if the email is duplicate, 422 for invalid input

Only dummy data is used. No real student information is stored in this repo.
