import sqlite3
from typing import List, Tuple, Any

DB_PATH = "analytics_sandbox.db"

def init_db():
    """Initializes the database with sample SaaS data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create Customers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        region TEXT NOT NULL,
        signup_date DATE NOT NULL,
        tier TEXT NOT NULL
    );
    """)
    
    # Create Transactions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        amount DECIMAL(10, 2) NOT NULL,
        transaction_date DATE NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    );
    """)
    
    # Seed Data
    cursor.execute("DELETE FROM customers;")
    cursor.execute("DELETE FROM transactions;")
    
    customers = [
        (1, "Acme Corp", "EMEA", "2025-01-15", "Enterprise"),
        (2, "Starlight AI", "NAMER", "2025-02-10", "Pro"),
        (3, "Nebula Systems", "EMEA", "2025-03-01", "Enterprise"),
        (4, "Quantum Devs", "APAC", "2025-03-20", "Basic"),
        (5, "Cybernetics Inc", "NAMER", "2025-04-05", "Pro")
    ]
    
    transactions = [
        (101, 1, 12000.00, "2025-04-15", "Completed"),
        (102, 2, 1500.00, "2025-04-18", "Completed"),
        (103, 3, 15000.00, "2025-04-20", "Completed"),
        (104, 1, 12000.00, "2025-05-15", "Completed"),
        (105, 4, 300.00, "2025-05-22", "Failed"),
        (106, 5, 1500.00, "2025-06-01", "Completed"),
        (107, 3, 15000.00, "2025-06-20", "Completed"),
        (108, 2, 1500.00, "2025-06-25", "Refunded")
    ]
    
    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?);", customers)
    cursor.executemany("INSERT INTO transactions VALUES (?, ?, ?, ?, ?);", transactions)
    
    conn.commit()
    conn.close()

def get_schema() -> str:
    """Reflects the database schema and returns DDL as a string."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return "\n\n".join([t[0] for t in tables if t[0] is not None])

def execute_query(sql: str) -> Tuple[List[Tuple[Any, ...]], str]:
    """
    Executes an SQL query safely.
    Returns: (results, error_message)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.commit()
        return results, ""
    except Exception as e:
        return [], str(e)
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")