# ================================================================
# FINMATRIX - SQLite DATABASE
# Stores user profiles, expenses, and investment history
# ================================================================

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'finmatrix.db')

def get_db_connection():
    """Create and return database connection"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with all tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            cibil_score INTEGER DEFAULT 750,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            food REAL DEFAULT 0,
            rent REAL DEFAULT 0,
            transport REAL DEFAULT 0,
            shopping REAL DEFAULT 0,
            entertainment REAL DEFAULT 0,
            healthcare REAL DEFAULT 0,
            utilities REAL DEFAULT 0,
            month TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # User investments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            investment_type TEXT NOT NULL,
            bank_name TEXT NOT NULL,
            amount REAL NOT NULL,
            rate REAL NOT NULL,
            tenure_years INTEGER NOT NULL,
            maturity_amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Bank ratings history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bank_ratings_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bank_name TEXT NOT NULL,
            health_score REAL NOT NULL,
            rank INTEGER NOT NULL,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def save_user_expenses(user_id, expenses, month):
    """Save user's monthly expenses"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO user_expenses 
        (user_id, food, rent, transport, shopping, entertainment, healthcare, utilities, month)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, expenses.get('Food', 0), expenses.get('Rent', 0), expenses.get('Transport', 0),
          expenses.get('Shopping', 0), expenses.get('Entertainment', 0), expenses.get('Healthcare', 0),
          expenses.get('Utilities', 0), month))
    conn.commit()
    conn.close()

def get_user_expenses(user_id, month):
    """Get user's expenses for a specific month"""
    conn = get_db_connection()
    result = conn.execute('SELECT * FROM user_expenses WHERE user_id = ? AND month = ?', (user_id, month)).fetchone()
    conn.close()
    return dict(result) if result else None

def create_user(username, email, cibil_score=750):
    """Create new user"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email, cibil_score) VALUES (?, ?, ?)',
                      (username, email, cibil_score))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_user_by_username(username):
    """Retrieve user by username"""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

def update_cibil_score(user_id, new_score):
    """Update user's CIBIL score"""
    conn = get_db_connection()
    conn.execute('UPDATE users SET cibil_score = ? WHERE id = ?', (new_score, user_id))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()