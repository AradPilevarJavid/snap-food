import json
import sqlite3
import os
from abc import ABC, abstractmethod

STORAGE_TYPE = "json"

class Storage(ABC):
    @abstractmethod
    def load(self) -> dict:
        pass

    @abstractmethod
    def save(self, data: dict) -> None:
        pass

class JSONStorage(Storage):
    def __init__(self, filepath="data.json"):
        self.filepath = filepath

    def load(self) -> dict:
        if not os.path.exists(self.filepath):
            return {}
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: dict) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

class SQLiteStorage(Storage):
    def __init__(self, db_path="data.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT
            );
            CREATE TABLE IF NOT EXISTS restaurants (
                name TEXT PRIMARY KEY,
                manager_id TEXT,
                FOREIGN KEY (manager_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                price REAL,
                available INTEGER,
                type TEXT,
                restaurant_name TEXT,
                FOREIGN KEY (restaurant_name) REFERENCES restaurants(name)
            );
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                customer_id TEXT,
                restaurant_name TEXT,
                datetime TEXT,
                FOREIGN KEY (customer_id) REFERENCES users(id),
                FOREIGN KEY (restaurant_name) REFERENCES restaurants(name)
            );
            CREATE TABLE IF NOT EXISTS order_items (
                order_id INTEGER,
                item_name TEXT,
                item_price REAL,
                item_type TEXT,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            );
        """)
        self.conn.commit()

    def load(self) -> dict:
        data = {"users": [], "restaurants": [], "menu_items": [], "orders": []}
        self.cursor.execute("SELECT * FROM users")
        for row in self.cursor.fetchall():
            data["users"].append({
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "username": row[3],
                "password": row[4],
                "role": row[5]
            })
        self.cursor.execute("SELECT * FROM restaurants")
        for row in self.cursor.fetchall():
            data["restaurants"].append({
                "name": row[0],
                "manager_id": row[1]
            })
        self.cursor.execute("SELECT name, price, available, type, restaurant_name FROM menu_items")
        for row in self.cursor.fetchall():
            data["menu_items"].append({
                "name": row[0],
                "price": row[1],
                "available": bool(row[2]),
                "type": row[3],
                "restaurant_name": row[4]
            })
        self.cursor.execute("SELECT id, customer_id, restaurant_name, datetime FROM orders")
        orders = {}
        for row in self.cursor.fetchall():
            order_id = row[0]
            orders[order_id] = {
                "id": order_id,
                "customer_id": row[1],
                "restaurant_name": row[2],
                "datetime": row[3],
                "items": []
            }
        self.cursor.execute("SELECT order_id, item_name, item_price, item_type FROM order_items")
        for row in self.cursor.fetchall():
            orders[row[0]]["items"].append({
                "name": row[1],
                "price": row[2],
                "type": row[3]
            })
        data["orders"] = list(orders.values())
        return data

    def save(self, data: dict) -> None:
        self.cursor.execute("DELETE FROM order_items")
        self.cursor.execute("DELETE FROM orders")
        self.cursor.execute("DELETE FROM menu_items")
        self.cursor.execute("DELETE FROM restaurants")
        self.cursor.execute("DELETE FROM users")
        for user in data.get("users", []):
            self.cursor.execute("INSERT INTO users VALUES (?,?,?,?,?,?)",
                                (user["id"], user["first_name"], user["last_name"],
                                 user["username"], user["password"], user["role"]))
        for rest in data.get("restaurants", []):
            self.cursor.execute("INSERT INTO restaurants VALUES (?,?)",
                                (rest["name"], rest["manager_id"]))
        for item in data.get("menu_items", []):
            self.cursor.execute("INSERT INTO menu_items (name, price, available, type, restaurant_name) VALUES (?,?,?,?,?)",
                                (item["name"], item["price"], int(item["available"]), item["type"], item["restaurant_name"]))
        for order in data.get("orders", []):
            self.cursor.execute("INSERT INTO orders VALUES (?,?,?,?)",
                                (order["id"], order["customer_id"], order["restaurant_name"], order["datetime"]))
            for oi in order["items"]:
                self.cursor.execute("INSERT INTO order_items VALUES (?,?,?,?)",
                                    (order["id"], oi["name"], oi["price"], oi["type"]))
        self.conn.commit()

    def __del__(self):
        self.conn.close()

def get_storage(storage_type=STORAGE_TYPE):
    if storage_type == "sqlite":
        return SQLiteStorage()
    return JSONStorage()