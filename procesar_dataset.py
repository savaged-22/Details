"""
PROCESAMIENTO MASIVO DEL DATASET - WATSON

Lee un dataset (TSV) con columnas username, ipaddress, email y
consulta cada persona usando la logica de buscar_persona (las 3
busquedas en paralelo). Procesa en CHUNKS de 30 personas,
pausando entre chunks para revision manual.

- Un archivo por persona en Results/
- IPs se consultan UNA sola vez (se reusa el resultado) + etiqueta
  de en que emails aparece cada IP.
- Ritmo controlado para no saturar el servidor.
- Se puede REANUDAR: salta personas ya procesadas.

"""

import csv
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor

# Importamos lo que ya existe en tu proyecto
from main_watson import _buscar_uno
from watson_clean import limpiar_respuesta

# ---- CONFIGURACION ----
DATASET = "data.txt"          # tu archivo (ajusta la ruta si hace falta)
CHUNK_SIZE = 30               # personas por chunk
PAUSA_ENTRE_PERSONAS = 1.0    # segundos entre personas (no saturar)
RESULTS_DIR = "Results"

# Cache de IPs ya consultadas (para no repetir la misma IP)
_cache_ips = {}


def _nombre_archivo_persona(username, ip, email):
    """Genera el nombre del archivo de una persona (usa el primer dato)."""
    referencia = username or ip or email or "persona"
    nombre = f"persona_{referencia}.json"
    return nombre.replace("/", "_").replace("@", "_at_").replace(":", "_")


def _consultar_ip_con_cache(ip):
    """Consulta una IP, pero si ya se consulto antes, reusa el resultado."""
    if not ip:
        return None
    if ip in _cache_ips:
        return _cache_ips[ip]        # ya la teniamos, no gastamos consulta
    resultado = _buscar_uno("ip", ip)
    _cache_ips[ip] = resultado
    return resultado


def procesar_persona(persona):
    """
    Procesa UNA persona: busca username, ip (con cache) y email en
    paralelo, y guarda un archivo. Devuelve (nombre, ok/fallo).
    """
    username = persona.get("username") or None
    ip = persona.get("ipaddress") or None
    email = persona.get("email") or None

    nombre_archivo = _nombre_archivo_persona(username, ip, email)
    ruta = os.path.join(RESULTS_DIR, nombre_archivo)

    # REANUDAR: si ya existe, la saltamos
    if os.path.exists(ruta):
        return (nombre_archivo, "saltada")

    # Buscamos username y email en paralelo; la IP con cache aparte
    resultados = {}
    with ThreadPoolExecutor(max_workers=2) as executor:
        futuros = {}
        if username:
            futuros[executor.submit(_buscar_uno, "username", username)] = "username"
        if email:
            futuros[executor.submit(_buscar_uno, "email", email)] = "email"
        for futuro in futuros:
            tipo = futuros[futuro]
            resultados[tipo] = futuro.result()

    # La IP con cache (fuera del pool para reusar entre personas)
    if ip:
        resultados["ip"] = _consultar_ip_con_cache(ip)

    # Armamos el archivo con lo que si dio resultado
    investigacion = {}
    for tipo in ("username", "ip", "email"):
        if resultados.get(tipo) is not None:
            investigacion[tipo] = resultados[tipo]

    if not investigacion:
        return (nombre_archivo, "sin_resultado")

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(investigacion, f, ensure_ascii=False, indent=2)
    return (nombre_archivo, "ok")


def main():
    # 1) Leer el dataset (solo las 3 columnas que importan)
    with open(DATASET, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        personas = [
            {"username": r.get("username", ""),
             "ipaddress": r.get("ipaddress", ""),
             "email": r.get("email", "")}
            for r in reader
        ]

    os.makedirs(RESULTS_DIR, exist_ok=True)

    total = len(personas)
    print(f"Dataset cargado: {total} personas")

    # 2) Etiqueta: en que emails aparece cada IP (dato de investigacion)
    from collections import defaultdict
    ip_a_emails = defaultdict(list)
    for p in personas:
        if p["ipaddress"]:
            ip_a_emails[p["ipaddress"]].append(p["email"])
    ips_compartidas = {ip: correos for ip, correos in ip_a_emails.items() if len(correos) > 1}
    with open(os.path.join(RESULTS_DIR, "_ips_compartidas.json"), "w", encoding="utf-8") as f:
        json.dump(ips_compartidas, f, ensure_ascii=False, indent=2)
    print(f"IPs compartidas (en >1 email): {len(ips_compartidas)} -> guardado en Results/_ips_compartidas.json")

    # 3) Procesar por chunks
    for inicio in range(0, total, CHUNK_SIZE):
        chunk = personas[inicio:inicio + CHUNK_SIZE]
        num_chunk = inicio // CHUNK_SIZE + 1
        print(f"\n{'='*55}")
        print(f"CHUNK {num_chunk} (personas {inicio+1} a {inicio+len(chunk)} de {total})")
        print(f"{'='*55}")

        conteo = {"ok": 0, "saltada": 0, "sin_resultado": 0}
        for i, persona in enumerate(chunk, 1):
            nombre, estado = procesar_persona(persona)
            conteo[estado] = conteo.get(estado, 0) + 1
            print(f"  [{i}/{len(chunk)}] {persona['username']:25} -> {estado}")
            time.sleep(PAUSA_ENTRE_PERSONAS)

        print(f"\nResumen chunk {num_chunk}: {conteo}")

        # Pausa para revision manual (menos en el ultimo chunk)
        if inicio + CHUNK_SIZE < total:
            resp = input("\n¿Continuar con el siguiente chunk? (s/n): ").strip().lower()
            if resp != "s":
                print("Detenido por el usuario. Puedes reanudar despues (salta lo ya hecho).")
                break

    print("\nProcesamiento terminado.")


if __name__ == "__main__":
    main()