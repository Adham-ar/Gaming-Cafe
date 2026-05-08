from database import Session, User, Item, Pricing
from tkinter import messagebox
import tkinter
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


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
    else:
        details_window.title("Unknown Console")

    session.close()  # Close the temporary session used for the title
    details_window.geometry("800x500")
    details_window.configure(bg="#2c2f33")

    # Use a dictionary to keep the flag mutable across functions
    state = {"window_active": True}

    # --- DATA VARIABLES ---
    choice_console = tkinter.StringVar(value="PS 4")
    choice_mode = tkinter.StringVar(value="Single")

    # --- UI: TIMER LABEL ---
    timer_label = tkinter.Label(
        details_window, text="00:00:00",
        bg="#2c2f33", fg="#7ECB94", font=("Arial", 30, "bold")
    )
    timer_label.pack(pady=30)

    bill_label = tkinter.Label(
        details_window, text="Total Bill: 0.00",
        bg="#2c2f33", fg="#43b581", font=("Arial", 14, "bold")
    )
    bill_label.pack(pady=10)

    # NEW: The Final Bill Label (The "Receipt")
    final_bill_label = tkinter.Label(details_window, text="", bg="#2c2f33", fg="#f1c40f", font=("Arial", 16, "bold"))
    final_bill_label.pack(pady=10)

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
    console_frame.pack(pady=10)

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
        pady=(15, 0))
    mode_frame = tkinter.Frame(details_window, bg="#2c2f33")
    mode_frame.pack(pady=10)

    mode_btns = {}
    for text in ["Single", "Multi"]:
        btn = tkinter.Button(mode_frame, text=text.upper(), width=12, relief="flat", font=("Arial", 10, "bold"))
        btn.config(command=lambda t=text, b=btn: set_selection(choice_mode, t, mode_btns))
        btn.pack(side="left", padx=5)
        mode_btns[text] = btn
        selection_buttons.append(btn)

    # Initialize first selection
    set_selection(choice_console, "PS 4", console_btns)
    set_selection(choice_mode, "Single", mode_btns)

    # --- SECTION 3: TIMER LOGIC ---
    def refresh_ui():
        if not state.get("window_active", False):
            return

        session = Session()
        item = session.query(Item).get(item_id)

        if item and item.is_running:
            if item.is_paused:
                # Freeze UI colors to show it's stopped
                timer_label.config(fg="#f1c40f")
                bill_label.config(fg="#f1c40f")
            else:
                # Run the clock normally
                elapsed = datetime.now() - item.start_time
                seconds = int(elapsed.total_seconds())

                h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
                timer_label.config(text=f"{h:02}:{m:02}:{s:02}", fg="#7ECB94")

                current_price = calculate_bill(seconds, choice_console.get(), choice_mode.get())
                bill_label.config(text=f"Current Bill: ${current_price:.2f}", fg="#43b581")

        session.close()
        timer_label.after(1000, refresh_ui)

    def start_timer():
        session = Session()
        item = session.query(Item).get(item_id)
        if item:
            item.start_time = datetime.now()
            item.is_running = True
            item.is_paused = False
            session.commit()

            # LOCK UI: Can't change console/mode once started
            for btn in selection_buttons:
                btn.config(state="disabled")

            # Clear final bill from previous session
            final_bill_label.config(text="")
        session.close()

    def toggle_pause():
        session = Session()
        item = session.query(Item).get(item_id)

        if item and item.is_running:
            if not item.is_paused:
                # --- ACTION: PAUSE ---
                item.is_paused = True
                item.pause_start = datetime.now()  # Mark the moment pause began
                pause_btn.config(text="RESUME", bg="#7289da")
            else:
                # --- ACTION: RESUME ---
                # Calculate how long they were paused
                pause_duration = datetime.now() - item.pause_start

                # SHIFT the start_time forward by that duration
                # This "forgives" the paused time so it doesn't count
                item.start_time = item.start_time + pause_duration

                item.is_paused = False
                item.pause_start = None  # Clear the pause timestamp
                pause_btn.config(text="PAUSE", bg="#faa61a")

            session.commit()
        session.close()

    def calculate_bill(duration_seconds, console_type, mode):
        session = Session()
        # Construct the key based on selections (e.g., "PS 5_Multi")
        key = f"{console_type}_{mode}"

        pricing_rule = session.query(Pricing).filter_by(category=key).first()
        rate = pricing_rule.price_per_hour if pricing_rule else 10.0  # Default if not set

        # Calculate: (rate / 3600 seconds) * actual seconds played
        total_price = (rate / 3600) * duration_seconds
        session.close()

        return round(total_price, 2)

    def stop_timer():
        if messagebox.askyesno("Confirm", "Stop session and calculate total?"):
            session = Session()
            item = session.query(Item).get(item_id)

            if item and item.is_running:
                # Calculate final time
                elapsed = datetime.now() - item.start_time
                total_seconds = int(elapsed.total_seconds())
                # Get selections from our toggle variables
                final_price = calculate_bill(total_seconds, choice_console.get(), choice_mode.get())

                # Update the label on the details window
                final_bill_label.config(text=f"FINAL RECEIPT: ${final_price:.2f}")

                item.is_running = False
                session.commit()

                # UNLOCK UI: Ready for next customer
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

    # Pause Button (We save this to a variable so toggle_pause can change its text)
    pause_btn = tkinter.Button(ctrl_frame, text="PAUSE", bg="#faa61a", fg="white", width=12, height=2,
                               font=("Arial", 11, "bold"), relief="flat", command=toggle_pause)
    pause_btn.pack(side="left", padx=10)

    tkinter.Button(ctrl_frame, text="STOP", bg="#f04747", fg="white", width=15, height=2,
                   font=("Arial", 11, "bold"), relief="flat", command=stop_timer).pack(side="left", padx=10)

    # --- CLEANUP ---
    def on_close():
        state["window_active"] = False
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


