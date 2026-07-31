# Here this file is essentially our database layer for this app. 
# It sets up and manages a lightweight SQLite database (data.db) to store users and their workout activity.



# Imports Python’s built-in SQLite library. This lets you create and interact with a lightweight relational database stored in a single file (data.db).
import sqlite3
import streamlit as st

# Imports the Path class from Python’s pathlib module. Provides a clean, cross-platform way to handle file paths (better than string concatenation).
from pathlib import Path

_DB_PATH = str(Path(__file__).parent.parent.parent / "data.db")
# __file__ → The path of the current Python file.
# .parent → Moves one directory up.
# .parent.parent.parent → Moves three directories up from the current file’s location.
# / "data.db" → Appends "data.db" to that path.
# str(...) → Converts the Path object into a string, since sqlite3.connect() expects a string path.



# In Python, a single leading underscore (e.g., _get_connection) is a naming convention that signals: “This function/variable is intended for internal use only.” It’s not part of the public API of the module.
# Other developers should treat it as private and avoid calling it directly unless they know what they’re doing
# _get_connection() is a helper function that sets up and caches the SQLite connection.
# It’s not meant to be called directly by end users of your app. Instead, higher-level functions like init_db(), get_user(), or add_exercise() call it internally.
# The underscore signals: “Don’t use this outside of this file/module—it’s an implementation detail.”

# This function is responsible for creating and caching a database connection to our SQLite file (data.db) so our Streamlit app can interact with it efficiently.
@st.cache_resource
def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Thread :-
# A thread is a logical branch of the program which can be executed in parallel with other threads of the same program.
# By default, SQLite enforces that a connection can only be used in the same thread where it was created.
# If you try to use the connection from another thread, you’ll get an error.
# Streamlit reruns your script whenever the UI changes (e.g., user input). These reruns may happen in different threads.
# If you used the default check_same_thread=True, your cached connection would break when accessed from another thread.
# What check_same_thread=False Does :-
# It disables the thread check, allowing the same connection object to be shared across multiple threads.
# This is necessary in Streamlit apps because:
# The app reruns frequently.
# Cached resources (like your database connection) need to be reused safely across reruns.
# Without it, you’d constantly hit threading errors when trying to query the database.


# @st.cache_resource :-
# A Streamlit decorator that caches the result of the function. Ensures the database connection is created only once and reused across reruns of the app. 
# Prevents multiple redundant connections, which could slow down or break the app.

# def _get_connection() -> sqlite3.Connection :-
# Defines a helper function that returns a SQLite connection object.
# The return type annotation (sqlite3.Connection) makes it clear what kind of object is expected.

# conn = sqlite3.connect(_DB_PATH, check_same_thread=False) :-
# Opens a connection to the SQLite database file located at _DB_PATH.
# check_same_thread=False: By default, SQLite restricts connections to the thread that created them.
# Streamlit reruns code in different threads, so this flag allows the connection to be shared safely across threads.

# conn.row_factory = sqlite3.Row :- 
# Configures the connection so query results are returned as Row objects.
# This means you can access columns by name (like a dictionary) instead of only by index.
# e.g row = conn.execute("SELECT * FROM users").fetchone()
# print(row["username"])  # Access by column name & not like row[0] or row[1]



# It is the starting point for initializing our database in the app
def init_db() -> None:
    conn = _get_connection()

    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS exercises (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL REFERENCES users(id),
                exercise_name TEXT    NOT NULL,
                reps          INTEGER NOT NULL DEFAULT 0,
                sets          INTEGER NOT NULL DEFAULT 0,
                time          INTEGER NOT NULL DEFAULT 0,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )




# This function is our user lookup helper. It queries the database to check if a given username exists in the users table and returns the corresponding row.
# Return type annotation → sqlite3.Row, meaning the function will return a single row from the database.
def get_user(username: str) -> sqlite3.Row:
    conn = _get_connection()

    return conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    # conn.execute("SELECT * FROM users WHERE username = ?", (username,)) :-
    # Executes an SQL query to select all columns (*) from the users table where the username matches the provided value.
    # Uses parameter substitution (?):
    ## Prevents SQL injection attacks.
    ## (username,) is a tuple containing the value to substitute.

    # .fetchone() :-
    # Retrieves the first matching row from the query result.
    # If a user with that username exists → returns a sqlite3.Row object.
    # If no match is found → returns None.




def create_user(username: str) -> sqlite3.Row:
    conn = _get_connection()
    
    with conn:
        conn.execute(
            "INSERT INTO users (username) VALUES (?)", (username,)
        )

    # conn.execute("INSERT INTO users (username) VALUES (?)", (username,)) :-
    # Executes an SQL INSERT statement to add a new user. ? is a placeholder for parameter substitution (prevents SQL injection).
    # (username,) is a tuple containing the actual username value.
    # The users table automatically assigns:
    # id → auto-increment primary key.
    # created_at → defaults to the current timestamp.

    return get_user(username) 




def get_or_create_user(username: str) -> sqlite3.Row:
    user = get_user(username)

    if user is None:
        user = create_user(username)
    
    return user




def add_exercise(user_id, exercise_name, reps, sets, time):
    conn = _get_connection()

    with conn:
        # Checks if there’s already an exercise record for this user, exercise name, and today’s date.
        existing = conn.execute("""
            SELECT * FROM exercises 
            WHERE user_id = ? AND exercise_name = ? AND Date('created_at') = Date('now')
        """, (user_id, exercise_name)).fetchone()

        if existing:
            conn.execute("""
                UPDATE exercises 
                SET reps = reps + ?, sets = sets + ?, time = time + ?
                WHERE id = ?
            """, (reps, sets, time, existing['id']))
        else:
            conn.execute("""
                INSERT INTO exercises (user_id, exercise_name, sets, reps, time)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, exercise_name, sets, reps, time))




def get_users_exercises(user_id):
    conn = _get_connection()

    return conn.execute("""
        SELECT * FROM exercises 
        WHERE user_id = ?
    """, (user_id,)).fetchall()