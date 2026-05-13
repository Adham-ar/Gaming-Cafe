from database import Session, User, Item, Pricing, Drinks, ConsoleOrder
from tkinter import messagebox
import tkinter
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from tkinter import ttk


bg_color = "#424549"
sec_color = "#7289da"
image_refs = []


def register_user(username_entry, password_entry):
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning("Empty Fields", "Please fill in all fields")
        return

    # Create the salt + hash using pbkdf2:sha256
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

    session = Session()
    try:
        new_user = User(username=username, password=hashed_password)
        session.add(new_user)
        session.commit()
        messagebox.showinfo("Success", "Account created successfully!")
    except Exception as e:
        session.rollback()
        messagebox.showerror("Error", "Username already exists")
    finally:
        session.close()


def handle_login(username_entry, password_entry, login_frame, show_main_page_callback):
    username = username_entry.get()
    password = password_entry.get()

    session = Session()
    # FIX: Only filter by username. Do NOT include password in the query.
    user = session.query(User).filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        user_id = user.id  # Get the ID
        session.close()
        login_frame.destroy()
        show_main_page_callback(username, user_id)  # Pass ID to main page
    else:
        session.close()
        messagebox.showerror("Error", "Invalid username or password")


def item_clicked(item_id):
    print(f"You clicked on item number: {item_id + 1}")


def add_item_logic(content_area, grid_data, plus_button, user_id):
    session = Session()
    new_db_item = Item(label=f"Ps {grid_data['count'] + 1}", user_id=user_id)
    session.add(new_db_item)
    session.commit()

    # Capture the ID after the commit
    new_id = new_db_item.id
    label_text = new_db_item.label
    session.close()

    # Pass the new_id to the draw function
    draw_item_card(content_area, grid_data, plus_button, label_text, new_id)


def open_details_window(item_id, main_img_label):
    # Create the new window
    details_window = tkinter.Toplevel()

    # --- FETCH ITEM DATA FOR TITLE ---
    session = Session()
    item = session.query(Item).get(item_id)

    # Set the title dynamically based on the item label
    if item:
        details_window.title(f"Managing: {item.label}")
        saved_console = item.console_type if item.console_type else "PS 4"
        saved_mode = item.player_mode if item.player_mode else "Single"
    else:
        details_window.title("Unknown Console")
        saved_console = "PS 4"
        saved_mode = "Single"

    session.close()  # Close the temporary session used for the title

    # Increased height slightly (from 500 to 680) to give room for the drinks UI elements comfortably
    details_window.geometry("800x680")
    details_window.configure(bg="#2c2f33")

    # Use a dictionary to keep the flag mutable across functions
    state = {"window_active": True}

    # --- DATA VARIABLES ---
    choice_console = tkinter.StringVar(value=saved_console)
    choice_mode = tkinter.StringVar(value=saved_mode)

    # --- UI: TIMER LABEL ---
    timer_label = tkinter.Label(
        details_window, text="00:00:00",
        bg="#2c2f33", fg="#7ECB94", font=("Arial", 30, "bold")
    )
    timer_label.pack(pady=20)

    bill_label = tkinter.Label(
        details_window, text="Total Bill: 0.00",
        bg="#2c2f33", fg="#43b581", font=("Arial", 14, "bold")
    )
    bill_label.pack(pady=5)

    # The Final Bill Label (The "Receipt")
    final_bill_label = tkinter.Label(details_window, text="", bg="#2c2f33", fg="#f1c40f", font=("Arial", 16, "bold"))
    final_bill_label.pack(pady=5)

    selection_buttons = []

    # --- HELPER: TOGGLE LOGIC ---
    def set_selection(variable, value, buttons_dict):
        variable.set(value)
        for val, btn in buttons_dict.items():
            if val == value:
                btn.config(bg="#7289da", fg="white")  # Selected Blue
            else:
                btn.config(bg="#4f545c", fg="#b9bbbe")  # Inactive Gray

    # --- SECTION 1: CONSOLE SELECTION ---
    tkinter.Label(details_window, text="SELECT CONSOLE", bg="#2c2f33", fg="#b9bbbe", font=("Arial", 9, "bold")).pack()
    console_frame = tkinter.Frame(details_window, bg="#2c2f33")
    console_frame.pack(pady=5)

    console_btns = {}
    for text in ["PS 4", "PS 5"]:
        btn = tkinter.Button(console_frame, text=text, width=12, relief="flat", font=("Arial", 10, "bold"))
        btn.config(command=lambda t=text, b=btn: set_selection(choice_console, t, console_btns))
        btn.pack(side="left", padx=5)
        console_btns[text] = btn
        selection_buttons.append(btn)

    # Initialize first selection
    set_selection(choice_console, "PS 4", console_btns)

    # --- SECTION 2: MODE SELECTION ---
    tkinter.Label(details_window, text="PLAYER MODE", bg="#2c2f33", fg="#b9bbbe", font=("Arial", 9, "bold")).pack(
        pady=(10, 0))
    mode_frame = tkinter.Frame(details_window, bg="#2c2f33")
    mode_frame.pack(pady=5)

    mode_btns = {}
    for text in ["Single", "Multi"]:
        btn = tkinter.Button(mode_frame, text=text.upper(), width=12, relief="flat", font=("Arial", 10, "bold"))
        btn.config(command=lambda t=text, b=btn: set_selection(choice_mode, t, mode_btns))
        btn.pack(side="left", padx=5)
        mode_btns[text] = btn
        selection_buttons.append(btn)

    # Initialize selections based on DB values
    set_selection(choice_console, saved_console, console_btns)
    set_selection(choice_mode, saved_mode, mode_btns)

    # --- SECTION 2.5: DRINK ORDERS INTERFACE ---
    tkinter.Label(details_window, text="ADD DRINKS TO TAB", bg="#2c2f33", fg="#b9bbbe", font=("Arial", 9, "bold")).pack(
        pady=(15, 0))

    drink_order_frame = tkinter.Frame(details_window, bg="#2c2f33")
    drink_order_frame.pack(pady=5)

    # Fetch available inventory from database
    db_session = Session()
    drink_menu_items = db_session.query(Drinks).all()
    db_session.close()

    drink_names = [f"{d.name} (${d.price:.2f})" for d in drink_menu_items]

    drink_dropdown = ttk.Combobox(drink_order_frame, values=drink_names, state="readonly", width=25)
    drink_dropdown.pack(side="left", padx=5)

    # Force the dropdown to start completely empty
    drink_dropdown.set("")

    tkinter.Label(drink_order_frame, text="Qty:", bg="#2c2f33", fg="white").pack(side="left", padx=2)
    qty_dropdown = ttk.Combobox(drink_order_frame, values=[1, 2, 3, 4, 5], state="readonly", width=3)
    qty_dropdown.pack(side="left", padx=5)
    qty_dropdown.current(0)

    # Visual field summarizing orders currently placed on this session
    active_orders_label = tkinter.Label(details_window, text="No drinks ordered yet.", bg="#2c2f33", fg="#b9bbbe",
                                        font=("Arial", 10, "italic"))
    active_orders_label.pack(pady=5)

    def refresh_drink_list():
        """Queries the database to update the string display of orders."""
        session = Session()
        orders = session.query(ConsoleOrder).filter_by(item_id=item_id).all()
        if not orders:
            active_orders_label.config(text="No drinks ordered yet.", fg="#b9bbbe", font=("Arial", 10, "italic"))
            session.close()
            return
        summary_text = "Active Orders: " + " | ".join([f"{o.quantity}x {o.drink.name}" for o in orders])
        active_orders_label.config(text=summary_text, fg="white", font=("Arial", 10, "bold"))
        session.close()

    def handle_add_drink_to_tab():
        selected_index = drink_dropdown.current()
        # Safeguard: prevent index lookups if no drink is chosen
        if selected_index == -1 or drink_dropdown.get() == "":
            return

        drink_obj = drink_menu_items[selected_index]
        quantity = int(qty_dropdown.get())

        session = Session()
        # Check if this exact drink has already been ordered on this session tab
        existing_order = session.query(ConsoleOrder).filter_by(item_id=item_id, drink_id=drink_obj.id).first()

        if existing_order:
            existing_order.quantity += quantity
        else:
            new_order = ConsoleOrder(item_id=item_id, drink_id=drink_obj.id, quantity=quantity)
            session.add(new_order)

        session.commit()
        session.close()

        # Reset dropdown box to empty after saving, then refresh visual list
        drink_dropdown.set("")
        refresh_drink_list()

    tkinter.Button(
        drink_order_frame, text="+ Add", bg="#7289da", fg="white",
        font=("Arial", 9, "bold"), relief="flat", command=handle_add_drink_to_tab
    ).pack(side="left", padx=5)

    # Load order list immediately on window popup load
    refresh_drink_list()

    # --- SECTION 3: TIMER LOGIC ---
    def refresh_ui():
        if not state.get("window_active", False):
            return

        session = Session()
        item = session.query(Item).get(item_id)

        if item and item.is_running and item.start_time:
            elapsed = datetime.now() - item.start_time
            seconds = int(elapsed.total_seconds())

            h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
            timer_label.config(text=f"{h:02}:{m:02}:{s:02}", fg="#7ECB94")

            current_price = calculate_bill(seconds, choice_console.get(), choice_mode.get())
            bill_label.config(text=f"Current Bill: ${current_price:.2f}", fg="#43b581")

            main_img_label.config(image=main_img_label.active_photo)

        session.close()
        timer_label.after(1000, refresh_ui)

    def start_timer():
        session = Session()
        item = session.query(Item).get(item_id)
        if item:
            item.start_time = datetime.now()
            item.is_running = True
            # SAVE CURRENT CHOICES TO THE DB
            item.console_type = choice_console.get()
            item.player_mode = choice_mode.get()

            session.commit()

            # LOCK UI: Can't change console/mode once started
            for btn in selection_buttons:
                btn.config(state="disabled")

            # Clear final bill from previous session
            final_bill_label.config(text="")
        session.close()

    def calculate_bill(duration_seconds, console_type, mode):
        session = Session()
        # Construct the key based on selections (e.g., "PS 5_Multi")
        key = f"{console_type}_{mode}"

        pricing_rule = session.query(Pricing).filter_by(category=key).first()
        rate = pricing_rule.price_per_hour if pricing_rule else 0.0

        # Calculate time cost: (rate / 3600 seconds) * actual seconds played
        time_cost = (rate / 3600) * duration_seconds

        # Calculate active drink tabs cost
        drink_orders = session.query(ConsoleOrder).filter_by(item_id=item_id).all()
        drinks_cost = sum([order.quantity * order.drink.price for order in drink_orders])

        session.close()
        return round(time_cost + drinks_cost, 2)

    def stop_timer():
        session = Session()
        item = session.query(Item).get(item_id)

        if item and item.is_running:
            # --- THE POPUP CONFIRMATION ---
            # It will return True if "Yes" is clicked, and False if "No" is clicked
            confirm = messagebox.askyesno(
                title="Confirm Stop",
                message=f"Are you sure you want to stop the timer for {item.label}?"
            )

            # If the user clicks "No", close the session and exit the function safely
            if not confirm:
                session.close()
                return

                # --- REST OF YOUR WORKING STOP LOGIC ---
            # Calculate total up to this exact millisecond
            elapsed = datetime.now() - item.start_time
            total_seconds = int(elapsed.total_seconds())
            final_price = calculate_bill(total_seconds, item.console_type, item.player_mode)

            # Put it on the text options
            timer_label.config(fg="#f04747")  # Turn red to visually show it's frozen
            final_bill_label.config(text=f"FINAL RECEIPT: ${final_price:.2f}")

            # Commit stop status to DB so background checkers know it's off
            item.is_running = False
            session.commit()

            # UNLOCK UI selection fields for the next round
            for btn in selection_buttons:
                btn.config(state="normal")

        session.close()

    # --- AUTO-LOCK IF ALREADY RUNNING ---
    session = Session()
    item = session.query(Item).get(item_id)
    if item and item.is_running:
        for btn in selection_buttons:
            btn.config(state="disabled")
    session.close()

    # --- SECTION 4: CONTROL BUTTONS ---
    ctrl_frame = tkinter.Frame(details_window, bg="#2c2f33")
    ctrl_frame.pack(pady=40)

    tkinter.Button(ctrl_frame, text="START", bg="#43b581", fg="white", width=15, height=2,
                   font=("Arial", 11, "bold"), relief="flat", command=start_timer).pack(side="left", padx=10)

    tkinter.Button(ctrl_frame, text="STOP", bg="#f04747", fg="white", width=15, height=2,
                   font=("Arial", 11, "bold"), relief="flat", command=stop_timer).pack(side="left", padx=10)

    # --- CLEANUP ---
    def on_close():
        state["window_active"] = False

        session = Session()
        item = session.query(Item).get(item_id)

        # Only clear the drink tab if the timer is NOT running
        if item and not item.is_running:
            try:
                session.query(ConsoleOrder).filter_by(item_id=item_id).delete()
                session.commit()
            except Exception as e:
                print(f"Error clearing drink tab: {e}")
                session.rollback()

        session.close()
        details_window.destroy()

    details_window.protocol("WM_DELETE_WINDOW", on_close)
    refresh_ui()

def draw_item_card(content_area, grid_data, plus_button, text, item_id):
    # This is your existing UI drawing code moved to a helper
    row = grid_data["count"] // grid_data["max_columns"]
    col = grid_data["count"] % grid_data["max_columns"]

    # 1. Create a Container Frame for the "Card"
    card = tkinter.Frame(content_area, bg=bg_color, cursor="hand2")
    card.grid(row=row, column=col, padx=15, pady=15)

    # 2. Load and display the Image with Option 2 logic
    img_label = tkinter.Label(card, bg=bg_color)
    img_label.pack()

    try:
        # Load both states
        normal_photo = tkinter.PhotoImage(file="images/controller.png")
        active_photo = tkinter.PhotoImage(file="images/controller_filld.png")

        # Attach to widget to prevent Garbage Collection
        img_label.normal_photo = normal_photo
        img_label.active_photo = active_photo

        # Set initial image
        img_label.config(image=normal_photo)
    except Exception as e:
        print(f"Error loading images for card {item_id}: {e}")

    # 3. Add the Label text
    name_label = tkinter.Label(card, text=text, bg=bg_color, fg="white", font=("Arial", 10))
    name_label.pack(pady=5)

    # 4. Status Checker Loop (The "Auto-Update" logic)
    def update_status():
        # Using a new session for every check to get fresh data
        session = Session()
        item = session.query(Item).get(item_id)

        if item:
            if item.is_running:
                img_label.config(image=img_label.active_photo)
            else:
                img_label.config(image=img_label.normal_photo)
                card.config(highlightthickness=0)

        session.close()
        # Check the database again in 2 seconds
        # We use content_area or card because they exist for the life of the app
        card.after(2000, update_status)

    # Start the loop
    update_status()

    # 5. Make the whole card clickable
    def on_click(event):
        open_details_window(item_id, img_label)

    for widget in (card, img_label, name_label):
        widget.bind("<Button-1>", on_click)

    # 6. Update Grid Position
    grid_data["count"] += 1
    if plus_button:
        new_row = grid_data["count"] // grid_data["max_columns"]
        new_col = grid_data["count"] % grid_data["max_columns"]
        plus_button.grid(row=new_row, column=new_col)

def get_pricing_rate(cat_key):
    """Fetches the hourly rate for a specific console category."""
    session = Session()
    record = session.query(Pricing).filter_by(category=cat_key).first()
    current_val = record.price_per_hour if record else 0.0
    session.close()
    return current_val

def update_pricing_rate(cat_key, price_str):
    """Validates and updates the hourly rate for a console category."""
    try:
        new_price = float(price_str)
        session = Session()
        item = session.query(Pricing).filter_by(category=cat_key).first()
        if item:
            item.price_per_hour = new_price
        else:
            session.add(Pricing(category=cat_key, price_per_hour=new_price))
        session.commit()
        session.close()
        tkinter.messagebox.showinfo("Success", f"Price for {cat_key} updated!")
        return True
    except ValueError:
        tkinter.messagebox.showerror("Error", "Please enter a valid number.")
        return False

def get_all_drinks():
    """Fetches all items from the drink inventory."""
    session = Session()
    all_drinks = session.query(Drinks).all()
    session.close()
    return all_drinks

def commit_new_drink(name, price_str):
    """Validates and commits a new drink item to the inventory."""
    if not name or not price_str:
        tkinter.messagebox.showerror("Error", "Please fill out both fields.")
        return False

    try:
        clean_price_str = price_str.replace('$', '').strip()
        price = float(clean_price_str)
    except ValueError:
        tkinter.messagebox.showerror("Error", "Price must be a valid number (e.g., 2.50).")
        return False

    session = Session()
    existing = session.query(Drinks).filter_by(name=name).first()
    if existing:
        tkinter.messagebox.showerror("Error", f"'{name}' already exists in inventory.")
        session.close()
        return False

    new_drink = Drinks(name=name, price=round(price, 2))
    session.add(new_drink)
    session.commit()
    session.close()
    return True

def commit_delete_drink(drink_id):
    """Deletes a selected drink item from the inventory."""
    if tkinter.messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):
        session = Session()
        drink = session.query(Drinks).get(drink_id)
        if drink:
            session.delete(drink)
            session.commit()
        session.close()
        return True
    return False
