"""

WATSON - LIMPIEZA DE RESULTADOS 

Procesa la respuesta CRUDA de la API de Watson y devuelve un
resultado LIMPIO y unificado, listo para mostrar al cliente.

Soporta los 4 tipos de busqueda: username, email, ip, domain.
Cada tipo tiene su propia estructura, por eso hay un limpiador
especifico para cada uno (dispatcher segun query_type).

Para el cliente:
  - Se ocultan los nombres de las herramientas internas de busqueda.
  - Se filtra el ruido (Not Found, exists:false, errores tecnicos).
  - Se estandariza el texto (sin tildes, formato uniforme).
  - Se entrega en JSON legible.

Uso:
    from watson_clean import limpiar_respuesta
    limpio = limpiar_respuesta(respuesta_cruda_dict)   # dict -> dict

"""

import json
import unicodedata
from collections import Counter



# AUXILIARES

def _sin_tildes(texto):
    """Quita tildes de un texto (NFKD). Deja el resto igual."""
    if texto is None:
        return None
    texto = str(texto)
    return (
        unicodedata.normalize("NFKD", texto)
        .encode("ascii", errors="ignore")
        .decode("utf-8")
    )


def _dominio_limpio(valor):
    """
    Recorta una URL a su dominio base.
    'https://www.javeriana.edu.co/inicio' -> 'javeriana.edu.co'
    """
    if not valor:
        return valor
    v = str(valor).strip().lower()
    for prefijo in ("https://", "http://"):
        if v.startswith(prefijo):
            v = v[len(prefijo):]
    if v.startswith("www."):
        v = v[4:]
    # cortar en la primera barra (quitar /inicio, /path, etc.)
    v = v.split("/")[0]
    return v

def _es_encontrado(registro):
    """Decide si un registro representa un hallazgo positivo."""
    if not isinstance(registro, dict):
        return False
    status = str(registro.get("status", "")).lower()
    if status in ("found", "registered", "claimed"):
        return True
    if registro.get("exists") is True:
        return True
    if registro.get("confirmed") is True:
        return True
    return False


def _filtrar_data(data):
    """Filtra el 'data' dejando solo los registros encontrados."""
    if not isinstance(data, dict):
        return data
    nuevo = {}
    for clave, valor in data.items():
        if isinstance(valor, list) and valor and isinstance(valor[0], dict):
            nuevo[clave] = [r for r in valor if _es_encontrado(r)]
        else:
            nuevo[clave] = valor
    return nuevo

# LIMPIADOR: USERNAME

def _limpiar_username(cruda):
    """
    username: usa clean_profile (cuentas confirmadas con datos ricos
    en 'extra') y ademas cuenta cuantos sitios se revisaron.
    """
    query = cruda.get("query_value", "")
    perfiles = cruda.get("clean_profile", []) or []

    # Mapa sitio -> categoria (la categoria vive en los vectors del crudo,
    # no en el clean_profile, asi que la cruzamos)
    mapa_categorias = {}
    total_revisados = 0
    for fuente in cruda.get("sources", []):
        data = fuente.get("data", {}) or {}
        for v in data.get("vectors", []):
            if v.get("site_name"):
                mapa_categorias[v["site_name"]] = v.get("category")
            total_revisados += 1

    cuentas = []
    contador_categorias = Counter()
    for p in perfiles:
        if p.get("confirmed"):
            extra = p.get("extra", {}) or {}
            sitio = p.get("site_name", "")
            categoria = mapa_categorias.get(sitio)
            # contar categorias (ignorando las vacias)
            if categoria:
                contador_categorias[categoria] += 1
            cuentas.append({
                "sitio": sitio,
                "categoria": categoria,
                "url": (p.get("urls") or [""])[0],
                # datos ricos si el sitio los trae (Instagram, etc.)
                "nombre_real": extra.get("fullname"),
                "bio": extra.get("bio"),
                "seguidores": extra.get("follower_count"),
                "siguiendo": extra.get("following_count"),
                "privado": extra.get("private"),
                "verificado": extra.get("verified"),
            })

    # Categorias ordenadas de mayor a menor
    categorias_top = dict(contador_categorias.most_common())

    return {
        "tipo": "username",
        "consultado": query,
        "resumen": {
            "cuentas_encontradas": len(cuentas),
            "sitios_revisados": total_revisados,
            "categorias": categorias_top,
        },
        "cuentas": cuentas,
    }



# LIMPIADOR: EMAIL

def _limpiar_email(cruda):
    """
    email: combina clean_profile (cuentas confirmadas) + datos del
    crudo que son valiosos: filtraciones (leakcheck) y PGP (protonmail).
    """
    query = cruda.get("query_value", "")

    # 1) cuentas confirmadas desde clean_profile
    cuentas = []
    for p in (cruda.get("clean_profile", []) or []):
        if p.get("confirmed"):
            extra = p.get("extra", {}) or {}
            cuentas.append({
                "sitio": p.get("site_name", ""),
                "url": (p.get("urls") or [""])[0],
                "metodo_login": extra.get("login_method"),
            })

    # 2) datos del crudo: filtraciones y pgp
    filtraciones = {"encontradas": 0, "fuentes": [], "campos": []}
    usa_pgp = None

    # el crudo puede estar en 'sources' o en 'metadata' segun el tipo
    bloques = list(cruda.get("sources", [])) + list(cruda.get("metadata", []))
    for b in bloques:
        # leakcheck
        if b.get("source") == "leakcheck":
            raw = b.get("raw", {}) or {}
            filtraciones["encontradas"] = raw.get("found", 0)
            filtraciones["fuentes"] = raw.get("sources", []) or []
            filtraciones["campos"] = raw.get("fields", []) or []
        # protonmail
        if b.get("source") == "protonmail":
            raw = b.get("raw", {}) or {}
            usa_pgp = raw.get("has_pgp_key")

    return {
        "tipo": "email",
        "consultado": query,
        "resumen": {
            "cuentas_encontradas": len(cuentas),
            "filtraciones_encontradas": filtraciones["encontradas"],
            "usa_correo_cifrado_pgp": usa_pgp,
        },
        "cuentas": cuentas,
        "filtraciones": filtraciones,
    }



# LIMPIADOR: DOMAIN

def _limpiar_domain(cruda):
    """
    domain: el valor esta en el crudo (registros DNS). Extrae
    subdominios (a_records), servidores de correo (mx), de nombres
    (ns) y verificaciones (txt).
    """
    query = _dominio_limpio(cruda.get("query_value", ""))

    subdominios = []
    servidores_correo = []
    servidores_nombres = []
    verificaciones = []

    for fuente in cruda.get("sources", []):
        data = fuente.get("data", {}) or {}

        # a_records -> subdominios con su ip, pais, proveedor
        for reg in data.get("a_records", []):
            host = reg.get("host", "")
            for ipinfo in (reg.get("ips", []) or []):
                subdominios.append({
                    "subdominio": host,
                    "ip": ipinfo.get("ip"),
                    "pais": ipinfo.get("country"),
                    "proveedor": ipinfo.get("asn_name"),
                })

        # mx_records -> servidores de correo
        for reg in data.get("mx_records", []):
            servidores_correo.append(reg.get("host", ""))

        # ns_records -> servidores de nombres
        for reg in data.get("ns_records", []):
            servidores_nombres.append(reg.get("host", ""))

        # txt_records -> verificaciones (lista de strings)
        for txt in data.get("txt_records", []):
            verificaciones.append(txt)

    # Contar subdominios por pais (dato util del resumen)
    paises = Counter(s["pais"] for s in subdominios if s.get("pais"))

    return {
        "tipo": "domain",
        "consultado": query,
        "resumen": {
            "total_subdominios": len(subdominios),
            "servidores_correo": len(servidores_correo),
            "servidores_nombres": len(servidores_nombres),
            "verificaciones": len(verificaciones),
            "paises": dict(paises.most_common()),
        },
        "subdominios": subdominios,
        "servidores_correo": servidores_correo,
        "servidores_nombres": servidores_nombres,
        "verificaciones": verificaciones,
    }


# LIMPIADOR: IP  (defensivo: estructura aun no confirmada)

def _limpiar_ip(cruda):
    """
    ip: usa el formato CONSERVADOR (estructura completa + resumen
    arriba + solo encontrados), a diferencia de los otros tipos que
    usan formato filtrado/reconstruido.
    Arma primero un resumen legible de la IP (pais, proveedor, riesgo)
    y luego conserva la estructura original sin los nombres de las
    herramientas.
    """
    query = cruda.get("query_value", "")

    # Armamos el resumen legible de la IP
    datos = {}
    for fuente in cruda.get("sources", []):
        d = fuente.get("data", {}) or {}
        if d:
            datos = d
            break

    puntaje_abuso = datos.get("abuse_confidence_score")

    # Interpretamos el nivel de riesgo de forma legible
    if puntaje_abuso is None:
        riesgo = "desconocido"
    elif puntaje_abuso == 0:
        riesgo = "limpia"
    elif puntaje_abuso < 25:
        riesgo = "bajo"
    elif puntaje_abuso < 75:
        riesgo = "medio"
    else:
        riesgo = "alto"

    resumen = {
        "pais": datos.get("country_code"),
        "proveedor": datos.get("isp"),
        "puntaje_abuso": puntaje_abuso,
        "nivel_riesgo": riesgo,
        "total_reportes": datos.get("total_reports", 0),
    }

    # Conservamos la estructura, quitando source_name y filtrando data
    sources_sin_nombre = []
    for fuente in cruda.get("sources", []):
        sources_sin_nombre.append({
            "success": fuente.get("success"),
            "from_cache": fuente.get("from_cache"),
            "data": _filtrar_data(fuente.get("data", {})),
            "error_message": fuente.get("error_message"),
        })

    # metadata: solo el 'raw' de cada bloque
    metadata_solo_raw = []
    for bloque in cruda.get("metadata", []):
        metadata_solo_raw.append({"raw": bloque.get("raw", {})})

    return {
        "resumen": resumen,
        "query_type": cruda.get("query_type"),
        "query_value": query,
        "queried_at": cruda.get("queried_at"),
        "sources": sources_sin_nombre,
        "summary": cruda.get("summary", {}),
        "metadata": metadata_solo_raw,
    }


# DISPATCHER PRINCIPAL

def limpiar_respuesta(cruda):
    """
    Recibe la respuesta CRUDA (dict) de la API de Watson y devuelve
    el resultado LIMPIO (dict) segun el tipo de busqueda.
    """
    if not isinstance(cruda, dict):
        return {"error": "La respuesta cruda no es un objeto valido."}

    tipo = (cruda.get("query_type") or "").lower()

    limpiadores = {
        "username": _limpiar_username,
        "email": _limpiar_email,
        "domain": _limpiar_domain,
        "ip": _limpiar_ip,
    }

    limpiador = limpiadores.get(tipo)
    if limpiador is None:
        return {"error": f"Tipo de busqueda no soportado: {tipo}"}

    return limpiador(cruda)


def limpiar_a_json(cruda, ruta_salida=None):
    """
    Limpia y opcionalmente guarda a un archivo JSON.
    Devuelve el dict limpio.
    """
    limpio = limpiar_respuesta(cruda)
    if ruta_salida:
        with open(ruta_salida, "w", encoding="utf-8") as f:
            json.dump(limpio, f, ensure_ascii=False, indent=2)
    return limpio


