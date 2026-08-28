import json
from pathlib import Path
from typing import List


class Client:
    def __init__(self, name: str, contact: str, business: str):
        self.name = name
        self.contact = contact
        self.business = business

    def to_dict(self):
        return {
            "name": self.name,
            "contact": self.contact,
            "business": self.business,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["contact"], data["business"])

    def __repr__(self):
        return f"Client name: {self.name}\nContact: {self.contact}\nType of business: {self.business}"


class ClientManager:
    def __init__(self, file_path="clients.json"):
        self.file_path = Path(file_path)
        self.clients: List[Client] = []
        self.load_clients()

    def add_client(self, name: str, contact: str, business: str):
        client = Client(name, contact, business)
        self.clients.append(client)
        self.save_clients()

    def list_clients(self):
        if not self.clients:
            return "No clients found."

        result = []
        for client in self.clients:
            result.append(f"{client.name} | {client.contact} | {client.business}")
        return "\n".join(result)

    def search_clients(self, keyword: str):
        keyword_lower = keyword.lower()
        return [
            client
            for client in self.clients
            if keyword_lower in client.name.lower()
            or keyword_lower in client.contact.lower()
            or keyword_lower in client.business.lower()
        ]

    def save_clients(self):
        payload = [client.to_dict() for client in self.clients]
        self.file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load_clients(self):
        if not self.file_path.exists():
            self.clients = []
            return

        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            self.clients = [Client.from_dict(item) for item in data]
        except (json.JSONDecodeError, TypeError, ValueError):
            self.clients = []


if __name__ == "__main__":
    manager = ClientManager("clients.json")

    manager.add_client("Bin Salim", "99999999", "machineries suppliers 'Hilti'")
    manager.add_client("Ali Ahmed", "55555555", "Printing Services")

    print("\nAll clients:")
    print(manager.list_clients())

    print("\nSearch result for 'ali':")
    for client in manager.search_clients("ali"):
        print(client)
