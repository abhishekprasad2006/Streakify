# Streakify API 

A habit tracking REST API built with **FastAPI** and **PostgreSQL**.

> "Help people build life-changing habits through streak psychology, smart tracking, and productivity insights."

---

##  Technology Stack

| Technology | Purpose |
|------------|---------|
| Python 3.13 | Programming language |
| FastAPI | REST API framework |
| PostgreSQL | Database |
| SQLAlchemy | ORM (database connection) |
| Pydantic | Data validation |
| Uvicorn | ASGI server |
| Postman | API testing |

---

##  Project Structure

```
Streakify/
├── main.py                   # App entry point, registers all routers
├── database.py               # PostgreSQL connection setup
├── models.py                 # Database table definitions
├── schemas.py                # Request/Response data shapes
├── .env                      # Environment variables (DB credentials)
│
├── routers/
│   ├── __init__.py
│   ├── users.py              # User endpoints
│   ├── habits.py             # Habit endpoints
│   ├── logs.py               # Habit log endpoints
│   └── streak.py             # Streak endpoint
│
├── services/
│   ├── __init__.py
│   ├── user_service.py       # User business logic
│   ├── habit_service.py      # Habit business logic
│   ├── log_service.py        # Log business logic
│   ├── streak_service.py     # Streak calculation logic
│   └── dashboard_service.py  # Dashboard logic
│
└── repositories/
    ├── __init__.py
    ├── user_repo.py          # User DB queries
    ├── habit_repo.py         # Habit DB queries
    └── log_repo.py           # Log DB queries
```

---

##  Setup Steps

### 1. Clone the repository
```bash
git clone https://github.com/abhishekprasad2006/streakify.git
cd streakify
```

### 2. Create a virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pydantic[email]
```

### 4. Create the database
Open pgAdmin and create a database called `streakify_db`

### 5. Configure environment
Create a `.env` file in the root folder:
```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/streakify_db
```

### 6. Run the server
```bash
python -m uvicorn main:app --reload
```

### 7. Open API docs
Visit: http://127.0.0.1:8000/docs

---

##  Database Design

### Users Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | Primary Key, Auto Increment |
| name | String(100) | Not Null |
| email | String(255) | Unique, Not Null |
| created_at | DateTime | Default: Current Time |

### Habits Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | Primary Key, Auto Increment |
| name | String(100) | Not Null |
| target_days_per_week | Integer | Not Null |
| user_id | Integer | Foreign Key → users.id |
| is_active | Boolean | Default: True |
| created_at | DateTime | Default: Current Time |

### Habit Logs Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | Primary Key, Auto Increment |
| habit_id | Integer | Foreign Key → habits.id |
| log_date | Date | Not Null |
| completed | Boolean | Default: False |
| created_at | DateTime | Default: Current Time |
| — | — | Unique(habit_id, log_date) |

---

##  API Endpoints

### Users
| Method | URL | Description | Status Code |
|--------|-----|-------------|-------------|
| POST | /users | Create a user | 201 |
| GET | /users/{id} | Get user profile | 200 |
| DELETE | /users/{id} | Delete user | 200 |

### Habits
| Method | URL | Description | Status Code |
|--------|-----|-------------|-------------|
| POST | /habits | Create a habit | 201 |
| GET | /users/{id}/habits | Get all habits for user | 200 |
| DELETE | /habits/{id} | Delete a habit | 200 |

### Habit Logs
| Method | URL | Description | Status Code |
|--------|-----|-------------|-------------|
| POST | /habits/{id}/logs | Log a habit for a date | 201 |
| PUT | /habits/{id}/logs/{date} | Update a log | 200 |
| GET | /habits/{id}/logs | Get all logs for a habit | 200 |

### Streak & Dashboard
| Method | URL | Description | Status Code |
|--------|-----|-------------|-------------|
| GET | /habits/{id}/streak | Get current and longest streak | 200 |
| GET | /users/{id}/dashboard | Get full productivity dashboard | 200 |

---

##  Sample Requests & Responses

### Create User
**Request:**
```json
POST /users
{
    "name": "Abhishek",
    "email": "abhishek@test.com"
}
```
<img width="1566" height="935" alt="Create user  201 response" src="https://github.com/user-attachments/assets/00405729-c161-47fe-af59-9f18ba6c3bef" />


```

Create Habit

```
<img width="1570" height="949" alt="Create user" src="https://github.com/user-attachments/assets/bf92ed42-9b12-4b24-be98-3d03b8c18f4a" />

```


 Log a Habit
```
<img width="1575" height="950" alt="habit loging 1" src="https://github.com/user-attachments/assets/76a2b8e6-60f5-4229-908a-7ade16e4178d" />

```

### Get Streak
```
<img width="1540" height="926" alt="image" src="https://github.com/user-attachments/assets/0f364fc0-9364-419a-b908-47255f19049a" />
```
### Get Dashboard
```
<img width="1576" height="993" alt="Habit daashboard" src="https://github.com/user-attachments/assets/1d611109-0e14-4d2e-b1c9-63facd328d00" />
```

##  Business Rules

- Cannot log the same habit twice on the same day
- Cannot log future dates
- Streak resets if a day is missed
- Deleting a user automatically deletes all their habits and logs
- Deleting a habit automatically deletes all its logs
- Target days per week must be between 1 and 7
- Email must be in valid format

---

##  Streak Calculation Logic

**Current Streak** — counts consecutive days from today backwards:
- Start from today
- Walk backwards day by day
- If a completed log exists → count increases
- If a day is missing → stop counting

**Longest Streak** — finds the longest consecutive run in history:
- Sort all completed logs oldest to newest
- Walk through checking if each day follows the previous
- Track the longest consecutive run found


---

##  Error Responses

| Status Code | Meaning | Example |
|-------------|---------|---------|
| 400 | Bad Request | Duplicate log, future date, email already registered |
| 404 | Not Found | User or habit doesn't exist |
| 422 | Validation Error | Invalid email format |

---

##  Architecture

```
Postman Request
      ↓
  Routers        ← receives HTTP request
      ↓
  Services       ← validates business rules
      ↓
  Repositories   ← queries the database
      ↓
  PostgreSQL     ← stores the data
```

---
##  Built By
- **Name:** Abhishek Prasad
- **GitHub:** [abhishekprasad2006](https://github.com/abhishekprasad2006)
- **Date:** April 2026

##  Repository
[https://github.com/abhishekprasad2006/streakify](https://github.com/abhishekprasad2006/streakify)
