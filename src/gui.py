import tkinter as tk
from tkinter import messagebox, ttk
from models import MenuItem

class App:
    def __init__(self, platform):
        self.platform = platform
        self.root = tk.Tk()
        self.root.title("Restaurant Management System")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def run(self):
        self._show_login_frame()
        self.root.mainloop()

    def _on_close(self):
        self.platform.save()
        self.root.destroy()

    def _clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def _show_login_frame(self):
        self._clear_frame()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)
        ttk.Label(frame, text="Welcome", font=("Arial", 24)).pack(pady=10)
        ttk.Label(frame, text="Username:").pack()
        username_var = tk.StringVar()
        ttk.Entry(frame, textvariable=username_var).pack()
        ttk.Label(frame, text="Password:").pack()
        password_var = tk.StringVar()
        ttk.Entry(frame, textvariable=password_var, show="*").pack()
        ttk.Button(frame, text="Login", command=lambda: self._login(username_var.get(), password_var.get())).pack(pady=5)
        ttk.Button(frame, text="Sign Up", command=self._show_signup_frame).pack()

    def _login(self, username, password):
        success, msg = self.platform.sign_in(username, password)
        if success:
            self._show_main_menu()
        else:
            messagebox.showerror("Error", msg)

    def _show_signup_frame(self):
        self._clear_frame()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)
        ttk.Label(frame, text="Sign Up", font=("Arial", 20)).pack(pady=10)
        ttk.Label(frame, text="First Name:").pack()
        first_var = tk.StringVar()
        ttk.Entry(frame, textvariable=first_var).pack()
        ttk.Label(frame, text="Last Name:").pack()
        last_var = tk.StringVar()
        ttk.Entry(frame, textvariable=last_var).pack()
        ttk.Label(frame, text="Username:").pack()
        user_var = tk.StringVar()
        ttk.Entry(frame, textvariable=user_var).pack()
        ttk.Label(frame, text="Password:").pack()
        pass_var = tk.StringVar()
        ttk.Entry(frame, textvariable=pass_var, show="*").pack()
        ttk.Label(frame, text="Role:").pack()
        role_var = tk.StringVar(value="customer")
        ttk.Radiobutton(frame, text="Customer", variable=role_var, value="customer").pack()
        ttk.Radiobutton(frame, text="Manager", variable=role_var, value="manager").pack()
        ttk.Label(frame, text="Restaurant Name (manager only):").pack()
        rest_var = tk.StringVar()
        ttk.Entry(frame, textvariable=rest_var).pack()
        ttk.Button(frame, text="Register", command=lambda: self._register(
            role_var.get(), first_var.get(), last_var.get(), user_var.get(), pass_var.get(), rest_var.get()
        )).pack(pady=10)
        ttk.Button(frame, text="Back", command=self._show_login_frame).pack()

    def _register(self, role, first, last, username, password, rest_name):
        success, msg = self.platform.sign_up(role, first, last, username, password, rest_name)
        if success:
            messagebox.showinfo("Success", msg)
            self._show_login_frame()
        else:
            messagebox.showerror("Error", msg)

    def _show_main_menu(self):
        self._clear_frame()
        if self.platform.current_user.role == "manager":
            self._manager_panel()
        else:
            self._customer_panel()

    def _manager_panel(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        mgr = self.platform.current_user
        rest = mgr.restaurant
        ttk.Label(frame, text=f"Manager Panel - {rest.name}", font=("Arial", 18)).pack(pady=5)
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Item", command=self._manager_add_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit Item", command=self._manager_edit_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Item", command=self._manager_delete_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="View Menu", command=self._manager_view_menu).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="View Orders", command=self._manager_view_orders).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Logout", command=self._logout).pack(pady=10)

    def _manager_add_item(self):
        win = tk.Toplevel(self.root)
        win.title("Add Menu Item")
        win.geometry("300x250")
        ttk.Label(win, text="Name:").pack()
        name_var = tk.StringVar()
        ttk.Entry(win, textvariable=name_var).pack()
        ttk.Label(win, text="Price:").pack()
        price_var = tk.StringVar()
        ttk.Entry(win, textvariable=price_var).pack()
        ttk.Label(win, text="Type:").pack()
        type_var = tk.StringVar(value="food")
        ttk.OptionMenu(win, type_var, "food", "food", "drink").pack()
        available_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(win, text="Available", variable=available_var).pack()
        def add():
            try:
                price = float(price_var.get())
                item = MenuItem(name_var.get(), price, type_var.get(), available_var.get())
                self.platform.current_user.add_menu_item(item)
                self.platform.save()
                messagebox.showinfo("Success", "Item added.")
                win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid price.")
        ttk.Button(win, text="Add", command=add).pack(pady=10)

    def _manager_edit_item(self):
        rest = self.platform.current_user.restaurant
        if not rest.menu:
            messagebox.showinfo("Info", "Menu is empty.")
            return
        win = tk.Toplevel(self.root)
        win.title("Edit Menu Item")
        win.geometry("500x350")
        tree = ttk.Treeview(win, columns=("name", "price", "type", "avail"), show="headings")
        tree.heading("name", text="Name")
        tree.heading("price", text="Price")
        tree.heading("type", text="Type")
        tree.heading("avail", text="Available")
        tree.pack(fill=tk.BOTH, expand=True)
        for idx, item in enumerate(rest.menu):
            tree.insert("", tk.END, iid=idx, values=(item.name, f"{item.price:.2f}", item.type, "Yes" if item.available else "No"))
        edit_frame = ttk.Frame(win)
        edit_frame.pack(pady=5)
        ttk.Label(edit_frame, text="New Name:").grid(row=0, column=0)
        name_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=name_var).grid(row=0, column=1)
        ttk.Label(edit_frame, text="New Price:").grid(row=1, column=0)
        price_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=price_var).grid(row=1, column=1)
        ttk.Label(edit_frame, text="New Type:").grid(row=2, column=0)
        type_var = tk.StringVar(value="food")
        ttk.OptionMenu(edit_frame, type_var, "food", "food", "drink").grid(row=2, column=1)
        avail_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(edit_frame, text="Available", variable=avail_var).grid(row=3, columnspan=2)
        def save_edit():
            selected = tree.selection()
            if not selected:
                return
            idx = int(selected[0])
            try:
                price = float(price_var.get())
                new_item = MenuItem(name_var.get() or rest.menu[idx].name, price, type_var.get(), avail_var.get())
                self.platform.current_user.edit_menu_item(idx, new_item)
                self.platform.save()
                messagebox.showinfo("Success", "Item updated.")
                win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid price.")
        ttk.Button(win, text="Update Selected", command=save_edit).pack(pady=5)

    def _manager_delete_item(self):
        rest = self.platform.current_user.restaurant
        if not rest.menu:
            messagebox.showinfo("Info", "Menu empty.")
            return
        win = tk.Toplevel(self.root)
        win.title("Delete Menu Item")
        win.geometry("400x300")
        tree = ttk.Treeview(win, columns=("name", "price", "type"), show="headings")
        tree.heading("name", text="Name")
        tree.heading("price", text="Price")
        tree.heading("type", text="Type")
        tree.pack(fill=tk.BOTH, expand=True)
        for idx, item in enumerate(rest.menu):
            tree.insert("", tk.END, iid=idx, values=(item.name, f"{item.price:.2f}", item.type))
        def delete():
            selected = tree.selection()
            if selected:
                idx = int(selected[0])
                self.platform.current_user.delete_menu_item(idx)
                self.platform.save()
                messagebox.showinfo("Success", "Item deleted.")
                win.destroy()
        ttk.Button(win, text="Delete Selected", command=delete).pack(pady=5)

    def _manager_view_menu(self):
        rest = self.platform.current_user.restaurant
        self._show_list_window(f"Menu of {rest.name}", ["Name", "Price", "Type", "Available"],
                               [[i.name, f"{i.price:.2f}", i.type, "Yes" if i.available else "No"] for i in rest.menu])

    def _manager_view_orders(self):
        rest = self.platform.current_user.restaurant
        data = []
        for order in rest.orders:
            items = ", ".join(f"{i.name}(${i.price:.2f})" for i in order.items)
            data.append([order.id, order.customer_id, items, f"${order.total_price():.2f}", order.datetime])
        self._show_list_window(f"Orders of {rest.name}", ["ID", "Customer", "Items", "Total", "DateTime"], data)

    def _customer_panel(self):
        self._clear_frame()
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Customer Panel", font=("Arial", 18)).pack(pady=5)
        ttk.Label(frame, text="Select a restaurant:").pack()
        listbox = tk.Listbox(frame, height=6)
        listbox.pack(fill=tk.X, padx=20)
        for r in self.platform.get_restaurants():
            listbox.insert(tk.END, r.name)
        def select_restaurant():
            sel = listbox.curselection()
            if not sel:
                return
            rest = self.platform.get_restaurants()[sel[0]]
            self._customer_restaurant_menu(rest)
        ttk.Button(frame, text="Select Restaurant", command=select_restaurant).pack(pady=5)
        ttk.Button(frame, text="View Order History", command=self._customer_order_history).pack(pady=5)
        ttk.Button(frame, text="Logout", command=self._logout).pack(pady=5)

    def _customer_restaurant_menu(self, restaurant):
        win = tk.Toplevel(self.root)
        win.title(f"Menu - {restaurant.name}")
        win.geometry("700x500")
        tree = ttk.Treeview(win, columns=("name", "price", "type", "avail"), show="headings")
        tree.heading("name", text="Name")
        tree.heading("price", text="Price")
        tree.heading("type", text="Type")
        tree.heading("avail", text="Available")
        tree.pack(fill=tk.BOTH, expand=True)
        for item in restaurant.menu:
            tree.insert("", tk.END, values=(item.name, f"${item.price:.2f}", item.type, "Yes" if item.available else "No"))
        cart_frame = ttk.Frame(win)
        cart_frame.pack(fill=tk.X, pady=5)
        ttk.Label(cart_frame, text="Your Cart:").pack()
        cart_listbox = tk.Listbox(cart_frame, height=4)
        cart_listbox.pack(fill=tk.X)
        customer = self.platform.current_user
        def refresh_cart():
            cart_listbox.delete(0, tk.END)
            for item in customer.cart:
                cart_listbox.insert(tk.END, f"{item.name} - ${item.price:.2f}")
        refresh_cart()
        def add_to_cart():
            selected = tree.selection()
            if not selected:
                return
            values = tree.item(selected[0])["values"]
            name, price_str, _, avail = values
            if avail != "Yes":
                messagebox.showwarning("Unavailable", "Item is not available.")
                return
            price = float(price_str.replace("$", ""))
            item = next((i for i in restaurant.menu if i.name == name and i.price == price), None)
            if item:
                customer.add_to_cart(item)
                refresh_cart()
        ttk.Button(win, text="Add to Cart", command=add_to_cart).pack(pady=2)
        def remove_from_cart():
            sel = cart_listbox.curselection()
            if sel:
                customer.remove_from_cart(sel[0])
                refresh_cart()
        ttk.Button(win, text="Remove Selected", command=remove_from_cart).pack()
        def checkout():
            if not customer.cart:
                messagebox.showinfo("Empty", "Cart is empty.")
                return
            order = self.platform.checkout(customer, restaurant)
            if order:
                messagebox.showinfo("Order", f"Order #{order.id} placed.\nTotal: ${order.total_price():.2f}")
                cart_listbox.delete(0, tk.END)
                refresh_cart()
        ttk.Button(win, text="Checkout", command=checkout).pack(pady=5)

    def _customer_order_history(self):
        orders = self.platform.get_customer_orders(self.platform.current_user)
        data = []
        for o in orders:
            items = ", ".join(f"{i.name}" for i in o.items)
            data.append([o.id, o.restaurant_name, items, f"${o.total_price():.2f}", o.datetime])
        self._show_list_window("Order History", ["ID", "Restaurant", "Items", "Total", "DateTime"], data)

    def _show_list_window(self, title, columns, data):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("700x300")
        tree = ttk.Treeview(win, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
        tree.pack(fill=tk.BOTH, expand=True)
        for row in data:
            tree.insert("", tk.END, values=row)

    def _logout(self):
        self.platform.logout()
        self.platform.save()
        self._show_login_frame()