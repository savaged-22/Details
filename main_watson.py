import argparse
import requests
import json
import sys
import time
import os

# Importamos nuestro modulo de limpieza (debe estar en la misma carpeta)
from watson_clean import limpiar_respuesta, _dominio_limpio

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # In case dotenv is not installed

banner = """
  W A T S O N
  v 0.1.0"""

print(banner, "\n")
BASE_URL = os.getenv("BASE_URL")
API_TOKEN = os.getenv("API_TOKEN")

BANNER = "Remember every process takes time to our server."


def docs():
    readme = """
        === Documentacion CLI OSINT ===

        Uso:
            python main.py [opciones]

        Opciones:
            --email <email>        Realiza busqueda por email
            --ip <ip>              Realiza busqueda por IP
            --username <user>      Realiza busqueda por username
            --domain <domain>      Realiza busqueda por dominio
            --raw                  Muestra la respuesta CRUDA (sin limpiar)
            --Docs                 Muestra esta ayuda

        Si no se proporcionan argumentos, se inicia el menu interactivo.
    """
    print(readme)


def perform_search(query_type: str, query_value: str, mostrar_crudo: bool = False):
    # Si es dominio, limpiamos la ENTRADA antes de enviar
    # (el servidor falla si le llega la URL completa con https:// y /path)
    if query_type == "domain":
        query_value = _dominio_limpio(query_value)

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
            cruda = response.json()

            # --- LIMPIEZA EN CALIENTE ---
            # En vez de mostrar el crudo, lo limpiamos al vuelo.
            if mostrar_crudo:
                # opcion interna para depurar: ver el crudo
                print(json.dumps(cruda, indent=2, ensure_ascii=False))
            else:
                limpio = limpiar_respuesta(cruda)
                # Mostramos el resultado limpio al cliente
                print(json.dumps(limpio, indent=2, ensure_ascii=False))
                # Y lo guardamos en un JSON para compartir
                nombre_archivo = f"resultado_{query_type}_{query_value}.json"
                # limpiar caracteres problematicos del nombre de archivo
                nombre_archivo = nombre_archivo.replace("/", "_").replace("@", "_at_").replace(":", "_")
                with open(nombre_archivo, "w", encoding="utf-8") as f:
                    json.dump(limpio, f, ensure_ascii=False, indent=2)
                print(f"\n[+] Resultado limpio guardado en: {nombre_archivo}")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Error connecting to server: {e}")


def main_menu():
    while True:
        print("\n=== Menu de Peticiones OSINT/IA ===")
        print("1. Investigate email")
        print("2. Investigate IP")
        print("3. Investigate username")
        print("4. Investigate domain")
        print("5. Documentacion")
        print("6. Salir")

        choice = input("Elige una opcion (1-6): ").strip()

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
            print("Opcion no valida. Intenta de nuevo.")


def parse_args():
    parser = argparse.ArgumentParser(description="Herramienta OSINT + AI")
    parser.add_argument("--email", help="Consulta informacion de un email")
    parser.add_argument("--ip", help="Consulta informacion de una IP")
    parser.add_argument("--username", help="Consulta informacion de un username")
    parser.add_argument("--domain", help="Consulta informacion de un dominio")
    parser.add_argument("--raw", action="store_true", help="Muestra la respuesta cruda sin limpiar")
    parser.add_argument("--Docs", action="store_true", help="Muestra la documentacion")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.Docs:
        docs()
    elif args.email:
        perform_search("email", args.email, mostrar_crudo=args.raw)
    elif args.ip:
        perform_search("ip", args.ip, mostrar_crudo=args.raw)
    elif args.username:
        perform_search("username", args.username, mostrar_crudo=args.raw)
    elif args.domain:
        perform_search("domain", args.domain, mostrar_crudo=args.raw)
    else:
        main_menu()