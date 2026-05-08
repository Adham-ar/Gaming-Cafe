import tkinter
from functions import handle_login, register_user, add_item_logic, draw_item_card
from database import Session, Item, Pricing, User

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
    # Clear the previous page
    for widget in content_area.winfo_children():
        widget.destroy()

    # --- BACK BUTTON ---
    # We pack this into its own frame to keep it aligned to the left
    top_frame = tkinter.Frame(content_area, bg="#2c2f33")
    top_frame.pack(fill="x", padx=20, pady=10)

    back_btn = tkinter.Button(
        top_frame,
        text="← Back",
        bg="#2c2f33",
        fg="#7289da",  # Discord-style blue for the link look
        font=("Arial", 10, "bold"),
        relief="flat",
        cursor="hand2",
        # This calls your main dashboard function
        command=lambda: show_dashboard_grid(content_area, user_id, username)
    )
    back_btn.pack(side="left")

    tkinter.Label(content_area, text="PRICING SETTINGS", bg=bg_color, fg="white", font=("Arial", 18, "bold")).pack(
        pady=20)

    # Container for the table
    table_frame = tkinter.Frame(content_area, bg=bg_color)
    table_frame.pack(pady=10)

    # Header Row
    tkinter.Label(table_frame, text="Category", width=20, bg=bg_color, fg="#b9bbbe").grid(row=0, column=0, padx=1,
                                                                                           pady=1)
    tkinter.Label(table_frame, text="Price per Hour ($)", width=20, bg=bg_color, fg="#b9bbbe").grid(row=0, column=1,
                                                                                                     padx=1, pady=1)
    tkinter.Label(table_frame, text="Action", width=15, bg=bg_color, fg="#b9bbbe").grid(row=0, column=2, padx=1,
                                                                                         pady=1)

    categories = [("PS 4", "Single"), ("PS 4", "Multi"), ("PS 5", "Single"), ("PS 5", "Multi")]

    for i, (console, mode) in enumerate(categories):
        cat_key = f"{console}_{mode}"

        # Get current price from DB
        session = Session()
        record = session.query(Pricing).filter_by(category=cat_key).first()
        current_val = record.price_per_hour if record else 10.0
        session.close()

        # UI Row
        tkinter.Label(table_frame, text=cat_key, bg=bg_color, fg="white").grid(row=i + 1, column=0, pady=5)

        price_entry = tkinter.Entry(table_frame, bg="#4f545c", fg="white", insertbackground="white", width=15)
        price_entry.insert(0, f"{current_val:.2f}")
        price_entry.grid(row=i + 1, column=1, pady=5)

        # Save function for this specific row
        def save_price(k=cat_key, e=price_entry):
            try:
                new_price = float(e.get())
                session = Session()
                item = session.query(Pricing).filter_by(category=k).first()
                if item:
                    item.price_per_hour = new_price
                else:
                    session.add(Pricing(category=k, price_per_hour=new_price))
                session.commit()
                session.close()
                tkinter.messagebox.showinfo("Success", f"Price for {k} updated!")
            except ValueError:
                tkinter.messagebox.showerror("Error", "Please enter a valid number.")

        tkinter.Button(table_frame, text="SAVE", bg="#7289da", fg="white", command=save_price).grid(row=i + 1, column=2,
                                                                                                    padx=10)


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