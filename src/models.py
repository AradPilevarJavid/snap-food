import re
import datetime

class MenuItem:
    def __init__(self, name, price, item_type, available=True):
        self.name = name
        self.price = price
        self.type = item_type
        self.available = available

    def display_info(self):
        return f"{self.name} ({self.type}) - ${self.price:.2f} {'[Available]' if self.available else '[Unavailable]'}"

    def to_dict(self):
        return {"name": self.name, "price": self.price, "type": self.type, "available": self.available}

    @staticmethod
    def from_dict(d):
        return MenuItem(d["name"], d["price"], d["type"], d.get("available", True))

class User:
    @staticmethod
    def validate_name(name):
        return bool(re.fullmatch(r"[A-Za-z ]+", name)) and len(name.strip()) > 0

    @staticmethod
    def validate_username(username):
        return bool(re.fullmatch(r"[A-Za-z0-9_]{3,}", username))

    @staticmethod
    def validate_password(password):
        return len(password) >= 6

    def __init__(self, user_id, first_name, last_name, username, password, role):
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password
        self.role = role

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "password": self.password,
            "role": self.role
        }

class Manager(User):
    def __init__(self, user_id, first_name, last_name, username, password, restaurant):
        super().__init__(user_id, first_name, last_name, username, password, "manager")
        self.restaurant = restaurant

    def add_menu_item(self, item):
        self.restaurant.menu.append(item)

    def edit_menu_item(self, index, new_item):
        self.restaurant.menu[index] = new_item

    def delete_menu_item(self, index):
        del self.restaurant.menu[index]

class Customer(User):
    def __init__(self, user_id, first_name, last_name, username, password):
        super().__init__(user_id, first_name, last_name, username, password, "customer")
        self.cart = []
        self.order_history = []

    def add_to_cart(self, item):
        self.cart.append(item)

    def remove_from_cart(self, index):
        if 0 <= index < len(self.cart):
            del self.cart[index]

class Order:
    def __init__(self, order_id, customer_id, restaurant_name, items, dt=None):
        self.id = order_id
        self.customer_id = customer_id
        self.restaurant_name = restaurant_name
        self.items = items
        self.datetime = dt if dt else datetime.datetime.now().isoformat()

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, index):
        if 0 <= index < len(self.items):
            del self.items[index]

    def total_price(self):
        return sum(item.price for item in self.items)

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "restaurant_name": self.restaurant_name,
            "datetime": self.datetime,
            "items": [i.to_dict() for i in self.items]
        }

class Restaurant:
    def __init__(self, name, manager):
        self.name = name
        self.manager = manager
        self.menu = []
        self.orders = []

    def display_menu(self):
        return self.menu

    def display_orders(self):
        return self.orders

    def register_order(self, order):
        self.orders.append(order)

    def to_dict(self):
        return {
            "name": self.name,
            "manager_id": self.manager.id
        }