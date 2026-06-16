import tkinter as tk
from tkinter import ttk, messagebox
from models import MenuItem

class App:
    """
    Professional-grade Tkinter GUI for Restaurant Management System.
    Implements a clean, consistent UI with status bar, scrollable treeviews,
    pre-populated edit dialogs, and robust error handling.
    """

    # Color palette (adaptable)
    BG_COLOR = "#f0f0f5"
    CARD_BG = "#ffffff"
    PRIMARY = "#2c3e50"
    ACCENT = "#3498db"
    SUCCESS = "#27ae60"
    DANGER = "#e74c3c"
    FONT_TITLE = ("Segoe UI", 18, "bold")
    FONT_LABEL = ("Segoe UI", 10)
    FONT_BUTTON = ("Segoe UI", 10, "bold")

    def __init__(self, platform):
        self.platform = platform
        self.root = tk.Tk()
        self.root.title("Restaurant Management System")
        self.root.geometry("900x650")
        self.root.minsize(800, 550)
        self.root.configure(bg=self.BG_COLOR)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)


        self.style = ttk.Style()
        self.style.theme_use("clam")  
        self._configure_styles()


        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief=tk.SUNKEN,
            anchor=tk.W, padding=(10, 4)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)


        self.container = ttk.Frame(self.root, padding=10)
        self.container.pack(fill=tk.BOTH, expand=True)


    def _configure_styles(self):
        """Apply custom ttk styles for a modern, consistent look."""
        # General
        self.style.configure("TLabel", background=self.CARD_BG, font=self.FONT_LABEL)
        self.style.configure("TButton", font=self.FONT_BUTTON, padding=6)
        self.style.map("TButton",
                       background=[("active", self.ACCENT), ("!active", self.PRIMARY)],
                       foreground=[("active", "white"), ("!active", "white")])
        # Card frame for login / signup
        self.style.configure("Card.TFrame", background=self.CARD_BG, relief="raised", borderwidth=1)
        # Title
        self.style.configure("Title.TLabel", font=self.FONT_TITLE, background=self.CARD_BG, foreground=self.PRIMARY)
        # Accent button
        self.style.configure("Accent.TButton", background=self.ACCENT)
        self.style.map("Accent.TButton", background=[("active", "#2980b9")])

    # ------------------------------------------------------------------
    # Utility UI builders (reusable components)
    # ------------------------------------------------------------------
    def _create_scrollable_tree(self, parent, columns, headings, height=10):
        """Create a Treeview inside a frame with vertical and horizontal scrollbars."""
        frame = ttk.Frame(parent)
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=height)
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
            tree.column(col, width=100, anchor=tk.CENTER)
        return frame, tree

    def _clear_container(self):
        """Remove all widgets from the main container."""
        for widget in self.container.winfo_children():
            widget.destroy()

    def _set_status(self, message, is_error=False):
        """Update the status bar. Optional error coloring."""
        self.status_var.set(message)
        if is_error:
            self.status_bar.configure(foreground=self.DANGER)
        else:
            self.status_bar.configure(foreground=self.PRIMARY)
        # Clear after 5 seconds
        self.root.after(5000, lambda: self.status_var.set(""))

    def _show_frame(self, frame_class, **kwargs):
        """Replace container content with a new frame built by the given method."""
        self._clear_container()
        frame = frame_class(**kwargs)
        frame.pack(fill=tk.BOTH, expand=True)
        return frame

    # ------------------------------------------------------------------
    # Page builders (return ttk.Frame instances)
    # ------------------------------------------------------------------
    def _build_login_frame(self):
        """Login card."""
        frame = ttk.Frame(self.container, style="Card.TFrame", padding=30)
        # Center card using grid
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        ttk.Label(frame, text="🍽️ Restaurant Manager", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 20))
        ttk.Label(frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        username_var = tk.StringVar()
        ttk.Entry(frame, textvariable=username_var, width=25).grid(row=1, column=1, pady=5)
        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        password_var = tk.StringVar()
        ttk.Entry(frame, textvariable=password_var, show="•", width=25).grid(row=2, column=1, pady=5)

        btn_frame = ttk.Frame(frame, style="Card.TFrame")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="Login", style="Accent.TButton",
                   command=lambda: self._login(username_var.get(), password_var.get())).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Sign Up", command=lambda: self._show_frame(self._build_signup_frame)).pack(side=tk.LEFT, padx=5)
        return frame

    def _build_signup_frame(self):
        """Registration card with role selection."""
        frame = ttk.Frame(self.container, style="Card.TFrame", padding=30)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        ttk.Label(frame, text="Create Account", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 20))

        fields = [
            ("First Name:", "first_var"),
            ("Last Name:", "last_var"),
            ("Username:", "user_var"),
            ("Password:", "pass_var"),
        ]
        vars_dict = {}
        for i, (label, var_name) in enumerate(fields, start=1):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=4)
            var = tk.StringVar()
            ttk.Entry(frame, textvariable=var, width=25, show="•" if "pass" in var_name else "").grid(row=i, column=1, pady=4)
            vars_dict[var_name] = var

        # Role selection
        ttk.Label(frame, text="Role:").grid(row=5, column=0, sticky=tk.W, pady=4)
        role_var = tk.StringVar(value="customer")
        ttk.Radiobutton(frame, text="Customer", variable=role_var, value="customer").grid(row=5, column=1, sticky=tk.W)
        ttk.Radiobutton(frame, text="Manager", variable=role_var, value="manager").grid(row=6, column=1, sticky=tk.W)

        ttk.Label(frame, text="Restaurant Name (manager):").grid(row=7, column=0, sticky=tk.W, pady=4)
        rest_var = tk.StringVar()
        ttk.Entry(frame, textvariable=rest_var, width=25).grid(row=7, column=1, pady=4)

        def submit():
            role = role_var.get()
            fname = vars_dict["first_var"].get()
            lname = vars_dict["last_var"].get()
            username = vars_dict["user_var"].get()
            password = vars_dict["pass_var"].get()
            rest_name = rest_var.get() if role == "manager" else None
            success, msg = self.platform.sign_up(role, fname, lname, username, password, rest_name)
            if success:
                self._set_status(msg)
                self._show_frame(self._build_login_frame)
            else:
                self._set_status(msg, is_error=True)

        btn_frame = ttk.Frame(frame, style="Card.TFrame")
        btn_frame.grid(row=8, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="Register", style="Accent.TButton", command=submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Back", command=lambda: self._show_frame(self._build_login_frame)).pack(side=tk.LEFT, padx=5)
        return frame

    def _build_main_menu(self):
        """Role‑based dashboard layout."""
        if self.platform.current_user.role == "manager":
            return self._build_manager_dashboard()
        else:
            return self._build_customer_dashboard()

    def _build_manager_dashboard(self):
        """Manager panel with sidebar + content area."""
        main = ttk.Frame(self.container)
        sidebar = ttk.Frame(main, width=200, style="Card.TFrame", padding=10)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        content = ttk.Frame(main, padding=20, style="Card.TFrame")
        content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        mgr = self.platform.current_user
        rest = mgr.restaurant
        ttk.Label(sidebar, text=f"🍕 {rest.name}", font=self.FONT_TITLE, background=self.CARD_BG).pack(pady=10)

        buttons = [
            ("📋 Menu", self._show_manager_menu_view),
            ("➕ Add Item", self._show_manager_add_item),
            ("✏️ Edit Item", self._show_manager_edit_item),
            ("🗑️ Delete Item", self._show_manager_delete_item),
            ("📦 Orders", self._show_manager_orders),
            ("🚪 Logout", self._logout),
        ]
        for text, cmd in buttons:
            ttk.Button(sidebar, text=text, command=lambda c=cmd: c(content), width=18).pack(pady=4)

        # Default view
        self._show_manager_menu_view(content)
        return main

    def _build_customer_dashboard(self):
        """Customer panel with restaurant list and quick actions."""
        main = ttk.Frame(self.container)
        header = ttk.Frame(main, padding=10, style="Card.TFrame")
        header.pack(fill=tk.X)
        ttk.Label(header, text=f"👤 Welcome, {self.platform.current_user.first_name}!", font=self.FONT_TITLE,
                  background=self.CARD_BG).pack(side=tk.LEFT)
        ttk.Button(header, text="Logout", command=self._logout).pack(side=tk.RIGHT)

        body = ttk.Frame(main, padding=20)
        body.pack(fill=tk.BOTH, expand=True)
        ttk.Label(body, text="Select a restaurant to view its menu:", font=self.FONT_LABEL).pack(anchor=tk.W, pady=(0,10))

        # Restaurant list with Treeview
        cols = ("name",)
        tree_frame, self.rest_tree = self._create_scrollable_tree(body, cols, ["Restaurant Name"], height=6)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        for r in self.platform.get_restaurants():
            self.rest_tree.insert("", tk.END, values=(r.name,))

        btn_row = ttk.Frame(body)
        btn_row.pack(pady=10)
        ttk.Button(btn_row, text="Open Menu", command=self._customer_open_menu).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="Order History", command=self._customer_order_history).pack(side=tk.LEFT, padx=5)

        return main

    # ------------------------------------------------------------------
    # Manager actions
    # ------------------------------------------------------------------
    def _show_manager_menu_view(self, content):
        """Populate content area with the restaurant's menu."""
        for w in content.winfo_children():
            w.destroy()
        rest = self.platform.current_user.restaurant
        cols = ("name", "price", "type", "available")
        headings = ["Name", "Price", "Type", "Available"]
        tree_frame, tree = self._create_scrollable_tree(content, cols, headings, height=12)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        for item in rest.menu:
            tree.insert("", tk.END, values=(item.name, f"${item.price:.2f}", item.type, "Yes" if item.available else "No"))

    def _show_manager_add_item(self, content):
        """Inline add item form."""
        for w in content.winfo_children():
            w.destroy()
        frame = ttk.Frame(content, padding=20, style="Card.TFrame")
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text="Add New Menu Item", font=self.FONT_TITLE).pack(pady=10)

        fields = [
            ("Name:", tk.StringVar()),
            ("Price:", tk.StringVar()),
        ]
        for label, var in fields:
            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=4)
            ttk.Label(row, text=label, width=10).pack(side=tk.LEFT)
            ttk.Entry(row, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Label(frame, text="Type:").pack(anchor=tk.W, pady=(10,0))
        type_var = tk.StringVar(value="food")
        ttk.OptionMenu(frame, type_var, "food", "food", "drink").pack(anchor=tk.W)

        avail_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Available", variable=avail_var).pack(anchor=tk.W, pady=5)

        def add_item():
            try:
                price = float(fields[1][1].get())
                item = MenuItem(fields[0][1].get(), price, type_var.get(), avail_var.get())
                self.platform.current_user.add_menu_item(item)
                self.platform.save()
                self._set_status("Item added successfully.")
                self._show_manager_menu_view(content)  # refresh view
            except ValueError:
                self._set_status("Invalid price. Please enter a number.", is_error=True)

        ttk.Button(frame, text="Add Item", style="Accent.TButton", command=add_item).pack(pady=15)

    def _show_manager_edit_item(self, content):
        """Edit item: tree selection + pre-populated form."""
        for w in content.winfo_children():
            w.destroy()
        rest = self.platform.current_user.restaurant
        if not rest.menu:
            ttk.Label(content, text="Menu is empty.", font=self.FONT_LABEL).pack(expand=True)
            return

        top = ttk.Frame(content)
        top.pack(fill=tk.BOTH, expand=True)

        cols = ("name", "price", "type", "avail")
        headings = ["Name", "Price", "Type", "Available"]
        tree_frame, tree = self._create_scrollable_tree(top, cols, headings, height=6)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        for idx, item in enumerate(rest.menu):
            tree.insert("", tk.END, iid=str(idx), values=(item.name, f"{item.price:.2f}", item.type, "Yes" if item.available else "No"))

        form = ttk.LabelFrame(content, text="Edit Selected Item", padding=15)
        form.pack(fill=tk.X, pady=10)

        name_var = tk.StringVar()
        price_var = tk.StringVar()
        type_var = tk.StringVar(value="food")
        avail_var = tk.BooleanVar(value=True)

        # Form grid
        ttk.Label(form, text="New Name:").grid(row=0, column=0, sticky=tk.W, pady=4)
        ttk.Entry(form, textvariable=name_var).grid(row=0, column=1, sticky=tk.EW, padx=5)
        ttk.Label(form, text="New Price:").grid(row=1, column=0, sticky=tk.W, pady=4)
        ttk.Entry(form, textvariable=price_var).grid(row=1, column=1, sticky=tk.EW, padx=5)
        ttk.Label(form, text="Type:").grid(row=2, column=0, sticky=tk.W, pady=4)
        ttk.OptionMenu(form, type_var, "food", "food", "drink").grid(row=2, column=1, sticky=tk.W, padx=5)
        ttk.Checkbutton(form, text="Available", variable=avail_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        form.grid_columnconfigure(1, weight=1)

        def on_select(event):
            sel = tree.selection()
            if not sel:
                return
            idx = int(sel[0])
            item = rest.menu[idx]
            name_var.set(item.name)
            price_var.set(str(item.price))
            type_var.set(item.type)
            avail_var.set(item.available)

        tree.bind("<<TreeviewSelect>>", on_select)

        def update_item():
            sel = tree.selection()
            if not sel:
                self._set_status("Select an item first.", is_error=True)
                return
            idx = int(sel[0])
            # Verify item still exists at that index (robustness)
            if idx >= len(rest.menu):
                self._set_status("Menu changed externally. Refresh and try again.", is_error=True)
                return
            try:
                new_price = float(price_var.get())
                new_item = MenuItem(name_var.get(), new_price, type_var.get(), avail_var.get())
                self.platform.current_user.edit_menu_item(idx, new_item)
                self.platform.save()
                self._set_status("Item updated.")
                self._show_manager_edit_item(content)  # refresh
            except ValueError:
                self._set_status("Invalid price.", is_error=True)

        ttk.Button(content, text="Update Selected", style="Accent.TButton", command=update_item).pack(pady=10)

    def _show_manager_delete_item(self, content):
        """Delete item with confirmation."""
        for w in content.winfo_children():
            w.destroy()
        rest = self.platform.current_user.restaurant
        if not rest.menu:
            ttk.Label(content, text="Menu empty.", font=self.FONT_LABEL).pack(expand=True)
            return

        cols = ("name", "price", "type")
        headings = ["Name", "Price", "Type"]
        tree_frame, tree = self._create_scrollable_tree(content, cols, headings, height=8)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        for idx, item in enumerate(rest.menu):
            tree.insert("", tk.END, iid=str(idx), values=(item.name, f"${item.price:.2f}", item.type))

        def delete():
            sel = tree.selection()
            if not sel:
                self._set_status("Select an item.", is_error=True)
                return
            idx = int(sel[0])
            if not messagebox.askyesno("Confirm", f"Delete '{rest.menu[idx].name}'?"):
                return
            self.platform.current_user.delete_menu_item(idx)
            self.platform.save()
            self._set_status("Item deleted.")
            self._show_manager_delete_item(content)

        ttk.Button(content, text="Delete Selected", command=delete).pack(pady=10)

    def _show_manager_orders(self, content):
        """Order history for the manager."""
        for w in content.winfo_children():
            w.destroy()
        rest = self.platform.current_user.restaurant
        cols = ("id", "customer", "items", "total", "datetime")
        headings = ["Order ID", "Customer ID", "Items", "Total", "Date"]
        tree_frame, tree = self._create_scrollable_tree(content, cols, headings, height=10)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        for order in rest.orders:
            items_desc = ", ".join(f"{i.name}(${i.price:.2f})" for i in order.items)
            tree.insert("", tk.END, values=(order.id, order.customer_id, items_desc, f"${order.total_price():.2f}", order.datetime))

    # ------------------------------------------------------------------
    # Customer actions
    # ------------------------------------------------------------------
    def _customer_open_menu(self):
        """Open selected restaurant's menu in a new top-level window."""
        sel = self.rest_tree.selection()
        if not sel:
            self._set_status("Please select a restaurant.", is_error=True)
            return
        rest_name = self.rest_tree.item(sel[0])["values"][0]
        restaurant = next((r for r in self.platform.get_restaurants() if r.name == rest_name), None)
        if not restaurant:
            self._set_status("Restaurant not found.", is_error=True)
            return
        self._show_restaurant_menu_window(restaurant)

    def _show_restaurant_menu_window(self, restaurant):
        """Toplevel with menu, cart, and checkout."""
        win = tk.Toplevel(self.root)
        win.title(f"Menu – {restaurant.name}")
        win.geometry("800x600")
        win.minsize(700, 500)
        win.configure(bg=self.BG_COLOR)

        # Menu Treeview
        cols = ("name", "price", "type", "avail")
        tree_frame, tree = self._create_scrollable_tree(win, cols, ["Item", "Price", "Type", "Available"], height=8)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for item in restaurant.menu:
            tree.insert("", tk.END, values=(item.name, f"${item.price:.2f}", item.type, "Yes" if item.available else "No"))

        # Cart frame
        cart_frame = ttk.LabelFrame(win, text="🧺 Your Cart", padding=10)
        cart_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

        cart_listbox = tk.Listbox(cart_frame, height=4, font=self.FONT_LABEL)
        cart_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        cart_scroll = ttk.Scrollbar(cart_frame, orient=tk.VERTICAL, command=cart_listbox.yview)
        cart_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        cart_listbox.config(yscrollcommand=cart_scroll.set)

        total_var = tk.StringVar(value="Total: $0.00")
        ttk.Label(win, textvariable=total_var, font=("Segoe UI", 12, "bold"), background=self.BG_COLOR).pack(anchor=tk.E, padx=20)

        customer = self.platform.current_user

        def refresh_cart():
            cart_listbox.delete(0, tk.END)
            total = 0.0
            for item in customer.cart:
                cart_listbox.insert(tk.END, f"{item.name} - ${item.price:.2f}")
                total += item.price
            total_var.set(f"Total: ${total:.2f}")

        def add_to_cart():
            sel = tree.selection()
            if not sel:
                self._set_status("Select an item.", is_error=True)
                return
            values = tree.item(sel[0])["values"]
            name, price_str, _, avail = values
            if avail != "Yes":
                messagebox.showwarning("Unavailable", "This item is currently unavailable.", parent=win)
                return
            price = float(price_str.replace("$", ""))
            item = next((i for i in restaurant.menu if i.name == name and i.price == price), None)
            if item:
                customer.add_to_cart(item)
                refresh_cart()
                self._set_status(f"Added '{item.name}' to cart.")

        def remove_from_cart():
            sel = cart_listbox.curselection()
            if sel:
                customer.remove_from_cart(sel[0])
                refresh_cart()

        def checkout():
            if not customer.cart:
                messagebox.showinfo("Empty Cart", "Add items to your cart first.", parent=win)
                return
            order = self.platform.checkout(customer, restaurant)
            if order:
                messagebox.showinfo("Order Placed",
                                    f"Order #{order.id} confirmed.\nTotal: ${order.total_price():.2f}",
                                    parent=win)
                customer.cart.clear()
                refresh_cart()
                win.destroy()

        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add to Cart", command=add_to_cart).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remove Selected", command=remove_from_cart).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Checkout", style="Accent.TButton", command=checkout).pack(side=tk.LEFT, padx=5)

        refresh_cart()

    def _customer_order_history(self):
        """Show order history in a new window."""
        orders = self.platform.get_customer_orders(self.platform.current_user)
        win = tk.Toplevel(self.root)
        win.title("Order History")
        win.geometry("750x400")
        cols = ("id", "restaurant", "items", "total", "datetime")
        headings = ["Order ID", "Restaurant", "Items", "Total", "Date"]
        tree_frame, tree = self._create_scrollable_tree(win, cols, headings, height=10)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for o in orders:
            items_desc = ", ".join(f"{i.name}" for i in o.items)
            tree.insert("", tk.END, values=(o.id, o.restaurant_name, items_desc, f"${o.total_price():.2f}", o.datetime))

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------
    def _login(self, username, password):
        success, msg = self.platform.sign_in(username, password)
        if success:
            self._set_status("Login successful")
            self._show_main_menu()
        else:
            self._set_status(msg, is_error=True)

    def _logout(self, _=None):
        """Log out the current user. The optional parameter is for compatibility with sidebar lambda calls."""
        self.platform.logout()
        self.platform.save()
        self._set_status("Logged out.")
        self._show_frame(self._build_login_frame)

    def _show_main_menu(self):
        """Switch to role-based dashboard."""
        self._clear_container()
        frame = self._build_main_menu()
        frame.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # Entry points
    # ------------------------------------------------------------------
    def run(self):
        """Start the GUI event loop with login screen."""
        self._show_frame(self._build_login_frame)
        self.root.mainloop()

    def _on_close(self):
        """Save data on window close."""
        try:
            self.platform.save()
        except Exception:
            pass
        self.root.destroy()