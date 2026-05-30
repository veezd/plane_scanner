import sqlite3
import os

class DBmanager:
    def __init__(self):
        current_file_path = os.path.abspath(__file__)
        app_dir = os.path.dirname(current_file_path)
        self.db_dir = os.path.join(os.path.dirname(app_dir), "database")
        self.db_path = os.path.join(self.db_dir, "data.db")

        self.connection, self.cursor = self.create_db_connection()
        
        self.send_query("create_tables.sql")

    def create_db_connection(self):
        con, cur = None, None 

        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            # Odrazu przy polaczeniu inicjalizuje uzywane przez nas tablice
            print("[DBmanager] Connection successfully created")

        except sqlite3.Error as e:
            print(f"[DBmanager] A database error occurred: {e}")
        except Exception as e:
            print(f"[DBmanager] An unexpected error occurred: {e}")
            
        return (con, cur)
    

    def send_query(self, query_or_file):
        # jako argumenty podac jedno zapytanie str, albo caly skrypt .sql (musi byc w folderze database)
        try:
            if isinstance(query_or_file, str) and query_or_file.strip().endswith('.sql'):
                
                if not os.path.isabs(query_or_file) and not os.path.exists(query_or_file):
                    file_path = os.path.join(self.db_dir, query_or_file)
                else:
                    file_path = query_or_file
                
                print(f"[DBmanager] Executing script: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as file:
                    sql_content = file.read()
                
                self.cursor.executescript(sql_content)
                
            else:
                self.cursor.execute(query_or_file)
            
            self.connection.commit()
            
        except FileNotFoundError:
            print(f"[DBmanager] No SQL script: {query_or_file} found")
            return None
        except sqlite3.Error as e:
            print(f"[DBmanager] Database error: {e}")
            if self.connection:
                self.connection.rollback() 
            return None