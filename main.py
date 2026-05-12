import tkinter
from functions import (handle_login, register_user, add_item_logic, draw_item_card, get_pricing_rate, update_pricing_rate, get_all_drinks, commit_new_drink, commit_delete_drink,)
from database import Session, Item, Pricing, User, Drinks, ConsoleOrder

bg_color = "#424549"
sec_color = "#7289da"

window = tkinter.Tk()
window.title("Playstation Cafe")
window.geometry("1200x760")
window.configure(bg=bg_color)


# --- PAGE 1: LOGIN PAGE ---
def show_login_page():
    # Create a container frame for this page
    login_frame = tkinter.Frame(window, bg=bg_color)
    login_frame.pack(expand=True)

    # Creating widgets inside login_frame
    login_label = tkinter.Label(
        login_frame, text="Login", bg=bg_color, fg=sec_color, font=("Arial", 30))
    username_label = tkinter.Label(
        login_frame, text="Username", bg=bg_color, fg="white", font=("Arial", 16))
    username_entry = tkinter.Entry(
        login_frame, font=("Arial", 16))
    password_label = tkinter.Label(
        login_frame, text="Password", bg=bg_color, fg="white", font=("Arial", 16))
    password_entry = tkinter.Entry(
        login_frame, show="*", font=("Arial", 16))

    login_button = tkinter.Button(
        login_frame, text="Login", bg=sec_color, fg="white", font=("Arial", 16),
        command=lambda: handle_login(username_entry, password_entry, login_frame, show_main_layout))

    register_button = tkinter.Button(
        login_frame, text="Register", bg="#7ECB94", fg="white", font=("Arial", 16),
        command=lambda: register_user(username_entry, password_entry))

    # Placing widgets
    login_label.grid(row=0, column=0, columnspan=2, sticky="news", pady=40)
    username_label.grid(row=1, column=0)
    username_entry.grid(row=1, column=1, pady=20)
    password_label.grid(row=2, column=0)
    password_entry.grid(row=2, column=1, pady=20)
    login_button.grid(row=3, column=0, columnspan=2, pady=(10, 5), sticky="we")
    register_button.grid(row=4, column=0, columnspan=2, pady=(5, 30), sticky="we")


def show_insights_page(content_area, user_id, username):
    # Clear the previous page entirely
    for widget in content_area.winfo_children():
        widget.destroy()

    # --- SCROLLABLE WRAPPER INFRASTRUCTURE ---
    container = tkinter.Frame(content_area, bg=bg_color)
    container.pack(fill="both", expand=True)

    canvas = tkinter.Canvas(container, bg=bg_color, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tkinter.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    scrollable_frame = tkinter.Frame(canvas, bg=bg_color)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame_id, width=e.width))
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    # --- BACK BUTTON ---
    top_frame = tkinter.Frame(scrollable_frame, bg="#2c2f33")
    top_frame.pack(fill="x", padx=20, pady=10)

    def go_back():
        canvas.unbind_all("<MouseWheel>")
        show_dashboard_grid(content_area, user_id, username)

    tkinter.Button(
        top_frame, text="← Back", bg="#2c2f33", fg="#7289da",
        font=("Arial", 10, "bold"), relief="flat", cursor="hand2", command=go_back
    ).pack(side="left")

    tkinter.Label(scrollable_frame, text="PRICING SETTINGS", bg=bg_color, fg="white",
                  font=("Arial", 18, "bold")).pack(pady=20)

    # --- CONSOLE PRICING GRID ---
    table_frame = tkinter.Frame(scrollable_frame, bg=bg_color)
    table_frame.pack(pady=10)

    tkinter.Label(table_frame, text="Category", width=20, bg=bg_color, fg="#b9bbbe").grid(row=0, column=0, padx=1,
                                                                                          pady=1)
    tkinter.Label(table_frame, text="Price per Hour ($)", width=20, bg=bg_color, fg="#b9bbbe").grid(row=0, column=1,
                                                                                                    padx=1, pady=1)
    tkinter.Label(table_frame, text="Action", width=15, bg=bg_color, fg="#b9bbbe").grid(row=0, column=2, padx=1,
                                                                                        pady=1)

    categories = [("PS 4", "Single"), ("PS 4", "Multi"), ("PS 5", "Single"), ("PS 5", "Multi")]

    for i, (console, mode) in enumerate(categories):
        cat_key = f"{console}_{mode}"
        current_val = get_pricing_rate(cat_key)  # <-- Logic Call

        tkinter.Label(table_frame, text=cat_key, bg=bg_color, fg="white").grid(row=i + 1, column=0, pady=5)

        price_entry = tkinter.Entry(table_frame, bg="#4f545c", fg="white", insertbackground="white", width=15)
        price_entry.insert(0, f"{current_val:.2f}")
        price_entry.grid(row=i + 1, column=1, pady=5)

        tkinter.Button(
            table_frame, text="SAVE", bg="#7289da", fg="white",
            command=lambda k=cat_key, e=price_entry: update_pricing_rate(k, e.get())  # <-- Logic Call
        ).grid(row=i + 1, column=2, padx=10)

    # --- DIVIDER ---
    tkinter.Frame(scrollable_frame, height=2, bg="#4f545c").pack(fill="x", padx=40, pady=25)

    # --- DRINK INVENTORY MANAGEMENT ---
    tkinter.Label(scrollable_frame, text="DRINK INVENTORY MANAGEMENT", bg=bg_color, fg="white",
                  font=("Arial", 16, "bold")).pack(pady=5)

    form_frame = tkinter.Frame(scrollable_frame, bg=bg_color)
    form_frame.pack(pady=10)

    tkinter.Label(form_frame, text="Drink Name:", bg=bg_color, fg="white", font=("Arial", 10)).grid(row=0, column=0,
                                                                                                    padx=5)
    name_entry = tkinter.Entry(form_frame, bg="#4f545c", fg="white", insertbackground="white", width=15)
    name_entry.grid(row=0, column=1, padx=5)

    tkinter.Label(form_frame, text="Price ($):", bg=bg_color, fg="white", font=("Arial", 10)).grid(row=0, column=2,
                                                                                                   padx=5)
    price_entry = tkinter.Entry(form_frame, bg="#4f545c", fg="white", insertbackground="white", width=8)
    price_entry.grid(row=0, column=3, padx=5)

    def handle_add_drink():
        if commit_new_drink(name_entry.get(), price_entry.get()):  # <-- Logic Call
            show_insights_page(content_area, user_id, username)

    tkinter.Button(
        form_frame, text="ADD DRINK", bg="#43b581", fg="white", font=("Arial", 9, "bold"), command=handle_add_drink
    ).grid(row=0, column=4, padx=10)

    # --- DRINK INVENTORY TABLE ---
    drink_table_frame = tkinter.Frame(scrollable_frame, bg=bg_color)
    drink_table_frame.pack(pady=10)

    tkinter.Label(drink_table_frame, text="Item Name", width=20, bg=bg_color, fg="#b9bbbe").grid(row=0, column=0,
                                                                                                 padx=1, pady=1)
    tkinter.Label(drink_table_frame, text="Price ($)", width=20, bg=bg_color, fg="#b9bbbe").grid(row=0, column=1,
                                                                                                 padx=1, pady=1)
    tkinter.Label(drink_table_frame, text="Action", width=15, bg=bg_color, fg="#b9bbbe").grid(row=0, column=2,
                                                                                              padx=1, pady=1)

    def handle_delete_drink(d_id):
        if commit_delete_drink(d_id):  # <-- Logic Call
            show_insights_page(content_area, user_id, username)

    all_drinks = get_all_drinks()  # <-- Logic Call
    for idx, drink in enumerate(all_drinks):
        tkinter.Label(drink_table_frame, text=drink.name, bg=bg_color, fg="white").grid(row=idx + 1, column=0,
                                                                                        pady=5)
        tkinter.Label(drink_table_frame, text=f"${drink.price:.2f}", bg=bg_color, fg="#43b581").grid(row=idx + 1,
                                                                                                     column=1,
                                                                                                     pady=5)

        tkinter.Button(
            drink_table_frame, text="DELETE", bg="#f04747", fg="white",
            command=lambda d_id=drink.id: handle_delete_drink(d_id)
        ).grid(row=idx + 1, column=2, padx=10)


# --- PAGE 2: MAIN PAGE ---
def show_main_layout(username, user_id):
    # This creates the main frame and Navbar
    main_container = tkinter.Frame(window, bg=bg_color)
    main_container.pack(expand=True, fill="both")

    navbar = tkinter.Frame(main_container, bg="#202225", height=50)
    navbar.pack(side="top", fill="x")

    # ... (Your Logout and Insights button code goes here) ...
    user_label = tkinter.Label(
        navbar, text=f"Logged in as: {username}", bg="#202225", fg=sec_color,
        font=("Arial", 10, "bold")
    )
    user_label.pack(side="left", padx=20, pady=10)

    logout_button = tkinter.Button(
        navbar, text="Logout", bg="#f04747", fg="white", font=("Arial", 10),
        command=lambda: [main_container.destroy(), show_login_page()],
        relief="flat", padx=10
    )
    logout_button.pack(side="right", padx=20, pady=10)

    # Assuming your User model has an 'is_admin' boolean
    if user_id == 1:
        insights_btn = tkinter.Button(
            navbar,
            text="Insights",
            bg="#202225",
            fg="white",
            relief="flat",
            command=lambda: show_insights_page(content_area, user_id, username)
        )
        insights_btn.pack(side="right", padx=10, pady=10)

    # This is the "Room" where content changes
    content_area = tkinter.Frame(main_container, bg=bg_color)
    content_area.pack(expand=True, fill="both", padx=20, pady=20)

    # IMMEDIATELY call the function to show the consoles
    show_dashboard_grid(content_area, user_id, username)

def show_dashboard_grid(content_area, user_id, username):
    # 1. Clear the area
    for widget in content_area.winfo_children():
        widget.destroy()

    grid_data = {"count": 0, "max_columns": 8}

    # 2. LOAD EXISTING ITEMS
    session = Session()
    existing_items = session.query(Item).all()
    session.close()

    # 3. DRAW CONSOLES (The Loop)
    for item in existing_items:
        # We pass None for the plus_button here because we handle it at the end
        draw_item_card(content_area, grid_data, None, item.label, item.id)

    # --- MOVE THIS SECTION OUTSIDE THE LOOP ---
    # 4. ONLY SHOW ADD BUTTON IF ADMIN (ID 1)
    if user_id == 1:
        plus_button = tkinter.Button(
            content_area, text="+", bg=sec_color, fg="white",
            font=("Arial", 18, "bold"), width=3, height=1, relief="flat"
        )
        # Update command to use the new structure
        plus_button.config(command=lambda: add_item_logic(content_area, grid_data, plus_button, user_id))

        # Position it at the very next available grid slot
        row = grid_data["count"] // grid_data["max_columns"]
        col = grid_data["count"] % grid_data["max_columns"]
        plus_button.grid(row=row, column=col, padx=10, pady=10)

# --- START THE APP ---
show_login_page()
window.mainloop()