import json
import sqlite3
import os
from abc import ABC, abstractmethod


STORAGE_TYPE = "sqlite"

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
                image_path TEXT,
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
            CREATE TABLE IF NOT EXISTS combined_orders (
                id INTEGER PRIMARY KEY,
                customer_id TEXT,
                datetime TEXT,
                FOREIGN KEY (customer_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS combined_order_items (
                combined_order_id INTEGER,
                item_name TEXT,
                item_price REAL,
                item_type TEXT,
                restaurant_name TEXT,
                FOREIGN KEY (combined_order_id) REFERENCES combined_orders(id)
            );
        """)
        self.conn.commit()

    def load(self) -> dict:
        data = {"users": [], "restaurants": [], "menu_items": [],
                "orders": [], "combined_orders": []}

        self.cursor.execute("SELECT * FROM users")
        for row in self.cursor.fetchall():
            data["users"].append({
                "id": row[0], "first_name": row[1], "last_name": row[2],
                "username": row[3], "password": row[4], "role": row[5]
            })

        self.cursor.execute("SELECT * FROM restaurants")
        for row in self.cursor.fetchall():
            data["restaurants"].append({"name": row[0], "manager_id": row[1]})

        self.cursor.execute("SELECT name, price, available, type, image_path, restaurant_name FROM menu_items")
        for row in self.cursor.fetchall():
            data["menu_items"].append({
                "name": row[0], "price": row[1], "available": bool(row[2]),
                "type": row[3], "image_path": row[4], "restaurant_name": row[5]
            })

        self.cursor.execute("SELECT id, customer_id, restaurant_name, datetime FROM orders")
        orders_dict = {}
        for row in self.cursor.fetchall():
            orders_dict[row[0]] = {
                "id": row[0], "customer_id": row[1], "restaurant_name": row[2],
                "datetime": row[3], "items": []
            }
        self.cursor.execute("SELECT order_id, item_name, item_price, item_type FROM order_items")
        for row in self.cursor.fetchall():
            if row[0] in orders_dict:
                orders_dict[row[0]]["items"].append({
                    "name": row[1], "price": row[2], "type": row[3]
                })
        data["orders"] = list(orders_dict.values())


        self.cursor.execute("SELECT id, customer_id, datetime FROM combined_orders")
        combined_dict = {}
        for row in self.cursor.fetchall():
            combined_dict[row[0]] = {
                "id": row[0], "customer_id": row[1], "datetime": row[2], "items": []
            }
        self.cursor.execute("SELECT combined_order_id, item_name, item_price, item_type, restaurant_name FROM combined_order_items")
        for row in self.cursor.fetchall():
            if row[0] in combined_dict:
                combined_dict[row[0]]["items"].append({
                    "name": row[1], "price": row[2], "type": row[3],
                    "restaurant_name": row[4]
                })
        data["combined_orders"] = list(combined_dict.values())

        return data

    def save(self, data: dict) -> None:
        self.cursor.execute("DELETE FROM combined_order_items")
        self.cursor.execute("DELETE FROM combined_orders")
        self.cursor.execute("DELETE FROM order_items")
        self.cursor.execute("DELETE FROM orders")
        self.cursor.execute("DELETE FROM menu_items")
        self.cursor.execute("DELETE FROM restaurants")
        self.cursor.execute("DELETE FROM users")

        for u in data.get("users", []):
            self.cursor.execute("INSERT INTO users VALUES (?,?,?,?,?,?)",
                                (u["id"], u["first_name"], u["last_name"],
                                 u["username"], u["password"], u["role"]))
        for r in data.get("restaurants", []):
            self.cursor.execute("INSERT INTO restaurants VALUES (?,?)",
                                (r["name"], r["manager_id"]))
        for m in data.get("menu_items", []):
            self.cursor.execute(
                "INSERT INTO menu_items (name, price, available, type, image_path, restaurant_name) VALUES (?,?,?,?,?,?)",
                (m["name"], m["price"], int(m["available"]), m["type"],
                 m.get("image_path"), m["restaurant_name"]))
        for o in data.get("orders", []):
            self.cursor.execute("INSERT INTO orders VALUES (?,?,?,?)",
                                (o["id"], o["customer_id"], o["restaurant_name"], o["datetime"]))
            for item in o["items"]:
                self.cursor.execute("INSERT INTO order_items VALUES (?,?,?,?)",
                                    (o["id"], item["name"], item["price"], item["type"]))
        for co in data.get("combined_orders", []):
            self.cursor.execute("INSERT INTO combined_orders VALUES (?,?,?)",
                                (co["id"], co["customer_id"], co["datetime"]))
            for item in co["items"]:
                self.cursor.execute("INSERT INTO combined_order_items VALUES (?,?,?,?,?)",
                                    (co["id"], item["name"], item["price"], item["type"],
                                     item.get("restaurant_name", "")))
        self.conn.commit()

    def __del__(self):
        self.conn.close()

def get_storage(storage_type=STORAGE_TYPE):
    if storage_type == "sqlite":
        return SQLiteStorage()
    return JSONStorage()