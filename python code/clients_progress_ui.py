import sys
import webbrowser
from pathlib import Path
from urllib.parse import quote
import tkinter as tk
from tkinter import ttk, messagebox

from clients_management import Client, ClientManager


def safe_main():
    try:
        app = ProgressApp()
        app.mainloop()
    except tk.TclError as exc:
        message = (
            "Tkinter could not start in this environment.\n\n"
            "Please run this script in a normal Windows terminal or VS Code terminal, "
            "not in a headless/debug console.\n\n"
            f"Details: {exc}"
        )
        print(message, file=sys.stderr)
        raise SystemExit(1)


class Plan:
    Clients_progress = {}

    def __init__(self, client: Client, all_tasks=None):
        self.client = client
        self.client_name = client.name
        self.all_tasks = list(all_tasks) if all_tasks else []
        self.pending_tasks = list(self.all_tasks)
        self.progress = 0
        self.refresh_progress()

    def refresh_progress(self):
        if not self.all_tasks:
            self.progress = 100
            return self.progress

        remaining = len(self.pending_tasks)
        completed = len(self.all_tasks) - remaining
        self.progress = round((completed / len(self.all_tasks)) * 100)
        return self.progress

    def sync_task_lists(self, all_tasks=None, pending_tasks=None):
        if all_tasks is not None:
            self.all_tasks = list(all_tasks)

        if pending_tasks is not None:
            self.pending_tasks = list(pending_tasks)
        elif not self.pending_tasks:
            self.pending_tasks = list(self.all_tasks)

        self.pending_tasks = [task for task in self.pending_tasks if task in self.all_tasks]
        self.pending_tasks = list(dict.fromkeys(self.pending_tasks))
        self.all_tasks = list(dict.fromkeys(self.all_tasks))
        self.refresh_progress()
        self.update_clients_progress()

    def add_pending_task(self, task):
        if not task:
            return
        if task not in self.all_tasks:
            self.all_tasks.append(task)
        if task not in self.pending_tasks:
            self.pending_tasks.append(task)
        self.refresh_progress()
        self.update_clients_progress()

    def complete_task(self, task):
        if task in self.pending_tasks:
            self.pending_tasks.remove(task)
        self.refresh_progress()
        self.update_clients_progress()

    def update_clients_progress(self):
        self.refresh_progress()
        Plan.Clients_progress[self.client.name] = {
            "client_name": self.client.name,
            "progress": self.progress,
            "pending_tasks": list(self.pending_tasks),
            "all_tasks": list(self.all_tasks),
        }

    def to_dict(self):
        return {
            "client_name": self.client_name,
            "progress": self.progress,
            "pending_tasks": list(self.pending_tasks),
            "all_tasks": list(self.all_tasks),
        }


class TaskDetailsWindow(tk.Toplevel):
    def __init__(self, master=None, client_name="Client", plan=None, all_tasks=None, pending_tasks=None):
        super().__init__(master)
        self.title(f"Task Details - {client_name}")
        self.geometry("560x430")
        self.minsize(460, 320)

        self.plan = plan
        self.master_app = master

        main = ttk.Frame(self, padding=14)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text=f"Client: {client_name}", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 10))

        task_columns = ttk.Frame(main)
        task_columns.pack(fill="both", expand=True)
        task_columns.columnconfigure(0, weight=1)
        task_columns.columnconfigure(1, weight=1)

        ttk.Label(task_columns, text="All Tasks", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 6))
        ttk.Label(task_columns, text="Pending Tasks", font=("Segoe UI", 9, "bold")).grid(row=0, column=1, sticky="w", pady=(0, 6))

        all_scroll = ttk.Scrollbar(task_columns, orient="vertical")
        pending_scroll = ttk.Scrollbar(task_columns, orient="vertical")

        self.all_box = tk.Listbox(task_columns, height=14, exportselection=False, font=("Segoe UI", 9), yscrollcommand=all_scroll.set)
        self.pending_box = tk.Listbox(task_columns, height=14, exportselection=False, bg="#fffef5", font=("Segoe UI", 9), yscrollcommand=pending_scroll.set)

        self.all_box.grid(row=1, column=0, sticky="nsew", padx=(0, 6), pady=(0, 10))
        all_scroll.grid(row=1, column=0, sticky="ns", padx=(0, 0), pady=(0, 10))
        self.pending_box.grid(row=1, column=1, sticky="nsew", padx=(6, 0), pady=(0, 10))
        pending_scroll.grid(row=1, column=1, sticky="ns", padx=(0, 0), pady=(0, 10))

        all_scroll.config(command=self.all_box.yview)
        pending_scroll.config(command=self.pending_box.yview)

        self.populate_lists(all_tasks=all_tasks, pending_tasks=pending_tasks)

        button_row = ttk.Frame(main)
        button_row.pack(fill="x", pady=(0, 8))
        ttk.Button(button_row, text="Mark Done", command=self.mark_selected_done).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Close", command=self.close_window).pack(side="left")

    def populate_lists(self, all_tasks=None, pending_tasks=None):
        self.all_box.delete(0, tk.END)
        self.pending_box.delete(0, tk.END)

        tasks = list(all_tasks) if all_tasks is not None else []
        pending = list(pending_tasks) if pending_tasks is not None else []

        if tasks:
            for task in tasks:
                self.all_box.insert(tk.END, task)
        else:
            self.all_box.insert(tk.END, "No tasks yet")

        if pending:
            for task in pending:
                self.pending_box.insert(tk.END, task)
        else:
            self.pending_box.insert(tk.END, "No pending tasks")

    def close_window(self):
        self.destroy()
        if self.master_app is not None:
            try:
                self.master_app.deiconify()
            except Exception:
                pass

    def mark_selected_done(self):
        if self.plan is None:
            messagebox.showwarning("No task plan", "There is no active task plan to update.")
            return

        selected = self.pending_box.curselection()
        if not selected:
            messagebox.showwarning("No task selected", "Select a task from the pending list first.")
            return

        task = self.pending_box.get(selected[0])
        self.plan.complete_task(task)

        if self.master_app and hasattr(self.master_app, "refresh_display"):
            self.master_app.refresh_display()

        self.populate_lists(all_tasks=self.plan.all_tasks, pending_tasks=self.plan.pending_tasks)


class AllClientsProgressWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("All Clients Progress")
        self.geometry("720x440")
        self.minsize(620, 360)

        self.manager = ClientManager("clients.json")
        self.tree = ttk.Treeview(
            self,
            columns=("client", "business", "progress", "tasks"),
            show="headings",
        )
        self.tree.heading("client", text="Client")
        self.tree.heading("business", text="Business")
        self.tree.heading("progress", text="Progress")
        self.tree.heading("tasks", text="Pending / Total")
        self.tree.column("client", width=190, anchor="w")
        self.tree.column("business", width=220, anchor="w")
        self.tree.column("progress", width=110, anchor="center")
        self.tree.column("tasks", width=150, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=12, pady=(12, 8))

        self.tree.bind("<Double-1>", self.edit_selected_client)

        button_row = ttk.Frame(self)
        button_row.pack(pady=(0, 12))
        ttk.Button(button_row, text="Edit Selected Client", command=self.edit_selected_client).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Refresh", command=self.refresh_view).pack(side="left")
        self.refresh_view()

    def edit_selected_client(self, event=None):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No client selected", "Select a client row first.")
            return

        values = self.tree.item(selection[0], "values")
        if not values:
            return

        client_name = values[0]
        business = values[1] if len(values) > 1 else "N/A"

        if self.master and hasattr(self.master, "load_client_progress"):
            self.master.load_client_progress(client_name, business)

        self.destroy()

    def refresh_view(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.manager.load_clients()
        all_progress = Plan.Clients_progress or {}

        seen = set()
        for client in self.manager.clients:
            seen.add(client.name)
            progress_info = all_progress.get(client.name, {})
            progress = progress_info.get("progress", 0)
            pending_tasks = progress_info.get("pending_tasks", [])
            all_tasks = progress_info.get("all_tasks", [])
            self.tree.insert(
                "",
                "end",
                values=(
                    client.name,
                    client.business,
                    f"{progress}%",
                    f"{len(pending_tasks)} / {len(all_tasks)}",
                ),
            )

        for client_name, progress_info in all_progress.items():
            if client_name in seen:
                continue
            pending_tasks = progress_info.get("pending_tasks", [])
            all_tasks = progress_info.get("all_tasks", [])
            self.tree.insert(
                "",
                "end",
                values=(
                    client_name,
                    "Saved progress only",
                    f"{progress_info.get('progress', 0)}%",
                    f"{len(pending_tasks)} / {len(all_tasks)}",
                ),
            )


class ProgressApp(tk.Tk):
    @staticmethod
    def resolve_client_file():
        candidates = [
            Path(__file__).resolve().parent.parent / "clients.json",
            Path(__file__).resolve().parent / "clients.json",
            Path.cwd() / "clients.json",
            Path(sys.executable).resolve().parent / "clients.json",
        ]

        if getattr(sys, "_MEIPASS", None):
            candidates.insert(0, Path(sys._MEIPASS) / "clients.json")

        for candidate in candidates:
            if candidate.exists():
                return candidate

        fallback = Path(sys.executable).resolve().parent / "clients.json"
        return fallback

    def __init__(self):
        super().__init__()
        self.title("Client Progress Tracker")
        self.geometry("850x600")
        self.minsize(760, 500)

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.client_file = self.resolve_client_file()
        self.client_manager = ClientManager(self.client_file)

        self.client_name_var = tk.StringVar(value="")
        self.contact_var = tk.StringVar(value="")
        self.business_var = tk.StringVar(value="")
        self.email_var = tk.StringVar(value="")
        self.total_tasks_var = tk.StringVar(value="0")
        self.new_task_var = tk.StringVar()

        self.plan = None
        self.client_combo = None

        self.build_ui()

    def build_ui(self):
        self.style.configure("Section.TLabelframe", padding=(12, 10), relief="groove")
        self.style.configure("Section.TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        self.style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        self.style.configure("Action.TButton", padding=(10, 6))
        self.style.configure("Red.Horizontal.TProgressbar", background="#d32f2f", troughcolor="#e0e0e0")
        self.style.configure("Yellow.Horizontal.TProgressbar", background="#f9a825", troughcolor="#e0e0e0")
        self.style.configure("Green.Horizontal.TProgressbar", background="#2e7d32", troughcolor="#e0e0e0")

        main = ttk.Frame(self, padding=18)
        main.pack(fill="both", expand=True)

        title = ttk.Label(main, text="Client Progress Manager", style="Header.TLabel")
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        details_frame = ttk.LabelFrame(main, text="Client Details", style="Section.TLabelframe")
        details_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 14))

        details_frame.columnconfigure(1, weight=1)

        ttk.Label(details_frame, text="Client Name").grid(row=0, column=0, sticky="w", padx=(10, 12), pady=(12, 8))
        self.client_combo = ttk.Combobox(details_frame, textvariable=self.client_name_var, state="normal")
        self.client_combo.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=(12, 8))
        self.client_combo.bind("<<ComboboxSelected>>", self.on_client_name_selected)
        self.refresh_client_combo()

        ttk.Label(details_frame, text="Contact").grid(row=1, column=0, sticky="w", padx=(10, 12), pady=(0, 8))
        self.contact_entry = ttk.Entry(details_frame, textvariable=self.contact_var)
        self.contact_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 8))

        ttk.Label(details_frame, text="Business").grid(row=2, column=0, sticky="w", padx=(10, 12), pady=(0, 8))
        self.business_entry = ttk.Entry(details_frame, textvariable=self.business_var)
        self.business_entry.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=(0, 8))

        ttk.Label(details_frame, text="Email").grid(row=3, column=0, sticky="w", padx=(10, 12), pady=(0, 10))
        self.email_entry = ttk.Entry(details_frame, textvariable=self.email_var)
        self.email_entry.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))

        action_row = ttk.Frame(main)
        action_row.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ttk.Button(action_row, text="Create Client Plan", command=self.create_plan, style="Action.TButton").pack(side="left", padx=(0, 8))

        progress_box = ttk.LabelFrame(main, text="Progress Overview", style="Section.TLabelframe")
        progress_box.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        progress_box.columnconfigure(1, weight=1)

        ttk.Label(progress_box, text="Progress").grid(row=0, column=0, sticky="w", padx=(10, 12), pady=(12, 6))
        self.progress_var = tk.StringVar(value="0%")
        ttk.Label(progress_box, textvariable=self.progress_var, font=("Segoe UI", 14, "bold")).grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(12, 6))

        self.progress_bar = ttk.Progressbar(progress_box, orient="horizontal", length=500, mode="determinate")
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(10, 10), pady=(0, 12))
        self._apply_progress_bar_color(0)

        ttk.Label(progress_box, text="Total Tasks").grid(row=2, column=0, sticky="w", padx=(10, 12), pady=(0, 12))
        self.total_entry = ttk.Entry(progress_box, textvariable=self.total_tasks_var, state="readonly")
        self.total_entry.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=(0, 12))

        tasks_frame = ttk.LabelFrame(main, text="Tasks", style="Section.TLabelframe")
        tasks_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(0, 12))
        tasks_frame.columnconfigure(0, weight=1)
        tasks_frame.columnconfigure(1, weight=1)
        tasks_frame.rowconfigure(1, weight=1)

        ttk.Label(tasks_frame, text="All Tasks", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=(10, 0), pady=(10, 4))
        ttk.Label(tasks_frame, text="Pending Tasks", font=("Segoe UI", 9, "bold")).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(10, 4))

        all_scroll = ttk.Scrollbar(tasks_frame, orient="vertical")
        pending_scroll = ttk.Scrollbar(tasks_frame, orient="vertical")

        self.all_tasks_box = tk.Listbox(
            tasks_frame,
            height=12,
            width=30,
            exportselection=False,
            bg="#ffffff",
            selectmode="browse",
            font=("Segoe UI", 9),
            yscrollcommand=all_scroll.set,
            relief="solid",
            borderwidth=1,
        )
        self.pending_tasks_box = tk.Listbox(
            tasks_frame,
            height=12,
            width=30,
            exportselection=False,
            bg="#fffef5",
            selectmode="browse",
            font=("Segoe UI", 9),
            yscrollcommand=pending_scroll.set,
            relief="solid",
            borderwidth=1,
        )

        all_scroll.config(command=self.all_tasks_box.yview)
        pending_scroll.config(command=self.pending_tasks_box.yview)

        self.all_tasks_box.grid(row=1, column=0, sticky="nsew", padx=(10, 4), pady=(0, 10))
        all_scroll.grid(row=1, column=1, sticky="ns", padx=(0, 8), pady=(0, 10))
        self.pending_tasks_box.grid(row=1, column=2, sticky="nsew", padx=(0, 4), pady=(0, 10))
        pending_scroll.grid(row=1, column=3, sticky="ns", padx=(0, 10), pady=(0, 10))

        task_entry_row = ttk.Frame(tasks_frame)
        task_entry_row.grid(row=2, column=0, columnspan=4, sticky="ew", padx=(10, 10), pady=(0, 10))
        ttk.Label(task_entry_row, text="New task").pack(side="left", padx=(0, 8))
        self.new_task_entry = ttk.Entry(task_entry_row, textvariable=self.new_task_var)
        self.new_task_entry.pack(side="left", fill="x", expand=True)

        button_row = ttk.Frame(tasks_frame)
        button_row.grid(row=3, column=0, columnspan=4, sticky="ew", padx=(10, 10), pady=(0, 12))

        ttk.Button(button_row, text="Add Task", command=self.add_task, style="Action.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Tasks Details", command=self.open_task_details_window, style="Action.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Refresh Progress", command=self.refresh_display, style="Action.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Open All Clients", command=self.open_all_clients, style="Action.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Send Email", command=self.send_email_to_client, style="Action.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Save & Exit", command=self.save_and_exit, style="Action.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Cancel", command=self.cancel_and_exit, style="Action.TButton").pack(side="left")

        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(4, weight=3)
        progress_box.columnconfigure(1, weight=1)

        self.clear_client_form()

    def refresh_client_combo(self):
        self.client_manager.load_clients()
        names = [client.name for client in self.client_manager.clients]
        combo_values = ["<New Client>"] + names
        self.client_combo.configure(values=combo_values)
        if self.client_name_var.get() in combo_values:
            self.client_combo.set(self.client_name_var.get())
        else:
            self.client_combo.set("<New Client>")

    def clear_client_form(self):
        self.plan = None
        self.client_name_var.set("")
        self.contact_var.set("")
        self.business_var.set("")
        self.email_var.set("")
        self.total_tasks_var.set("0")
        self.new_task_var.set("")
        self.progress_var.set("0%")
        self.progress_bar["value"] = 0
        self.progress_bar.configure(style="Red.Horizontal.TProgressbar")
        self.all_tasks_box.delete(0, tk.END)
        self.pending_tasks_box.delete(0, tk.END)
        self.all_tasks_box.insert(tk.END, "No client selected")
        self.pending_tasks_box.insert(tk.END, "No pending tasks")

    def on_client_name_selected(self, event=None):
        name = self.client_name_var.get().strip()
        if not name:
            self.clear_client_form()
            return

        if name == "<New Client>":
            self.clear_client_form()
            self.client_name_var.set("")
            return

        self.client_manager.load_clients()
        matching_client = next(
            (client for client in self.client_manager.clients if client.name.lower() == name.lower()),
            None,
        )

        if matching_client is None:
            self.clear_client_form()
            self.client_name_var.set(name)
            return

        self.load_client_progress(matching_client.name, matching_client.business)
        self.contact_var.set(matching_client.contact)
        self.business_var.set(matching_client.business)
        self.email_var.set(matching_client.email)

    def _parse_task_list(self):
        try:
            total = int(self.total_tasks_var.get())
        except ValueError:
            total = 0

        if total <= 0:
            return []
        return [f"Task {i}" for i in range(1, total + 1)]

    def create_plan(self):
        name = self.client_name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing client", "Please enter a client name.")
            return

        contact = self.contact_var.get().strip()
        business = self.business_var.get().strip()
        if not contact:
            messagebox.showwarning("Missing contact", "Please enter the client contact number.")
            return
        if not business:
            messagebox.showwarning("Missing business", "Please enter the client business type.")
            return

        email = self.email_var.get().strip()
        tasks = self._parse_task_list()

        self.client_manager.load_clients()
        existing = next((client for client in self.client_manager.clients if client.name.lower() == name.lower()), None)
        if existing is None:
            client = Client(name, contact, business, email)
            self.client_manager.clients.append(client)
            self.client_manager.save_clients()
        else:
            existing.contact = contact
            existing.business = business
            existing.email = email or existing.email
            self.client_manager.save_clients()
            client = existing

        self.plan = Plan(client, all_tasks=list(tasks))
        self.plan.sync_task_lists(all_tasks=list(tasks), pending_tasks=list(tasks))
        self.total_tasks_var.set(str(len(self.plan.all_tasks)))
        self.refresh_display()

    def open_task_details_window(self):
        if self.plan is None:
            messagebox.showwarning("No client plan", "Create a client plan first.")
            return

        TaskDetailsWindow(
            self,
            client_name=self.client_name_var.get().strip() or self.plan.client_name,
            plan=self.plan,
            all_tasks=list(self.plan.all_tasks),
            pending_tasks=list(self.plan.pending_tasks),
        )

    def add_task(self):
        if self.plan is None:
            messagebox.showwarning("No client plan", "Create a client plan first.")
            return

        task = self.new_task_var.get().strip()
        if not task:
            return

        self.plan.add_pending_task(task)
        self.refresh_display()
        self.new_task_var.set("")

    def complete_selected_task(self):
        if self.plan is None:
            return

        selected = self.pending_tasks_box.curselection()
        if not selected:
            messagebox.showwarning("No task selected", "Select a task from the pending list.")
            return

        task = self.pending_tasks_box.get(selected[0])
        self.plan.complete_task(task)
        self.refresh_display()

    def _apply_progress_bar_color(self, value):
        if value < 33:
            self.progress_bar.configure(style="Red.Horizontal.TProgressbar")
        elif value < 66:
            self.progress_bar.configure(style="Yellow.Horizontal.TProgressbar")
        else:
            self.progress_bar.configure(style="Green.Horizontal.TProgressbar")

    def refresh_display(self):
        self.all_tasks_box.delete(0, tk.END)
        self.pending_tasks_box.delete(0, tk.END)

        if self.plan is None:
            self.all_tasks_box.insert(tk.END, "No client selected")
            self.pending_tasks_box.insert(tk.END, "No pending tasks")
            return

        self.plan.sync_task_lists(all_tasks=self.plan.all_tasks, pending_tasks=self.plan.pending_tasks)
        self.progress_var.set(f"{self.plan.progress}%")
        self.progress_bar["value"] = self.plan.progress
        self._apply_progress_bar_color(self.plan.progress)
        self.total_tasks_var.set(str(len(self.plan.all_tasks)))

        if self.plan.all_tasks:
            for task in self.plan.all_tasks:
                self.all_tasks_box.insert(tk.END, task)
        else:
            self.all_tasks_box.insert(tk.END, "No tasks yet")

        if self.plan.pending_tasks:
            for task in self.plan.pending_tasks:
                self.pending_tasks_box.insert(tk.END, task)
        else:
            self.pending_tasks_box.insert(tk.END, "No pending tasks")

    def load_client_progress(self, client_name, business="N/A"):
        self.client_manager.load_clients()
        matching_client = next(
            (client for client in self.client_manager.clients if client.name.lower() == client_name.lower()),
            None,
        )

        if matching_client is not None:
            client = matching_client
            business = matching_client.business
            self.contact_var.set(matching_client.contact)
            self.business_var.set(matching_client.business)
            self.email_var.set(matching_client.email)
        else:
            client = Client(client_name, "N/A", business)

        saved = Plan.Clients_progress.get(client_name, {})
        all_tasks = list(saved.get("all_tasks", []))

        if not all_tasks:
            default_total = self.total_tasks_var.get().strip()
            try:
                total = int(default_total) if default_total else 5
            except ValueError:
                total = 5
            all_tasks = [f"Task {i}" for i in range(1, total + 1)]

        pending_tasks = list(saved.get("pending_tasks", all_tasks))
        self.client_name_var.set(client_name)
        self.plan = Plan(client, all_tasks=all_tasks)
        self.plan.sync_task_lists(all_tasks=all_tasks, pending_tasks=pending_tasks)
        self.total_tasks_var.set(str(len(self.plan.all_tasks)))
        self.refresh_display()

    def save_current_client(self):
        if self.plan is None:
            return

        self.client_manager.load_clients()
        name = self.client_name_var.get().strip()
        if not name:
            return

        existing = next(
            (client for client in self.client_manager.clients if client.name.lower() == name.lower()),
            None,
        )
        contact = self.contact_var.get().strip()
        business = self.business_var.get().strip()
        if not contact:
            messagebox.showwarning("Missing contact", "Please enter the client contact number before saving.")
            return
        if not business:
            messagebox.showwarning("Missing business", "Please enter the client business type before saving.")
            return

        if existing is None:
            client = Client(
                name,
                contact,
                business,
                self.email_var.get().strip(),
            )
            self.client_manager.clients.append(client)
        else:
            existing.contact = contact
            existing.business = business
            existing.email = self.email_var.get().strip() or existing.email
            client = existing

        self.client_manager.save_clients()
        self.plan.client = client
        self.plan.client_name = client.name
        self.plan.update_clients_progress()

    def send_email_to_client(self):
        email = self.email_var.get().strip()
        if not email:
            messagebox.showwarning("No email", "This client does not have an email saved yet.")
            return

        gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={quote(email)}"
        if webbrowser.open(gmail_url):
            return

        mailto_url = f"mailto:{quote(email)}"
        webbrowser.open(mailto_url)

    def save_and_exit(self):
        self.save_current_client()
        self.destroy()

    def cancel_and_exit(self):
        self.destroy()

    def open_all_clients(self):
        AllClientsProgressWindow(self)


if __name__ == "__main__":
    safe_main()
