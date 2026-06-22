import tkinter as tk
from tkinter import ttk, messagebox
from models import MenuItem
from pathlib import Path

class App:
    LIGHT_THEME = {
        "bg": "#f5f7fa",
        "card": "#ffffff",
        "primary": "#1a2639",
        "accent": "#3a7bd5",
        "accent_hover": "#2e6bc0",
        "success": "#2ecc71",
        "danger": "#e74c3c",
        "danger_hover": "#c0392b",
        "text": "#2c3e50",
        "text_light": "#7f8c8d",
        "button_fg": "#ffffff",
        "button_bg": "#3a7bd5",
        "sidebar_bg": "#e8edf2",
        "tree_bg": "#ffffff",
        "tree_bg_alt": "#f9f9fc",
        "tree_fg": "#2c3e50",
        "status_bg": "#ecf0f1",
        "status_fg": "#2c3e50",
        "border": "#dcdfe3",
        "shadow": "#e0e4e8",
        "cart_highlight": "#d5f5e3",
    }

    DARK_THEME = {
        "bg": "#1a1c23",
        "card": "#252732",
        "primary": "#e0e0e0",
        "accent": "#4a90d9",
        "accent_hover": "#3a7bc8",
        "success": "#2ecc71",
        "danger": "#e74c3c",
        "danger_hover": "#c0392b",
        "text": "#d0d0d0",
        "text_light": "#9099a0",
        "button_fg": "#ffffff",
        "button_bg": "#4a90d9",
        "sidebar_bg": "#1e2030",
        "tree_bg": "#1e2030",
        "tree_bg_alt": "#282b3a",
        "tree_fg": "#d0d0d0",
        "status_bg": "#1e2030",
        "status_fg": "#d0d0d0",
        "border": "#3f414a",
        "shadow": "#16181f",
        "cart_highlight": "#1e4d2b",
    }

    FONT_TITLE = ("Segoe UI", 20, "bold")
    FONT_SUBTITLE = ("Segoe UI", 12, "bold")
    FONT_LABEL = ("Segoe UI", 11)
    FONT_BUTTON = ("Segoe UI", 11, "bold")
    FONT_SMALL = ("Segoe UI", 9)

    def __init__(self, platform):
        self.platform = platform
        self.root = tk.Tk()
        self.root.title("Restaurant Management System")
        self.root.geometry("960x680")
        self.root.minsize(850, 580)
        self.root.configure(bg=self.LIGHT_THEME["bg"])
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.theme_colors = self.LIGHT_THEME.copy()
        self.is_dark_mode = False
        self._status_after_id = None
        self.open_windows = []

        self._configure_styles()

        self.top_bar = ttk.Frame(self.root, style="TopBar.TFrame", padding=(0, 5, 10, 5))
        self.top_bar.pack(fill="x", side="top")
        self.theme_btn = ttk.Button(
            self.top_bar,
            text="🌙 Dark Mode",
            style="Theme.TButton",
            command=self._toggle_theme,
        )
        self.theme_btn.pack(side="right")

        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            font=self.FONT_SMALL,
            bg=self.theme_colors["status_bg"],
            fg=self.theme_colors["status_fg"],
            padx=12,
            pady=6,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.theme_colors["border"],
        )
        self.status_bar.pack(side="bottom", fill="x")

        self.container = ttk.Frame(self.root, padding=15)
        self.container.pack(fill="both", expand=True)

    def _configure_styles(self):
        colors = self.theme_colors
        self.style.configure(".", background=colors["bg"], foreground=colors["text"], font=self.FONT_LABEL)
        self.style.configure("TLabel", background=colors["bg"], foreground=colors["text"], font=self.FONT_LABEL)
        self.style.configure("Card.TLabel", background=colors["card"], foreground=colors["text"], font=self.FONT_LABEL)
        self.style.configure("Title.TLabel", font=self.FONT_TITLE, background=colors["card"], foreground=colors["primary"])
        self.style.configure("Subtitle.TLabel", font=self.FONT_SUBTITLE, background=colors["card"], foreground=colors["primary"])
        self.style.configure("TButton", font=self.FONT_BUTTON, borderwidth=0, relief="flat", padding=(10, 6),
                             background=colors["button_bg"], foreground=colors["button_fg"], focuscolor="none",
                             bordercolor=colors["button_bg"])
        self.style.map("TButton", background=[("active", colors["accent_hover"]), ("!active", colors["button_bg"])],
                       foreground=[("active", colors["button_fg"]), ("!active", colors["button_fg"])])
        self.style.configure("Accent.TButton", font=self.FONT_BUTTON, borderwidth=0, relief="flat", padding=(16, 8),
                             background=colors["accent"], foreground="white")
        self.style.map("Accent.TButton", background=[("active", colors["accent_hover"]), ("!active", colors["accent"])])
        self.style.configure("Theme.TButton", font=self.FONT_SMALL, borderwidth=1, relief="solid", padding=(8, 4),
                             background=colors["card"], foreground=colors["accent"], bordercolor=colors["border"])
        self.style.map("Theme.TButton", background=[("active", colors["sidebar_bg"])],
                       foreground=[("active", colors["accent_hover"])])
        self.style.configure("TopBar.TFrame", background=colors["bg"])
        self.style.configure("Card.TFrame", background=colors["card"], relief="flat", borderwidth=0)
        self.style.configure("Sidebar.TFrame", background=colors["sidebar_bg"])
        self.style.configure("Treeview", background=colors["tree_bg"], foreground=colors["tree_fg"],
                             fieldbackground=colors["tree_bg"], borderwidth=0, font=self.FONT_LABEL)
        self.style.map("Treeview", foreground=[("selected", "white")], background=[("selected", colors["accent"])])
        self.style.configure("Treeview.Heading", font=self.FONT_SUBTITLE, background=colors["sidebar_bg"],
                             foreground=colors["primary"], relief="flat")
        self.style.map("Treeview.Heading", background=[("active", colors["accent"])])
        self.style.configure("TEntry", fieldbackground=colors["card"], foreground=colors["text"],
                             borderwidth=1, relief="solid", bordercolor=colors["border"])
        self.style.configure("TCheckbutton", background=colors["bg"], foreground=colors["text"])
        self.style.configure("TRadiobutton", background=colors["bg"], foreground=colors["text"])
        self.style.configure("TCombobox", fieldbackground=colors["card"], background=colors["button_bg"],
                             foreground=colors["text"], arrowcolor=colors["text"])
        self.style.map("TCombobox", fieldbackground=[("readonly", colors["card"])],
                       foreground=[("readonly", colors["text"])])
        self.root.configure(bg=colors["bg"])
        if hasattr(self, "status_bar"):
            self.status_bar.configure(bg=colors["status_bg"], fg=colors["status_fg"],
                                      highlightbackground=colors["border"])
        if hasattr(self, "top_bar"):
            self.top_bar.configure(style="TopBar.TFrame")

    def _toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.theme_colors = self.DARK_THEME.copy()
            self.theme_btn.configure(text="☀️ Light Mode")
        else:
            self.theme_colors = self.LIGHT_THEME.copy()
            self.theme_btn.configure(text="🌙 Dark Mode")
        self._configure_styles()
        for win in self.open_windows:
            try:
                win.destroy()
            except tk.TclError:
                pass
        self.open_windows.clear()
        if self.platform.current_user:
            self._show_main_menu()
        else:
            self._show_frame(self._build_login_frame)

    def _clear_widget(self, parent):
        for w in parent.winfo_children():
            w.destroy()

    def _show_empty_message(self, parent, text):
        return ttk.Label(parent, text=text, font=self.FONT_LABEL, style="Card.TLabel", anchor="center")

    def _set_tree_alternating_colors(self, tree, highlight_in_cart=False, cart_items=None):
        colors = self.theme_colors
        tree.tag_configure("odd", background=colors["tree_bg_alt"])
        if highlight_in_cart and cart_items is not None:
            tree.tag_configure("in_cart", background=colors["cart_highlight"])
        children = tree.get_children()
        for i, child in enumerate(children):
            tags = ["odd"] if i % 2 == 1 else []
            if highlight_in_cart and cart_items:
                item_name = tree.item(child, "values")[0]
                if item_name in cart_items:
                    tags.append("in_cart")
            tree.item(child, tags=tuple(tags))

    def _create_scrollable_tree(self, parent, columns, headings, height=10):
        frame = ttk.Frame(parent)
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=height, selectmode="browse")
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
            tree.column(col, width=110, anchor="center", minwidth=80)
        return frame, tree

    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def _set_status(self, message, is_error=False):
        if self._status_after_id is not None:
            self.root.after_cancel(self._status_after_id)
            self._status_after_id = None
        self.status_var.set(message)
        if is_error:
            self.status_bar.configure(fg=self.theme_colors["danger"])
        else:
            self.status_bar.configure(fg=self.theme_colors["success"])
        self._status_after_id = self.root.after(4000, lambda: self.status_var.set(""))

    def _show_frame(self, frame_class, **kwargs):
        self._clear_container()
        frame = frame_class(**kwargs)
        frame.pack(fill="both", expand=True)
        return frame

    def _build_login_frame(self):
        outer = ttk.Frame(self.container)
        card = ttk.Frame(outer, style="Card.TFrame", padding=40)
        card.place(relx=0.5, rely=0.5, anchor="center")
        ttk.Label(card, text="🍽️ Restaurant Manager", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 25))
        ttk.Label(card, text="Username", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=(5, 0))
        username_var = tk.StringVar()
        username_entry = ttk.Entry(card, textvariable=username_var, width=30)
        username_entry.grid(row=1, column=1, padx=(15, 0), pady=(5, 0), sticky="ew")
        username_entry.focus_set()
        ttk.Label(card, text="Password", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=(10, 0))
        password_var = tk.StringVar()
        password_entry = ttk.Entry(card, textvariable=password_var, show="•", width=30)
        password_entry.grid(row=2, column=1, padx=(15, 0), pady=(10, 0), sticky="ew")
        card.bind("<Return>", lambda e: self._login(username_var.get(), password_var.get()))
        username_entry.bind("<Return>", lambda e: password_entry.focus_set())
        password_entry.bind("<Return>", lambda e: self._login(username_var.get(), password_var.get()))
        btn_frame = ttk.Frame(card, style="Card.TFrame")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(25, 10))
        ttk.Button(btn_frame, text="Login", style="Accent.TButton",
                   command=lambda: self._login(username_var.get(), password_var.get())).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Sign Up",
                   command=lambda: self._show_frame(self._build_signup_frame)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Quit", command=self._on_close).pack(side="right", padx=(30, 5))
        card.grid_columnconfigure(1, weight=1)
        return outer

    def _build_signup_frame(self):
        outer = ttk.Frame(self.container)
        card = ttk.Frame(outer, style="Card.TFrame", padding=40)
        card.place(relx=0.5, rely=0.5, anchor="center")
        ttk.Label(card, text="Create Account", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 20))
        fields = [("First Name", "first_var"), ("Last Name", "last_var"), ("Username", "user_var"), ("Password", "pass_var")]
        vars_dict = {}
        entry_widgets = []
        for i, (label, var_name) in enumerate(fields, start=1):
            ttk.Label(card, text=label + ":", style="Card.TLabel").grid(row=i, column=0, sticky="w", pady=4)
            show = "•" if "pass" in var_name else ""
            var = tk.StringVar()
            entry = ttk.Entry(card, textvariable=var, width=30, show=show)
            entry.grid(row=i, column=1, padx=(15, 0), pady=4, sticky="ew")
            vars_dict[var_name] = var
            entry_widgets.append(entry)
        ttk.Label(card, text="Role:", style="Card.TLabel").grid(row=5, column=0, sticky="w", pady=(10, 0))
        role_var = tk.StringVar(value="customer")
        ttk.Radiobutton(card, text="Customer", variable=role_var, value="customer").grid(row=5, column=1, sticky="w", padx=(15, 0))
        ttk.Radiobutton(card, text="Manager", variable=role_var, value="manager").grid(row=6, column=1, sticky="w", padx=(15, 0))
        ttk.Label(card, text="Restaurant Name:", style="Card.TLabel").grid(row=7, column=0, sticky="w", pady=(10, 0))
        rest_var = tk.StringVar()
        rest_entry = ttk.Entry(card, textvariable=rest_var, width=30)
        rest_entry.grid(row=7, column=1, padx=(15, 0), pady=(10, 0), sticky="ew")
        entry_widgets.append(rest_entry)
        def submit():
            self._signup_submit(role_var.get(), vars_dict["first_var"].get(), vars_dict["last_var"].get(),
                                vars_dict["user_var"].get(), vars_dict["pass_var"].get(), rest_var.get())
        rest_entry.bind("<Return>", lambda e: submit())
        card.bind("<Return>", lambda e: submit())
        btn_frame = ttk.Frame(card, style="Card.TFrame")
        btn_frame.grid(row=8, column=0, columnspan=2, pady=(25, 10))
        ttk.Button(btn_frame, text="Register", style="Accent.TButton", command=submit).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Back", command=lambda: self._show_frame(self._build_login_frame)).pack(side="left", padx=5)
        card.grid_columnconfigure(1, weight=1)
        return outer

    def _signup_submit(self, role, fname, lname, username, password, rest_name):
        success, msg = self.platform.sign_up(role, fname, lname, username, password, rest_name if role == "manager" else None)
        if success:
            self._set_status(msg)
            self._show_frame(self._build_login_frame)
        else:
            self._set_status(msg, is_error=True)

    def _build_main_menu(self):
        if self.platform.current_user.role == "manager":
            return self._build_manager_dashboard()
        else:
            return self._build_customer_dashboard()


    def _build_manager_dashboard(self):
        main = ttk.Frame(self.container)
        sidebar = tk.Frame(main, bg=self.theme_colors["sidebar_bg"], width=220, padx=10, pady=20, highlightthickness=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        content = ttk.Frame(main, padding=20)
        content.pack(side="right", fill="both", expand=True)
        mgr = self.platform.current_user
        rest = mgr.restaurant
        tk.Label(sidebar, text=f"🍕 {rest.name}", font=self.FONT_SUBTITLE,
                 bg=self.theme_colors["sidebar_bg"], fg=self.theme_colors["primary"]).pack(pady=(0, 20))
        button_specs = [
            ("📋  Menu", self._show_manager_menu_view),
            ("📦  Orders", self._show_manager_orders),
            ("➕  Add Item", self._show_manager_add_item),
            ("✏️  Edit Item", self._show_manager_edit_item),
            ("🗑️  Delete Item", self._show_manager_delete_item),
            ("🚪  Logout", self._logout),
        ]
        self.sidebar_buttons = []
        self.active_sidebar_btn = None
        for text, cmd in button_specs:
            btn = tk.Button(sidebar, text=text, font=self.FONT_BUTTON, bg=self.theme_colors["button_bg"],
                            fg=self.theme_colors["button_fg"], activebackground=self.theme_colors["accent_hover"],
                            activeforeground="white", bd=0, relief="flat", padx=10, pady=8, width=18, anchor="w",
                            command=lambda c=cmd: c(content))
            btn.pack(pady=3, fill="x")
            btn.bind("<Button-1>", lambda e, b=btn: self._highlight_sidebar_button(b))
            btn.bind("<Enter>", lambda e, b=btn: self._set_sidebar_button_color(b, "hover"))
            btn.bind("<Leave>", lambda e, b=btn: self._set_sidebar_button_color(b, "normal"))
            self.sidebar_buttons.append(btn)
        if self.sidebar_buttons:
            self._highlight_sidebar_button(self.sidebar_buttons[0])
        self._show_manager_menu_view(content)
        return main

    def _set_sidebar_button_color(self, btn, state):
        if btn is self.active_sidebar_btn:
            btn.configure(bg=self.theme_colors["accent"] if state == "normal" else self.theme_colors["accent_hover"])
        else:
            btn.configure(bg=self.theme_colors["button_bg"] if state == "normal" else self.theme_colors["accent_hover"])

    def _highlight_sidebar_button(self, btn):
        for b in self.sidebar_buttons:
            b.configure(bg=self.theme_colors["button_bg"])
        btn.configure(bg=self.theme_colors["accent"])
        self.active_sidebar_btn = btn


    def _show_manager_menu_view(self, content):
        self._clear_widget(content)
        rest = self.platform.current_user.restaurant
        if not rest.menu:
            self._show_empty_message(content, "No menu items yet.\nClick 'Add Item' to create one.").pack(expand=True)
            return

        categories = {}
        for item in rest.menu:
            categories.setdefault(item.type, []).append(item)
        for cat, items in categories.items():
            cat_frame = ttk.LabelFrame(content, text=cat.capitalize(), padding=10)
            cat_frame.pack(fill="x", pady=5)
            cols = ("name", "price", "available", "image")
            tree_frame, tree = self._create_scrollable_tree(cat_frame, cols,
                                                             ["Name", "Price", "Available", "Image"], height=len(items))
            tree_frame.pack(fill="both", expand=True)
            for item in items:
                img_text = "No image"
                if item.image_path:
                    img = self._try_load_image(item.image_path)
                    if img:
                        img_text = "🖼️"
                        # For simplicity, we just show "Yes" or "No". A real implementation would use a canvas or label.
                        # We'll just display "Yes" if image_path exists.
                        img_text = "Yes" if Path(item.image_path).exists() else "No"
                    else:
                        img_text = "No"
                else:
                    img_text = "No"
                tree.insert("", "end", values=(item.name, f"${item.price:.2f}",
                                               "Yes" if item.available else "No",
                                               img_text))
            self._set_tree_alternating_colors(tree)

    def _show_manager_add_item(self, content):
        self._clear_widget(content)
        frame = ttk.Frame(content, padding=25)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Add New Menu Item", style="Title.TLabel").pack(pady=(0, 20))
        name_var = tk.StringVar()
        ttk.Label(frame, text="Name:", style="Card.TLabel").pack(anchor="w")
        name_entry = ttk.Entry(frame, textvariable=name_var, width=40)
        name_entry.pack(fill="x", pady=(2, 10))
        price_var = tk.StringVar()
        ttk.Label(frame, text="Price:", style="Card.TLabel").pack(anchor="w")
        price_entry = ttk.Entry(frame, textvariable=price_var, width=40)
        price_entry.pack(fill="x", pady=(2, 10))
        ttk.Label(frame, text="Type:", style="Card.TLabel").pack(anchor="w")
        type_var = tk.StringVar(value="food")
        type_combo = ttk.Combobox(frame, textvariable=type_var, values=["food", "drink", "dessert"],
                                  state="readonly", width=38)
        type_combo.pack(anchor="w", pady=(2, 10))
        avail_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Available", variable=avail_var).pack(anchor="w", pady=(2, 10))
        ttk.Label(frame, text="Image path (optional):", style="Card.TLabel").pack(anchor="w")
        img_var = tk.StringVar()
        ttk.Entry(frame, textvariable=img_var, width=40).pack(fill="x", pady=(2, 10))
        def add_item():
            name = name_var.get().strip()
            if not name:
                self._set_status("Name cannot be empty.", is_error=True)
                return
            try:
                price = float(price_var.get())
                if price <= 0:
                    self._set_status("Price must be positive.", is_error=True)
                    return
                img_path = img_var.get().strip() or None
                item = MenuItem(name, price, type_var.get(), avail_var.get(), img_path)
                self.platform.current_user.add_menu_item(item)
                self.platform.save()
                self._set_status("Item added successfully.")
                self._show_manager_menu_view(content)
            except ValueError:
                self._set_status("Invalid price.", is_error=True)
        ttk.Button(frame, text="Add Item", style="Accent.TButton", command=add_item).pack(pady=10)

    def _show_manager_edit_item(self, content):
        self._clear_widget(content)
        rest = self.platform.current_user.restaurant
        if not rest.menu:
            self._show_empty_message(content, "No menu items to edit.").pack(expand=True)
            return
        cols = ("name", "price", "type", "avail")
        tree_frame, tree = self._create_scrollable_tree(content, cols,
                                                         ["Name", "Price", "Type", "Available"], height=6)
        tree_frame.pack(fill="both", expand=True, pady=(0, 15))
        for idx, item in enumerate(rest.menu):
            tree.insert("", "end", iid=str(idx),
                        values=(item.name, f"${item.price:.2f}", item.type, "Yes" if item.available else "No"))
        self._set_tree_alternating_colors(tree)
        form = ttk.LabelFrame(content, text="Edit Selected Item", padding=20)
        form.pack(fill="x", pady=10)
        name_var = tk.StringVar()
        price_var = tk.StringVar()
        type_var = tk.StringVar(value="food")
        avail_var = tk.BooleanVar(value=True)
        img_var = tk.StringVar()
        ttk.Label(form, text="New Name:", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=name_var, width=30).grid(row=0, column=1, padx=(15, 0), pady=4, sticky="ew")
        ttk.Label(form, text="New Price:", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=price_var, width=30).grid(row=1, column=1, padx=(15, 0), pady=4, sticky="ew")
        ttk.Label(form, text="Type:", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=4)
        type_combo = ttk.Combobox(form, textvariable=type_var, values=["food", "drink", "dessert"],
                                  state="readonly", width=28)
        type_combo.grid(row=2, column=1, padx=(15, 0), sticky="w", pady=4)
        ttk.Checkbutton(form, text="Available", variable=avail_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=4)
        ttk.Label(form, text="Image path:", style="Card.TLabel").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=img_var, width=30).grid(row=4, column=1, padx=(15, 0), pady=4, sticky="ew")
        form.grid_columnconfigure(1, weight=1)
        def on_select(event):
            sel = tree.selection()
            if not sel:
                return
            idx = int(sel[0])
            if idx >= len(rest.menu):
                return
            item = rest.menu[idx]
            name_var.set(item.name)
            price_var.set(str(item.price))
            type_var.set(item.type)
            avail_var.set(item.available)
            img_var.set(item.image_path or "")
        tree.bind("<<TreeviewSelect>>", on_select)
        def update_item():
            sel = tree.selection()
            if not sel:
                self._set_status("Select an item first.", is_error=True)
                return
            idx = int(sel[0])
            if idx >= len(rest.menu):
                self._set_status("Menu changed externally.", is_error=True)
                return
            name = name_var.get().strip()
            if not name:
                self._set_status("Name cannot be empty.", is_error=True)
                return
            try:
                new_price = float(price_var.get())
                if new_price <= 0:
                    self._set_status("Price must be positive.", is_error=True)
                    return
                new_img = img_var.get().strip() or None
                new_item = MenuItem(name, new_price, type_var.get(), avail_var.get(), new_img)
                self.platform.current_user.edit_menu_item(idx, new_item)
                self.platform.save()
                self._set_status("Item updated.")
                self._show_manager_edit_item(content)
            except ValueError:
                self._set_status("Invalid price.", is_error=True)
        ttk.Button(content, text="Update Selected", style="Accent.TButton", command=update_item).pack(pady=10)

    def _show_manager_delete_item(self, content):
        self._clear_widget(content)
        rest = self.platform.current_user.restaurant
        if not rest.menu:
            self._show_empty_message(content, "No menu items to delete.").pack(expand=True)
            return
        cols = ("name", "price", "type")
        tree_frame, tree = self._create_scrollable_tree(content, cols, ["Name", "Price", "Type"], height=8)
        tree_frame.pack(fill="both", expand=True, pady=(0, 15))
        for idx, item in enumerate(rest.menu):
            tree.insert("", "end", iid=str(idx), values=(item.name, f"${item.price:.2f}", item.type))
        self._set_tree_alternating_colors(tree)
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
        ttk.Button(content, text="Delete Selected", style="Accent.TButton", command=delete).pack(pady=10)

    def _show_manager_orders(self, content):
        self._clear_widget(content)
        rest = self.platform.current_user.restaurant
        if not rest.orders:
            self._show_empty_message(content, "No orders yet.").pack(expand=True)
            return
        cols = ("id", "customer", "items", "total", "datetime")
        tree_frame, tree = self._create_scrollable_tree(content, cols,
                                                         ["Order ID", "Customer ID", "Items", "Total", "Date"], height=10)
        tree_frame.pack(fill="both", expand=True)
        for order in rest.orders:
            items_desc = ", ".join(f"{i.name}(${i.price:.2f})" for i in order.items)
            tree.insert("", "end", values=(order.id, order.customer_id, items_desc,
                                           f"${order.total_price():.2f}", order.datetime))
        self._set_tree_alternating_colors(tree)


    def _build_customer_dashboard(self):
        main = ttk.Frame(self.container)
        header = tk.Frame(main, bg=self.theme_colors["sidebar_bg"], padx=15, pady=10)
        header.pack(fill="x")
        tk.Label(header, text=f"👤 Welcome, {self.platform.current_user.first_name}!",
                 font=self.FONT_TITLE, bg=self.theme_colors["sidebar_bg"],
                 fg=self.theme_colors["primary"]).pack(side="left")
        tk.Button(header, text="Logout", font=self.FONT_BUTTON, bg=self.theme_colors["danger"],
                  fg="white", bd=0, relief="flat", padx=15, pady=5,
                  activebackground=self.theme_colors["danger_hover"],
                  command=self._logout).pack(side="right")
        body = ttk.Frame(main, padding=20)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Select a restaurant to view its menu:",
                  font=self.FONT_SUBTITLE, style="Card.TLabel").pack(anchor="w", pady=(0, 10))
        cols = ("name",)
        tree_frame, self.rest_tree = self._create_scrollable_tree(body, cols, ["Restaurant Name"], height=4)
        tree_frame.pack(fill="both", expand=True, pady=5)
        restaurants = self.platform.get_restaurants()
        for r in restaurants:
            self.rest_tree.insert("", "end", values=(r.name,))
        self._set_tree_alternating_colors(self.rest_tree)
        btn_row = ttk.Frame(body)
        btn_row.pack(pady=15)
        ttk.Button(btn_row, text="Open Menu", command=self._customer_open_menu).pack(side="left", padx=5)
        ttk.Button(btn_row, text="View Cart", command=self._customer_view_cart).pack(side="left", padx=5)
        ttk.Button(btn_row, text="Order History", command=self._customer_order_history).pack(side="left", padx=5)
        return main

    def _customer_open_menu(self):
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
        win = tk.Toplevel(self.root)
        self.open_windows.append(win)
        win.title(f"Menu – {restaurant.name}")
        win.geometry("900x700")
        win.minsize(700, 550)
        win.configure(bg=self.theme_colors["bg"])
        win.protocol("WM_DELETE_WINDOW", lambda: self._close_toplevel(win))

        categories = {}
        for item in restaurant.menu:
            categories.setdefault(item.type, []).append(item)

        if len(categories) > 1:
            notebook = ttk.Notebook(win)
            notebook.pack(fill="both", expand=True, padx=10, pady=10)
            for cat, items in categories.items():
                tab = ttk.Frame(notebook)
                notebook.add(tab, text=cat.capitalize())
                self._build_menu_tab(tab, items, restaurant)
        else:
            self._build_menu_tab(win, restaurant.menu, restaurant)

    def _build_menu_tab(self, parent, items, restaurant):
        cols = ("name", "price", "type", "avail")
        tree_frame, tree = self._create_scrollable_tree(parent, cols,
                                                         ["Item", "Price", "Type", "Available"], height=8)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=15)
        for idx, item in enumerate(items):
            tree.insert("", "end", iid=str(idx),
                        values=(item.name, f"${item.price:.2f}", item.type,
                                "Yes" if item.available else "No"))
        customer = self.platform.current_user
        cart_item_names = [item.name for item, rname in customer.cart if rname == restaurant.name]
        self._set_tree_alternating_colors(tree, highlight_in_cart=True, cart_items=cart_item_names)

        bottom = ttk.Frame(parent)
        bottom.pack(fill="x", padx=15, pady=5)
        total_var = tk.StringVar(value=f"Total items in cart: {len(customer.cart)}")
        tk.Label(bottom, textvariable=total_var, font=self.FONT_LABEL,
                 bg=self.theme_colors["bg"], fg=self.theme_colors["text"]).pack(side="left")

        btn_frame = ttk.Frame(bottom)
        btn_frame.pack(side="right")
        def add_to_cart():
            sel = tree.selection()
            if not sel:
                self._set_status("Select an item.", is_error=True)
                return
            idx = int(sel[0])
            item = items[idx]
            if not item.available:
                messagebox.showwarning("Unavailable", "This item is currently unavailable.", parent=win)
                return
            customer.add_to_cart(item, restaurant.name)
            self._set_status(f"Added '{item.name}' to cart.")
            total_var.set(f"Total items in cart: {len(customer.cart)}")
            cart_item_names = [i.name for i, r in customer.cart if r == restaurant.name]
            self._set_tree_alternating_colors(tree, highlight_in_cart=True, cart_items=cart_item_names)

        def remove_from_cart():
            sel = tree.selection()
            if not sel:
                return
            idx = int(sel[0])
            item = items[idx]
            for i, (ci, cr) in enumerate(customer.cart):
                if ci.name == item.name and cr == restaurant.name:
                    customer.remove_from_cart(i)
                    break
            total_var.set(f"Total items in cart: {len(customer.cart)}")
            cart_item_names = [i.name for i, r in customer.cart if r == restaurant.name]
            self._set_tree_alternating_colors(tree, highlight_in_cart=True, cart_items=cart_item_names)

        ttk.Button(btn_frame, text="Add to Cart", command=add_to_cart).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Remove from Cart", command=remove_from_cart).pack(side="left", padx=2)

    def _customer_view_cart(self):
        customer = self.platform.current_user
        if not customer.cart:
            messagebox.showinfo("Cart", "Your cart is empty.")
            return
        win = tk.Toplevel(self.root)
        self.open_windows.append(win)
        win.title("Your Cart")
        win.geometry("600x400")
        win.configure(bg=self.theme_colors["bg"])
        win.protocol("WM_DELETE_WINDOW", lambda: self._close_toplevel(win))
        frame = ttk.Frame(win, padding=15)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="🛒 Current Cart", font=self.FONT_SUBTITLE).pack(anchor="w", pady=(0, 10))
        cols = ("item", "price", "restaurant")
        tree_frame, tree = self._create_scrollable_tree(frame, cols, ["Item", "Price", "Restaurant"], height=8)
        tree_frame.pack(fill="both", expand=True)
        total = 0.0
        for item, rest_name in customer.cart:
            tree.insert("", "end", values=(item.name, f"${item.price:.2f}", rest_name))
            total += item.price
        self._set_tree_alternating_colors(tree)
        ttk.Label(frame, text=f"Total: ${total:.2f}", font=("Segoe UI", 12, "bold"),
                  style="Card.TLabel").pack(pady=10)
        btn_row = ttk.Frame(frame)
        btn_row.pack()
        ttk.Button(btn_row, text="Checkout", style="Accent.TButton",
                   command=lambda: self._checkout_multi(win)).pack(side="left", padx=5)
        ttk.Button(btn_row, text="Close", command=lambda: self._close_toplevel(win)).pack(side="left", padx=5)

    def _checkout_multi(self, cart_window):
        customer = self.platform.current_user
        if not customer.cart:
            return
        combined = self.platform.checkout_multi(customer)
        if combined:
            messagebox.showinfo("Order Placed",
                                f"Order #{combined.id} placed successfully.\nTotal: ${combined.total_price():.2f}",
                                parent=cart_window)
            self._close_toplevel(cart_window)
            self._set_status("Order placed.")
        else:
            messagebox.showerror("Error", "Could not place order.", parent=cart_window)

    def _customer_order_history(self):
        customer = self.platform.current_user
        win = tk.Toplevel(self.root)
        self.open_windows.append(win)
        win.title("Order History")
        win.geometry("800x450")
        win.configure(bg=self.theme_colors["bg"])
        win.protocol("WM_DELETE_WINDOW", lambda: self._close_toplevel(win))
        if not customer.order_history:
            self._show_empty_message(win, "No order history yet.").pack(expand=True)
            return
        cols = ("id", "items", "total", "datetime")
        tree_frame, tree = self._create_scrollable_tree(win, cols,
                                                         ["Order ID", "Items", "Total", "Date"], height=12)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=15)
        for co in customer.order_history:
            items_desc = ", ".join(f"{i.name} ({r})" for i, r in co.items_with_restaurant)
            tree.insert("", "end", values=(co.id, items_desc, f"${co.total_price():.2f}", co.datetime))
        self._set_tree_alternating_colors(tree)

    def _try_load_image(self, path):
        try:
            from PIL import Image, ImageTk
            img = Image.open(path)
            img = img.resize((40, 40), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def _close_toplevel(self, win):
        if win in self.open_windows:
            self.open_windows.remove(win)
        win.destroy()

    def _login(self, username, password):
        success, msg = self.platform.sign_in(username, password)
        if success:
            self._set_status("Login successful")
            self._show_main_menu()
        else:
            self._set_status(msg, is_error=True)

    def _logout(self, _=None):
        self.platform.logout()
        self.platform.save()
        self._set_status("Logged out.")
        self._show_frame(self._build_login_frame)

    def _show_main_menu(self):
        self._clear_container()
        frame = self._build_main_menu()
        frame.pack(fill="both", expand=True)

    def run(self):
        self._show_frame(self._build_login_frame)
        self.root.mainloop()

    def _on_close(self):
        try:
            self.platform.save()
        except Exception:
            pass
        self.root.destroy()