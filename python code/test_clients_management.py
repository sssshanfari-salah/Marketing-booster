import os
import tempfile
import unittest

from clients_management import Client, ClientManager
from clients_progress_ui import Plan


class ClientManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, "clients.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_and_list_clients(self):
        manager = ClientManager(self.file_path)
        manager.add_client("Bin Salim", "99999999", "machineries suppliers 'Hilti'")

        self.assertEqual(len(manager.clients), 1)
        self.assertEqual(manager.clients[0].name, "Bin Salim")
        self.assertIn("Bin Salim", manager.list_clients())

    def test_search_client(self):
        manager = ClientManager(self.file_path)
        manager.add_client("Ali", "123456", "Stationery")
        manager.add_client("Sara", "654321", "Electronics")

        result = manager.search_clients("sara")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Sara")

    def test_save_and_load(self):
        manager = ClientManager(self.file_path)
        manager.add_client("John", "111", "IT")
        manager.save_clients()

        loaded = ClientManager(self.file_path)
        loaded.load_clients()

        self.assertEqual(len(loaded.clients), 1)
        self.assertEqual(loaded.clients[0].name, "John")

    def test_manager_starts_with_loaded_clients(self):
        manager = ClientManager(self.file_path)
        self.assertEqual(manager.clients, [])

        manager.add_client("Sarah", "777", "Design")
        self.assertEqual(len(manager.clients), 1)
        self.assertEqual(manager.clients[0].name, "Sarah")

    def test_add_client_with_email(self):
        manager = ClientManager(self.file_path)
        manager.add_client("Nora", "555", "Consulting", "nora@example.com")

        self.assertEqual(manager.clients[0].email, "nora@example.com")
        self.assertEqual(manager.clients[0].to_dict()["email"], "nora@example.com")

    def test_delete_client_removes_selected_client(self):
        manager = ClientManager(self.file_path)
        manager.add_client("Ali", "123", "Stationery")
        manager.add_client("Sara", "456", "Electronics")

        removed = manager.delete_client("Ali")

        self.assertTrue(removed)
        self.assertEqual(len(manager.clients), 1)
        self.assertEqual(manager.clients[0].name, "Sara")

    def test_plan_sync_keeps_pending_tasks_in_sync(self):
        plan = Plan(Client("Sam", "123", "Marketing"), all_tasks=["Task 1", "Task 2", "Task 3"])
        plan.pending_tasks = ["Task 1", "Task 3"]

        plan.sync_task_lists(all_tasks=["Task 1", "Task 2", "Task 3", "Task 4"], pending_tasks=["Task 2", "Task 4"])

        self.assertEqual(plan.all_tasks, ["Task 1", "Task 2", "Task 3", "Task 4"])
        self.assertEqual(plan.pending_tasks, ["Task 2", "Task 4"])


if __name__ == "__main__":
    unittest.main()
