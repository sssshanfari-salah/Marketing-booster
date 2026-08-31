import sys
import tkinter as tk
from tkinter import ttk, messagebox

from clients_management import Client


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


class ProgressApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Client Progress Tracker")
        self.geometry("850x600")
        self.minsize(760, 500)

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.client_name_var = tk.StringVar(value="Ali")
        self.total_tasks_var = tk.StringVar(value="5")
        self.new_task_var = tk.StringVar()

        self.plan = None

        self.build_ui()

    def build_ui(self):
        main = ttk.Frame(self, padding=16)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Client Name", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 6)
        )
        self.client_entry = ttk.Entry(main, textvariable=self.client_name_var)
        self.client_entry.grid(row=0, column=1, sticky="ew", pady=(0, 6))

        ttk.Label(main, text="Total Tasks", font=("Segoe UI", 10, "bold")).grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=(0, 6)
        )
        self.total_entry = ttk.Entry(main, textvariable=self.total_tasks_var)
        self.total_entry.grid(row=1, column=1, sticky="ew", pady=(0, 6))

        ttk.Button(main, text="Create Client Plan", command=self.create_plan).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(8, 12)
        )

        self.progress_var = tk.StringVar(value="0%")
        ttk.Label(main, text="Progress", font=("Segoe UI", 10, "bold")).grid(
            row=3, column=0, sticky="w", pady=(0, 6)
        )
        ttk.Label(main, textvariable=self.progress_var, font=("Segoe UI", 14, "bold")).grid(
            row=3, column=1, sticky="w", pady=(0, 6)
        )

        self.progress_bar = ttk.Progressbar(main, orient="horizontal", length=500, mode="determinate")
        self.progress_bar.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(4, 12))

        ttk.Label(main, text="All Tasks", font=("Segoe UI", 10, "bold")).grid(
            row=5, column=0, sticky="w", pady=(8, 4)
        )
        ttk.Label(main, text="Pending Tasks", font=("Segoe UI", 10, "bold")).grid(
            row=5, column=1, sticky="w", pady=(8, 4)
        )

        self.all_tasks_box = tk.Listbox(main, height=12, exportselection=False)
        self.pending_tasks_box = tk.Listbox(main, height=12, exportselection=False)

        self.all_tasks_box.grid(row=6, column=0, sticky="nsew", padx=(0, 8))
        self.pending_tasks_box.grid(row=6, column=1, sticky="nsew")

        ttk.Label(main, text="New task", font=("Segoe UI", 10, "bold")).grid(
            row=7, column=0, sticky="w", pady=(12, 4)
        )
        self.new_task_entry = ttk.Entry(main, textvariable=self.new_task_var)
        self.new_task_entry.grid(row=7, column=1, sticky="ew", pady=(12, 4))

        button_row = ttk.Frame(main)
        button_row.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(6, 0))

        ttk.Button(button_row, text="Add Task", command=self.add_task).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Mark Done", command=self.complete_selected_task).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Refresh Progress", command=self.refresh_display).pack(side="left")

        main.columnconfigure(1, weight=1)
        main.rowconfigure(6, weight=1)

        self.create_plan()

    def create_plan(self):
        name = self.client_name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing client", "Please enter a client name.")
            return

        try:
            total = int(self.total_tasks_var.get())
        except ValueError:
            messagebox.showwarning("Invalid total", "Please enter a valid number of tasks.")
            return

        client = Client(name, "N/A", "N/A")
        self.plan = Plan(client, all_tasks=[f"Task {i}" for i in range(1, total + 1)])
        self.plan.pending_tasks = list(self.plan.all_tasks)
        self.plan.refresh_progress()
        self.plan.update_clients_progress()
        self.refresh_display()

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

    def refresh_display(self):
        if self.plan is None:
            return

        self.plan.refresh_progress()
        self.progress_var.set(f"{self.plan.progress}%")
        self.progress_bar["value"] = self.plan.progress

        self.all_tasks_box.delete(0, tk.END)
        for task in self.plan.all_tasks:
            self.all_tasks_box.insert(tk.END, task)

        self.pending_tasks_box.delete(0, tk.END)
        for task in self.plan.pending_tasks:
            self.pending_tasks_box.insert(tk.END, task)


if __name__ == "__main__":
    safe_main()
