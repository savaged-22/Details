import argparse
import requests
import json
import sys
import time

banner = """
  █     █░ ▄▄▄     ▄▄▄█████▓  ██████  ▒█████   ███▄    █
▓█░ █ ░█░▒████▄   ▓  ██▒ ▓▒▒██    ▒ ▒██▒  ██▒ ██ ▀█   █
▒█░ █ ░█ ▒██  ▀█▄ ▒ ▓██░ ▒░░ ▓██▄   ▒██░  ██▒▓██  ▀█ ██▒
░█░ █ ░█ ░██▄▄▄▄██░ ▓██▓ ░   ▒   ██▒▒██   ██░▓██▒  ▐▌██▒
░░██▒██▓ ▒▓█   ▓██  ▒██▒ ░ ▒██████▒▒░ ████▓▒░▒██░   ▓██░
░ ▓░▒ ▒  ░▒▒   ▓▒█  ▒ ░░   ▒ ▒▓▒ ▒ ░░ ▒░▒░▒░ ░ ▒░   ▒ ▒
  ▒ ░ ░  ░ ░   ▒▒     ░    ░ ░▒  ░ ░  ░ ▒ ▒░ ░ ░░   ░ ▒░
  ░   ░    ░   ▒    ░      ░  ░  ░  ░ ░ ░ ▒     ░   ░ ░
    ░          ░                 ░      ░ ░           ░
v 0.1.0"""


print(banner,"\n")
BASE_URL = "http://192.168.1.7:8000"
BANNER = "Remember every process takes time to our server."

def docs():
    readme = """
        === Documentación CLI OSINT ===

        Uso:
            python osint_tool.py [opciones]

        Opciones:
            --email <email>        Realiza GET a /api/osint/email/{email}
            --ip <ip>              Realiza GET a /api/osint/ip/{ip}
            --AI <prompt>          Realiza POST a /api/AI con un prompt
            --Docs                 Muestra esta ayuda

        Si no se proporcionan argumentos, se inicia el menú interactivo.

        /**************************************** Watson AI ***************************************************/
        1. What is Watson?
            Watson is a tool that will help you in your current investigation around someone in internet.
            In this digital age everyone is realted to something an email, ip address, phone number, and others.
            But one little detail that everyone forgot is that everyone is realted to other people in aspects we cannot
            notice at the first glance. Watson works with a database that help relate people through these aspects.

        2. How works Watson? 
            You send us a a request to analyze an email, ip address, phone, username, or Company.
            After we do our process to check for information through internet and our databases, we return information to you in a raw format and at the same time. 
            We send the information to our AI Agent to help you to understand the payload. 

        3. Power by IA?
            Yes, our AI agent Watson works with the data we find and store in our database help to clarify the payload.
            That's thereason we gave that cool name to the tool, cause we find you as a great researcher like sherlock homes.
            But every sherlock need a watson and that is what we want to give you.
        
        4. Why use watson?
            Give any reason to use watson, the idea is to increase the posibilities to any kind of usage. 
            With the help from our community, we want to improve watson to make it better.
        
        5. what inspire us to create this tool?
            From our point of view we want to help the people to investigate from any kind of source about "people"
            to make a better job to make a better world.
    """
    print(readme)

def get_email_info(email:str):
    print(BANNER)
    print("Investigate in our database and internet an email you want.")
    try:
        response = requests.get(f"{BASE_URL}/api/osint/email/{email}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def get_ip_info(ip:str):
    print(BANNER)
    print("Investigate in our database and internet an email you want.")
    try:
        response = requests.get(f"{BASE_URL}/api/osint/email/{ip}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")
    pass

def post_ai(prompt:str):
    print(BANNER)
    payload = {"prompt": prompt}
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    try:
        response = requests.post(f"{BASE_URL}/api/AI", headers=headers, json=payload)
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def post_profile_soc():
    print(BANNER)
    warning = """
        Warninig:

        1.) Before insert the name of your file, verify that your file have the same structure like in 'example.txt'. 
        To preserve the quality of our database, and if you dont have the complete data for every profile you want to upload, send us the info before to the next email
        and we will check it and send you an answer the fast as posible. 

        2.) If you have a documents you want to analyze to chat with does documents, go to our telegram bot read the instructions, 
        upload the file and finally chat directly with our Watson AI. (This feature is in progress).
    """
    print(warning)
    time.sleep(10)
    file = open("leaks.txt","r")
    res =  file.readlines()
    for line in res:
        res_x = line.split("\t")
        names = []
        emails = []
        ips = []
        usernames = []
        names.append(res_x[1])
        ips.append(res_x[2])
        emails.append(res_x[3])
        usernames.extend([res_x[1],extract_username(res_x[3])])
        payload = {
            "name":names,
            "surname":[],
            "email":emails,
            "urls":[],
            "ip":ips,
            "company":"",
            "username":usernames,
            "phone":[]
        }
        print("-----------------------------------------")
        payload_do = json.dumps(payload)
        print(payload_do)
        headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
        
        
def extract_username(email:str):
    prov = email.split("@")
    return prov[0]

def main_menu():
    while True:
        print("\n=== Menú de Peticiones OSINT/IA ===")
        print("1. Read File to upload your data to our database")
        print("2. Investigate email")
        print("3. GET /api/osint/ip/{ip}")
        print("4. POST /api/AI")
        print("5. Documentacion")
        print("6. Salir")
        
        choice = input("Elige una opción (1-5): ").strip()

        if choice == "1":
            print("Indicate the route of the file you want us to read.")
            post_profile_soc()
        elif choice == "2":
            email = input("Introduce el email: ").strip()
            get_email_info(email)
        elif choice == "3":
            ip = input("Introduce la IP: ").strip()
            get_ip_info(ip)
        elif choice == "4":
            prompt = input("Introduce el prompt para la IA: ")
            post_ai(prompt)
        elif choice == "5":
            docs()
            print("Documentacion")
        elif choice == "6":
            print("Thanks for use watson.")
            break

        else:
            print("Opción no válida. Intenta de nuevo.")

def parse_args():
    parser = argparse.ArgumentParser(description="Herramienta OSINT + AI")
    parser.add_argument("--email", help="Consulta información de un email")
    parser.add_argument("--ip", help="Consulta información de una IP")
    parser.add_argument("--AI", help="Envía un prompt a la IA")
    parser.add_argument("--Docs", action="store_true", help="Muestra la documentación")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    if args.Docs:
        docs()
    elif args.email:
        get_email_info(args.email)
    elif args.ip:
        get_ip_info(args.ip)
    elif args.AI:
        post_ai(args.AI)
    else:
        main_menu()





"""
import argparse
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def post_profile_soc():
    print("\n--- Enviar datos a /api/osint/profileSoc ---")
    name = input("Nombre(s): ").split(",")
    email = input("Email(s): ").split(",")
    ip = input("IP(s): ").split(",")
    username = input("Username(s): ").split(",")

    payload = {
        "name": [n.strip() for n in name if n.strip()],
        "surname": [],
        "email": [e.strip() for e in email if e.strip()],
        "urls": [],
        "ip": [i.strip() for i in ip if i.strip()],
        "company": "",
        "username": [u.strip() for u in username if u.strip()],
        "phone": [],
        "entity": "profile"
    }

    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    try:
        response = requests.post(f"{BASE_URL}/api/osint/profileSoc", headers=headers, json=payload)
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def get_email_info(email):
    try:
        response = requests.get(f"{BASE_URL}/api/osint/email/{email}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def get_ip_info(ip):
    try:
        response = requests.get(f"{BASE_URL}/api/osint/ip/{ip}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def post_ai(prompt):
    payload = {"prompt": prompt}
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    try:
        response = requests.post(f"{BASE_URL}/api/AI", headers=headers, json=payload)
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def main_menu():
    while True:
        print("\n=== Menú de Peticiones OSINT/IA ===")
        print("1. POST /api/osint/profileSoc")
        print("2. GET /api/osint/email/{email}")
        print("3. GET /api/osint/ip/{ip}")
        print("4. POST /api/AI")
        print("5. Salir")
        
        choice = input("Elige una opción (1-5): ").strip()

        if choice == "1":
            post_profile_soc()
        elif choice == "2":
            email = input("Introduce el email: ").strip()
            get_email_info(email)
        elif choice == "3":
            ip = input("Introduce la IP: ").strip()
            get_ip_info(ip)
        elif choice == "4":
            prompt = input("Introduce el prompt para la IA: ")
            post_ai(prompt)
        elif choice == "5":
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

def parse_args():
    parser = argparse.ArgumentParser(description="Herramienta OSINT + AI")
    parser.add_argument("--email", help="Consulta información de un email")
    parser.add_argument("--ip", help="Consulta información de una IP")
    parser.add_argument("--AI", help="Envía un prompt a la IA")
    parser.add_argument("--Docs", action="store_true", help="Muestra la documentación")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    if args.Docs:
        show_docs()
    elif args.email:
        get_email_info(args.email)
    elif args.ip:
        get_ip_info(args.ip)
    elif args.AI:
        post_ai(args.AI)
    else:
        main_menu()




"""