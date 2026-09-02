import json
from pathlib import Path
from typing import List


class Client:
    def __init__(self, name: str, contact: str, business: str, email: str = ""):
        self.name = name
        self.contact = contact
        self.business = business
        self.email = email

    def to_dict(self):
        return {
            "name": self.name,
            "contact": self.contact,
            "business": self.business,
            "email": self.email,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("name", ""),
            data.get("contact", ""),
            data.get("business", ""),
            data.get("email", ""),
        )

    def __repr__(self):
        return f"Client name: {self.name}\nContact: {self.contact}\nType of business: {self.business}\nEmail: {self.email}"


class ClientManager:
    def __init__(self, file_path=None):
        if file_path is None:
            file_path = Path(__file__).resolve().parent.parent / "clients.json"
        self.file_path = Path(file_path)
        self.clients = []
        self.load_clients()

    def add_client(self, name: str, contact: str, business: str, email: str = ""):
        client = Client(name, contact, business, email)
        self.clients.append(client)
        self.save_clients()

    def delete_client(self, name: str):
        if not name or not isinstance(name, str):
            return False

        target_name = name.strip()
        if not target_name:
            return False

        before = len(self.clients)
        self.clients = [client for client in self.clients if client.name.lower() != target_name.lower()]

        if len(self.clients) == before:
            return False

        self.save_clients()
        return True

    def list_clients(self):
        if not self.clients:
            return "No clients found."

        result = []
        for client in self.clients:
            email_info = f" | {client.email}" if client.email else ""
            result.append(f"{client.name} | {client.contact} | {client.business}{email_info}")
        return "\n".join(result)

    def search_clients(self, keyword: str):
        keyword_lower = keyword.lower()
        return [
            client
            for client in self.clients
            if keyword_lower in client.name.lower()
            or keyword_lower in client.contact.lower()
            or keyword_lower in client.business.lower()
            or keyword_lower in client.email.lower()
        ]

    def save_clients(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
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

    def json2txt(self):
        with self.file_path.open("r", encoding="utf-8") as infile:
            data = json.load(infile)

        output_path = Path(r"docs/clients_data.txt")
        with output_path.open("w", encoding="utf-8") as outfile:
            outfile.write(json.dumps(data, indent=2))