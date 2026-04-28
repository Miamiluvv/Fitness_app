import MySQLdb
from MySQLdb import Error
from contextlib import contextmanager

class DatabaseConnection:
    def __init__(self, host='localhost', user='root', password='', database='fitness_club'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = MySQLdb.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                db=self.database,
                charset='utf8mb4'
            )
            return self.connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    def disconnect(self):
        if self.connection:
            self.connection.close()

    @contextmanager
    def get_cursor(self):
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except Error as e:
            self.connection.rollback()
            print(f"Database error: {e}")
        finally:
            cursor.close()

    def execute_query(self, query, params=None):
        try:
            with self.get_cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
        except Error as e:
            print(f"Query execution error: {e}")
            return None

    def execute_insert(self, query, params=None):
        try:
            with self.get_cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.lastrowid
        except Error as e:
            print(f"Insert error: {e}")
            return None

    def execute_update(self, query, params=None):
        try:
            with self.get_cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.rowcount
        except Error as e:
            print(f"Update error: {e}")
            return 0
