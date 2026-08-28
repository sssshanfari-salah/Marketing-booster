import os
import tempfile
import unittest

from clients_management import Client, ClientManager


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


if __name__ == "__main__":
    unittest.main()
