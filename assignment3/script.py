import mysql.connector
import time

# ---Made with help of code shown on Practical Training---
# --- Database Connection Details ---
DB_NAME = "assignment3"
DB_USER = "root"
DB_PASSWORD = "Aa123456"
DB_HOST = "localhost"
DB_PORT = 3306


# --- Helper Functions ---

def get_connection(isolation_level_str: str):
    """Establishes a database connection with a specified isolation level."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        # Set the isolation level for this connection
        if isolation_level_str == "READ UNCOMMITTED":
            conn.autocommit = False  # Important for transactions
            conn.cmd_query(f"SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;")
            print(f"[INFO] Connection set to READ UNCOMMITTED.")
        elif isolation_level_str == "READ COMMITTED":
            conn.autocommit = False  # Important for transactions
            conn.cmd_query(f"SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
            print(f"[INFO] Connection set to READ COMMITTED.")
        elif isolation_level_str == "REPEATABLE READ":
            conn.autocommit = False
            conn.cmd_query(f"SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
            print(f"[INFO] Connection set to REPEATABLE READ.")
        else:
            raise ValueError(f"Unsupported isolation level: {isolation_level_str}")
        return conn
    except mysql.connector.Error as e:
        print(f"[ERROR] Could not connect to database: {e}")
        exit(1)

def fetch_status(conn, customer_name: str):
    """Fetches and prints the status for a particular order."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM orders WHERE customer_name = %s", (customer_name,))
            status = cur.fetchone()
            if status:
                print(f"[INFO] {customer_name}'s order status: {status[0]}")
            else:
                print(f"[ERROR] {customer_name}'s order not found.")
            return status[0] if status else None
    except mysql.connector.Error as e:
        print(f"[ERROR] Error fetching status: {e}")
        return None

def update_status(conn, customer_name: str, status: str):
    """Updates the order status for a given customer."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE orders SET status = %s WHERE customer_name = %s",
                (status, customer_name)
            )
            print(f"[UPDATE] Updated {customer_name}'s order status to {status}.")
    except mysql.connector.Error as e:
        print(f"[ERROR] Error updating status: {e}")

def reset_database():
    conn = get_connection("READ COMMITTED")
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE orders SET status = 'pending', total_amount = 150 WHERE customer_name = 'Anna'")
            cur.execute("UPDATE orders SET status = 'confirmed', total_amount = 200 WHERE customer_name = 'Mark'")
            conn.commit()
            print("\n[INFO] Database reset to initial state.")
    except mysql.connector.Error as e:
        print(f"[ERROR] Error resetting database: {e}")
        conn.rollback()
    finally:
        conn.close()


#Scenario 1: Dirty Read
#Transaction 1 makes a change without commiting it. Transaction 2 Read uncommited change.
#Isolation level is Read Uncommited for Transaction 2

print("\n[INFO] Scenario 1: Dirty Read\n")

conn_t1 = get_connection("READ UNCOMMITTED")
conn_t2 = get_connection("READ UNCOMMITTED")

try:
    print("\n[INFO] Transaction 1:")
    conn_t1.start_transaction()
    update_status(conn_t1, "Anna", "Shipped")
    fetch_status(conn_t1, "Anna")
    time.sleep(3)

    print("\n[INFO] Transaction 2:")
    conn_t2.start_transaction()
    fetch_status(conn_t2, "Anna")
    time.sleep(3)
    
    print("\n[INFO] Transaction 1 (making a rollback):")
    conn_t1.rollback()
    time.sleep(3)

    print("\n[INFO] Transaction 2:")
    fetch_status(conn_t1, "Anna")
except mysql.connector.Error as e:
    print(f"[ERROR] {e}")
finally:
    conn_t1.close()
    conn_t2.close()
    reset_database()

print("\n[✅] Dirty read scenario completed")

#Scenario 2: Non-repeatable read
#Transaction 1 reads the status, then transaction 2 changes it and commits
#Transaction 1 reads the same status again, getting different result
#Isolation level: both "READ COMMITED"

print("\n[INFO] SCENARIO 2: NON-REPEATABLE READ\n")

conn_t1 = get_connection("READ COMMITTED")
conn_t2 = get_connection("READ COMMITTED")
try:
    print("\n[INFO] Transaction 1:")
    conn_t1.start_transaction()
    fetch_status(conn_t1, "Anna")
    time.sleep(3)

    print("\n[INFO] Transaction 2: ")
    conn_t2.start_transaction()
    update_status(conn_t2, "Anna", "Shipped")
    conn_t2.commit()
    time.sleep(3)

    print("\n[INFO] Transaction 1:")
    fetch_status(conn_t1, "Anna")
    time.sleep(3)
except mysql.connector.Error as e:
    print(f"[ERROR] {e}")
finally:
    conn_t1.close()
    conn_t2.close()
    reset_database()

print("\n[✅] Non-Repeatable read scenario completed")

# ---Bonus Tasks---
#Scenario 3: Repeatable Read
#Shows the work of Scenario 2 with REPEATABLE READ level of isolation, making visible the difference
print("\nScenario 3: Scenario but 2 with REPEATABLE READ level of isolation.\n")

conn_t1 = get_connection("REPEATABLE READ")
conn_t2 = get_connection("REPEATABLE READ")
try:
    print("\n[INFO] Transaction 1:")
    conn_t1.start_transaction()
    fetch_status(conn_t1, "Anna")
    time.sleep(3)

    print("\n[INFO] Transaction 2: ")
    conn_t2.start_transaction()
    update_status(conn_t2, "Anna", "Shipped")
    conn_t2.commit()
    time.sleep(3)

    print("\n[INFO] Transaction 1: ")
    fetch_status(conn_t1, "Anna")
    time.sleep(3)

except mysql.connector.Error as e:
    print(f"[ERROR] {e}")
finally:
    conn_t1.close()
    conn_t2.close()
    reset_database()

print("\n[✅] Repeatable read scenario completed")

#Scenario 4: Deadlock
#Two transactions block each other while being executed concurrently

print("\nScenario 4: Deadlock.\n")

conn1 = get_connection("READ COMMITTED")
conn2 = get_connection("READ COMMITTED")

try:
    print("\n[INFO] Transaction 1:")
    conn1.start_transaction()
    update_status(conn1, "Anna", "processing")
    time.sleep(3)

    print("\n[INFO] Transaction 2:")
    conn2.start_transaction()
    update_status(conn2, "Mark", "shipped")
    time.sleep(3)

    print("\n[INFO] Transaction 1 trying to update Mark:")
    update_status(conn1, "Mark", "processing")

    print("\n[INFO] Transaction 2 trying to update Anna:")
    update_status(conn2, "Anna", "shipped")

except mysql.connector.Error as e:
    print(f"[ERROR] {e}")
finally:
    conn1.close()
    conn2.close()
    reset_database()

print("\n[✅] Deadlock scenario completed")
