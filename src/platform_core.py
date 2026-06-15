from storage import get_storage, STORAGE_TYPE
from models import MenuItem, User, Manager, Customer, Order, Restaurant

class Platform:
    def __init__(self, storage_type=STORAGE_TYPE):
        self.storage = get_storage(storage_type)
        self.users = []
        self.restaurants = []
        self.orders = []
        self.current_user = None
        self._manager_counter = 0
        self._customer_counter = 0
        self._order_counter = 1
        self._load_data()

    def _load_data(self):
        data = self.storage.load()
        if not data:
            self._create_default_data()
            return
        users_data = data.get("users", [])
        restaurants_data = data.get("restaurants", [])
        menu_items_data = data.get("menu_items", [])
        orders_data = data.get("orders", [])

        temp_managers = {}
        self.users = []
        self.restaurants = []
        for u in users_data:
            if u["role"] == "manager":
                rest = next((r for r in restaurants_data if r["manager_id"] == u["id"]), None)
                if rest:
                    restaurant = Restaurant(rest["name"], None)
                    self.restaurants.append(restaurant)
                    mgr = Manager(u["id"], u["first_name"], u["last_name"], u["username"], u["password"], restaurant)
                    restaurant.manager = mgr
                    self.users.append(mgr)
                    temp_managers[u["id"]] = mgr
                    if u["id"][1:].isdigit():
                        self._manager_counter = max(self._manager_counter, int(u["id"][1:]))
            else:
                cust = Customer(u["id"], u["first_name"], u["last_name"], u["username"], u["password"])
                self.users.append(cust)
                if u["id"][1:].isdigit():
                    self._customer_counter = max(self._customer_counter, int(u["id"][1:]))

        for item_dict in menu_items_data:
            rest_name = item_dict["restaurant_name"]
            restaurant = next((r for r in self.restaurants if r.name == rest_name), None)
            if restaurant:
                restaurant.menu.append(MenuItem.from_dict(item_dict))

        for order_dict in orders_data:
            items = [MenuItem.from_dict(i) for i in order_dict["items"]]
            order = Order(order_dict["id"], order_dict["customer_id"], order_dict["restaurant_name"], items, order_dict["datetime"])
            self.orders.append(order)
            restaurant = next((r for r in self.restaurants if r.name == order.restaurant_name), None)
            if restaurant:
                restaurant.orders.append(order)
            customer = next((u for u in self.users if u.id == order.customer_id and u.role == "customer"), None)
            if customer:
                customer.order_history.append(order)
            self._order_counter = max(self._order_counter, order.id + 1)

    def _create_default_data(self):
        rest = Restaurant("Admin's Kitchen", None)
        mgr = Manager("m1", "Ali", "Alavi", "admin", "123456", rest)
        rest.manager = mgr
        self.users.append(mgr)
        self._manager_counter = 1
        self.restaurants.append(rest)
        rest.menu.append(MenuItem("Pizza", 12.5, "food"))
        rest.menu.append(MenuItem("Cola", 3.0, "drink"))
        rest.menu.append(MenuItem("Salad", 7.0, "food", False))

        cust = Customer("c1", "Sara", "Ahmadi", "user", "123456")
        self.users.append(cust)
        self._customer_counter = 1

    def save(self):
        data = {
            "users": [u.to_dict() for u in self.users],
            "restaurants": [r.to_dict() for r in self.restaurants],
            "menu_items": [],
            "orders": [o.to_dict() for o in self.orders]
        }
        for r in self.restaurants:
            for item in r.menu:
                d = item.to_dict()
                d["restaurant_name"] = r.name
                data["menu_items"].append(d)
        self.storage.save(data)

    def _next_order_id(self):
        oid = self._order_counter
        self._order_counter += 1
        return oid

    def _add_order(self, order):
        self.orders.append(order)

    def sign_up(self, role, first_name, last_name, username, password, restaurant_name=None):
        if not User.validate_name(first_name) or not User.validate_name(last_name):
            return False, "Name must contain only letters and spaces."
        if not User.validate_username(username):
            return False, "Username must be at least 3 alphanumeric characters."
        if any(u.username == username for u in self.users):
            return False, "Username already exists."
        if not User.validate_password(password):
            return False, "Password must be at least 6 characters."
        if role == "manager":
            if not restaurant_name or not restaurant_name.strip():
                return False, "Restaurant name required."
            uid = f"m{self._manager_counter + 1}"
            rest = Restaurant(restaurant_name.strip(), None)
            mgr = Manager(uid, first_name, last_name, username, password, rest)
            rest.manager = mgr
            self.users.append(mgr)
            self.restaurants.append(rest)
            self._manager_counter += 1
        else:
            uid = f"c{self._customer_counter + 1}"
            cust = Customer(uid, first_name, last_name, username, password)
            self.users.append(cust)
            self._customer_counter += 1
        self.save()
        return True, "Registration successful."

    def sign_in(self, username, password):
        user = next((u for u in self.users if u.username == username and u.password == password), None)
        if user:
            self.current_user = user
            return True, "Login successful."
        return False, "Invalid username or password."

    def logout(self):
        self.current_user = None

    def checkout(self, customer, restaurant):
        if not customer.cart:
            return None
        items = customer.cart.copy()
        order_id = self._next_order_id()
        order = Order(order_id, customer.id, restaurant.name, items)
        restaurant.register_order(order)
        customer.order_history.append(order)
        customer.cart.clear()
        self._add_order(order)
        self.save()
        return order

    def get_restaurants(self):
        return self.restaurants

    def get_restaurant_menu(self, restaurant):
        return restaurant.menu

    def get_restaurant_orders(self, restaurant):
        return restaurant.orders

    def get_customer_orders(self, customer):
        return customer.order_history