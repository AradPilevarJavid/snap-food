from storage import get_storage, STORAGE_TYPE
from models import MenuItem, User, Manager, Customer, Order, CombinedOrder, Restaurant

class Platform:
    def __init__(self, storage_type=STORAGE_TYPE):
        self.storage = get_storage(storage_type)
        self.users = []
        self.restaurants = []
        self.orders = []
        self.combined_orders = []
        self.current_user = None
        self._manager_counter = 0
        self._customer_counter = 0
        self._order_counter = 1
        self._load_data()

    def _load_data(self):
        data = self.storage.load()
        if not data or not any(data.values()):
            self._create_default_data()
            return

        users_data = data.get("users", [])
        restaurants_data = data.get("restaurants", [])
        menu_items_data = data.get("menu_items", [])
        orders_data = data.get("orders", [])
        combined_orders_data = data.get("combined_orders", [])

        temp_managers = {}
        self.users = []
        self.restaurants = []

        for u in users_data:
            if u["role"] == "manager":
                rest = next((r for r in restaurants_data if r["manager_id"] == u["id"]), None)
                if rest:
                    restaurant = Restaurant(rest["name"], None)
                    self.restaurants.append(restaurant)
                    mgr = Manager(u["id"], u["first_name"], u["last_name"],
                                  u["username"], u["password"], restaurant)
                    restaurant.manager = mgr
                    self.users.append(mgr)
                    temp_managers[u["id"]] = mgr
                    if u["id"][1:].isdigit():
                        self._manager_counter = max(self._manager_counter, int(u["id"][1:]))
            else:
                cust = Customer(u["id"], u["first_name"], u["last_name"],
                                u["username"], u["password"])
                self.users.append(cust)
                if u["id"][1:].isdigit():
                    self._customer_counter = max(self._customer_counter, int(u["id"][1:]))


        for item_dict in menu_items_data:
            rest_name = item_dict["restaurant_name"]
            restaurant = next((r for r in self.restaurants if r.name == rest_name), None)
            if restaurant:
                restaurant.menu.append(MenuItem.from_dict(item_dict))

        # od processes regular orders from a single restaurant
        for od in orders_data:
            items = [MenuItem.from_dict(i) for i in od["items"]]
            order = Order(od["id"], od["customer_id"], od["restaurant_name"], items, od["datetime"])
            self.orders.append(order)
            restaurant = next((r for r in self.restaurants if r.name == order.restaurant_name), None)
            if restaurant:
                restaurant.orders.append(order)
            self._order_counter = max(self._order_counter, order.id + 1)


        # cod processes combined orders from multiple restaurants
        for cod in combined_orders_data:
            cart_items = []
            for item_dict in cod["items"]:
                rest_name = item_dict.pop("restaurant_name", "")
                menu_item = MenuItem.from_dict(item_dict)
                cart_items.append((menu_item, rest_name))
            combined = CombinedOrder(cod["id"], cod["customer_id"], cart_items, cod["datetime"])
            self.combined_orders.append(combined)
            customer = next((u for u in self.users if u.id == cod["customer_id"] and u.role == "customer"), None)
            if customer:
                customer.order_history.append(combined)
            self._order_counter = max(self._order_counter, combined.id + 1)

    def _create_default_data(self):
        rest = Restaurant("Admin's Kitchen", None)
        mgr = Manager(User.generate_id("manager", 1), "Ali", "Alavi", "admin", "123456", rest)
        rest.manager = mgr
        rest.menu.append(MenuItem("Pizza", 12.5, "food", True, "pizza.png"))
        rest.menu.append(MenuItem("Cola", 3.0, "drink", True, "cola.png"))
        rest.menu.append(MenuItem("Salad", 7.0, "food", False))
        self.users.append(mgr)
        self._manager_counter = 1
        self.restaurants.append(rest)


        cust = Customer(User.generate_id("customer", 1), "Sara", "Ahmadi", "user", "123456")
        self.users.append(cust)
        self._customer_counter = 1


        rest2 = Restaurant("Quick Bites", None)
        mgr2 = Manager(User.generate_id("manager", 2), "Reza", "Karimi", "manager2", "123456", rest2)
        rest2.manager = mgr2
        rest2.menu.append(MenuItem("Burger", 8.0, "food", True, "burger.png"))
        rest2.menu.append(MenuItem("Fries", 4.0, "food", True))
        rest2.menu.append(MenuItem("Lemonade", 2.5, "drink", True))
        self.users.append(mgr2)
        self._manager_counter = 2
        self.restaurants.append(rest2)

    def save(self):
        data = {
            "users": [u.to_dict() for u in self.users],
            "restaurants": [r.to_dict() for r in self.restaurants],
            "menu_items": [],
            "orders": [o.to_dict() for o in self.orders],
            "combined_orders": [co.to_dict() for co in self.combined_orders]
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
            uid = User.generate_id("manager", self._manager_counter + 1)
            rest = Restaurant(restaurant_name.strip(), None)
            mgr = Manager(uid, first_name, last_name, username, password, rest)
            rest.manager = mgr
            self.users.append(mgr)
            self.restaurants.append(rest)
            self._manager_counter += 1
        else:
            uid = User.generate_id("customer", self._customer_counter + 1)
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

    def checkout_multi(self, customer):
        """
        Process the customer's cart (which may contain items from several restaurants).
        Creates one CombinedOrder (customer-facing) and perestaurant Orders.
        Returns the CombinedOrder or None.
        """
        if not customer.cart:
            return None


        from itertools import groupby
        sorted_cart = sorted(customer.cart, key=lambda x: x[1])
        groups = {rest: [item for item, _ in grp]
                  for rest, grp in groupby(sorted_cart, key=lambda x: x[1])}


        combined_id = self._next_order_id()
        combined = customer.place_combined_order(combined_id)


        for rest_name, items in groups.items():
            restaurant = next((r for r in self.restaurants if r.name == rest_name), None)
            if restaurant:
                oid = self._next_order_id()
                order = Order(oid, customer.id, rest_name, items)
                restaurant.register_order(order)
                self.orders.append(order)

        self.combined_orders.append(combined)
        self.save()
        return combined

    # getter methods at the end.
    def get_restaurants(self):
        return self.restaurants

    def get_restaurant_menu(self, restaurant):
        return restaurant.menu

    def get_restaurant_orders(self, restaurant):
        return restaurant.orders

    def get_customer_orders(self, customer):
        return customer.order_history
