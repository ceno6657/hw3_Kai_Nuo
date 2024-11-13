from contextlib import contextmanager
import logging
import os
import sqlite3

from meal_max.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


# load the db path from the environment with a default value


# Update the DB_PATH to point to a temporary database
DB_PATH = os.getenv("DB_PATH", "test_db.sqlite")

# Ensure the test_db.sqlite file exists (create if not)
if not os.path.exists(DB_PATH):
    open(DB_PATH, 'a').close()  # Create an empty file if it doesn't exist



def check_database_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # This ensures the connection is actually active
        cursor.execute("SELECT 1;")
        conn.close()
    except sqlite3.Error as e:
        error_message = f"Database connection error: {e}"
        logger.error(error_message)
        raise Exception(error_message) from e

def check_table_exists(tablename: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT 1 FROM {tablename} LIMIT 1;")
        conn.close()
    except sqlite3.Error as e:
        error_message = f"Table check error: {e}"
        logger.error(error_message)
        raise Exception(error_message) from e

###################################################
#
# This one yields rather than returns.
# What is the type of the yielded value?
#
###################################################
@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        yield conn
    except sqlite3.Error as e:
        logger.error("Database connection error: %s", str(e))
        raise e
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")
