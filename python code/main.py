from clients_management import ClientManager

if __name__ == "__main__":
    manager = ClientManager("clients.json")



    manager.add_client("Bin Salim", "99999999", "machineries suppliers 'Hilti'")
    manager.add_client("Ali Ahmed", "55555555", "Printing Services")

    print("\nAll clients:")
    print(manager.list_clients())

    print("\nSearch result for 'ali':")
    for client in manager.search_clients("ali"):
        print(client)
