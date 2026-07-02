import re
import datetime
from pathlib import Path

def _try_image(path):
    """Return a PhotoImage if PIL(Python Image Library) is available and path exists, else None."""
    try:
        from PIL import Image, ImageTk
        img = Image.open(path)
        img = img.resize((60, 60), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


class MenuItem:
    def __init__(self, name, price, item_type, available=True, image_path=None):
        self.name = name
        self.price = price
        self.type = item_type
        self.available = available
        self.image_path = image_path

    def display_info(self):
        status = "[Available]" if self.available else "[Unavailable]"
        return f"{self.name} ({self.type}) - ${self.price:.2f} {status}"

    def to_dict(self):
        d = {"name": self.name, "price": self.price, "type": self.type,
             "available": self.available}
        if self.image_path:
            d["image_path"] = self.image_path
        return d

    @staticmethod
    def from_dict(d):
        return MenuItem(d["name"], d["price"], d["type"],
                        d.get("available", True),
                        d.get("image_path", None))


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

    @staticmethod
    def generate_id(role, counter):
        prefix = "m" if role == "manager" else "c"
        return f"{prefix}{counter}"

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
        # Call the User constructor, setting role to "manager" automatically.
        super().__init__(user_id, first_name, last_name, username, password, "manager")
        self.restaurant = restaurant

    def add_menu_item(self, item):
        self.restaurant.menu.append(item)

    def edit_menu_item(self, index, new_item):
        if 0 <= index < len(self.restaurant.menu):
            self.restaurant.menu[index] = new_item

    def delete_menu_item(self, index):
        if 0 <= index < len(self.restaurant.menu):
            del self.restaurant.menu[index]


class Customer(User):
    def __init__(self, user_id, first_name, last_name, username, password):
        super().__init__(user_id, first_name, last_name, username, password, "customer")
        self.cart: list[tuple[MenuItem, str]] = []
        self.order_history: list[CombinedOrder] = []

    def add_to_cart(self, item, restaurant_name):
        self.cart.append((item, restaurant_name))

    def remove_from_cart(self, index):
        if 0 <= index < len(self.cart):
            del self.cart[index]

    def place_combined_order(self, order_id):
        """Create a CombinedOrder from the current cart and return it."""
        if not self.cart:
            return None
        # Snapshot the cart before clearing it.
        items_snapshot = self.cart[:]
        combined = CombinedOrder(order_id, self.id, items_snapshot)
        self.order_history.append(combined)
        self.cart.clear()
        return combined


class Order:
    """Single-restaurant order (for managers' view)."""
    def __init__(self, order_id, customer_id, restaurant_name, items, dt=None):
        self.id = order_id
        self.customer_id = customer_id
        self.restaurant_name = restaurant_name
        self.items = items
        # Store datetime as an ISO‑formatted string for easy serialisation.
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


class CombinedOrder:
    """Customer-facing order that can include items from several restaurants."""
    def __init__(self, order_id, customer_id, cart_items, dt=None):
        self.id = order_id
        self.customer_id = customer_id
        self.items_with_restaurant = cart_items
        self.items = [item for item, _ in cart_items]
        self.datetime = dt if dt else datetime.datetime.now().isoformat()

    def total_price(self):
        return sum(item.price for item in self.items)

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "datetime": self.datetime,
            "items": [
                {**item.to_dict(), "restaurant_name": rest}
                for item, rest in self.items_with_restaurant
            ]
        }


class Restaurant:
    def __init__(self, name, manager):
        self.name = name
        self.manager = manager
        self.menu: list[MenuItem] = []
        self.orders: list[Order] = []

    def display_menu(self):
        return self.menu

    def display_orders(self):
        return self.orders

    def register_order(self, order: Order):
        self.orders.append(order)

    def to_dict(self):
        return {
            "name": self.name,
            "manager_id": self.manager.id
        }
