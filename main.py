import argparse
import requests
import json
import sys
import time
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass # In case dotenv is not installed

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
BASE_URL = os.getenv("BASE_URL")
API_TOKEN = os.getenv("API_TOKEN")

BANNER = "Remember every process takes time to our server."

def docs():
    readme = """
        === Documentación CLI OSINT ===

        Uso:
            python main.py [opciones]

        Opciones:
            --email <email>        Realiza búsqueda por email
            --ip <ip>              Realiza búsqueda por IP
            --username <user>      Realiza búsqueda por username
            --domain <domain>      Realiza búsqueda por dominio
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
    """
    print(readme)

def perform_search(query_type: str, query_value: str):
    print(BANNER)
    print(f"Investigating {query_type}: {query_value} in our database and internet...")
    
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {API_TOKEN}'
    }
    
    params = {
        'query_type': query_type,
        'query_value': query_value
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/tools/search", headers=headers, params=params)
        
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Error connecting to server: {e}")

def main_menu():
    while True:
        print("\n=== Menú de Peticiones OSINT/IA ===")
        print("1. Investigate email")
        print("2. Investigate IP")
        print("3. Investigate username")
        print("4. Investigate domain")
        print("5. Documentacion")
        print("6. Salir")
        
        choice = input("Elige una opción (1-6): ").strip()

        if choice == "1":
            email = input("Introduce el email: ").strip()
            perform_search("email", email)
        elif choice == "2":
            ip = input("Introduce la IP: ").strip()
            perform_search("ip", ip)
        elif choice == "3":
            username = input("Introduce el username: ").strip()
            perform_search("username", username)
        elif choice == "4":
            domain = input("Introduce el dominio: ").strip()
            perform_search("domain", domain)
        elif choice == "5":
            docs()
        elif choice == "6":
            print("Thanks for using watson.")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

def parse_args():
    parser = argparse.ArgumentParser(description="Herramienta OSINT + AI")
    parser.add_argument("--email", help="Consulta información de un email")
    parser.add_argument("--ip", help="Consulta información de una IP")
    parser.add_argument("--username", help="Consulta información de un username")
    parser.add_argument("--domain", help="Consulta información de un dominio")
    parser.add_argument("--Docs", action="store_true", help="Muestra la documentación")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    if args.Docs:
        docs()
    elif args.email:
        perform_search("email", args.email)
    elif args.ip:
        perform_search("ip", args.ip)
    elif args.username:
        perform_search("username", args.username)
    elif args.domain:
        perform_search("domain", args.domain)
    else:
        main_menu()