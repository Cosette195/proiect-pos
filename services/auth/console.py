import grpc
from idm_client import IDMClient

MENU = """
1. Autentificare
2. Listare conturi
3. Creare cont
4. Dezactivare cont
5. Activare cont
6. Validare token
7. Distrugere token
8. Introducere token manual
0. Iesire
"""


def run():
    client = IDMClient()
    token = ""

    while True:
        print(MENU)
        option = input("Optiune: ").strip()

        if option == "0":
            break

        try:
            if option == "1":
                token = client.auth(input("Username: "), input("Parola: "))
                print("Token:", token)
            elif option == "2":
                for account in client.list_accounts(token):
                    print(account)
            elif option == "3":
                print("Succes:", client.create_account(token, input("Username: "),
                                                        input("Rol (administrator/maintainer): ")))
            elif option == "4":
                print("Succes:", client.deactivate_account(token, input("Username: ")))
            elif option == "5":
                print("Succes:", client.activate_account(input("Username: "), input("Parola initiala: ")))
            elif option == "6":
                sub, role = client.validate_token(token)
                print("sub:", sub)
                print("role:", role)
            elif option == "7":
                print("Succes:", client.delete_token(token))
            elif option == "8":
                token = input("Token: ")
            else:
                print("Optiune invalida")
        except grpc.RpcError as e:
            print("Error:", e.details())
            print("Status code:", e.code())

    client.close()

if __name__ == "__main__":
    run()