import re
from typing import Any

from fastapi import Request

SUPPORTED_LANGS = {"es", "en", "ca"}

_ERROR_TRANSLATIONS = {
    "X-Tenant-ID header is required": {
        "es": "Se requiere la cabecera X-Tenant-ID",
        "ca": "Cal la capcalera X-Tenant-ID",
    },
    "Not authenticated": {
        "es": "No autenticado",
        "ca": "No autenticat",
    },
    "Session expired": {
        "es": "Sesion expirada",
        "ca": "Sessio caducada",
    },
    "User not found": {
        "es": "Usuario no encontrado",
        "ca": "Usuari no trobat",
    },
    "Admin role required": {
        "es": "Se requiere rol de administrador",
        "ca": "Cal el rol d'administrador",
    },
    "Permission required": {
        "es": "Permiso requerido",
        "ca": "Permis requerit",
    },
    "CSRF token invalid": {
        "es": "Token CSRF invalido",
        "ca": "Token CSRF invalid",
    },
    "Invalid credentials": {
        "es": "Credenciales invalidas",
        "ca": "Credencials invalides",
    },
    "Tenant mismatch": {
        "es": "Tenant no coincide",
        "ca": "Tenant no coincideix",
    },
    "User disabled": {
        "es": "Usuario deshabilitado",
        "ca": "Usuari deshabilitat",
    },
    "Role already exists": {
        "es": "El rol ya existe",
        "ca": "El rol ja existeix",
    },
    "Role not found": {
        "es": "Rol no encontrado",
        "ca": "Rol no trobat",
    },
    "Update conflict": {
        "es": "Conflicto al actualizar",
        "ca": "Conflicte en actualitzar",
    },
    "Status not found": {
        "es": "Status no encontrado",
        "ca": "Status no trobat",
    },
    "Status already exists": {
        "es": "El status ya existe",
        "ca": "El status ja existeix",
    },
    "Line not found": {
        "es": "Linea no encontrada",
        "ca": "Linia no trobada",
    },
    "Line already exists": {
        "es": "La linea ya existe",
        "ca": "La linia ja existeix",
    },
    "Cell not found": {
        "es": "Celda no encontrada",
        "ca": "Cella no trobada",
    },
    "Cell already exists": {
        "es": "La celda ya existe",
        "ca": "La cella ja existeix",
    },
    "Model not found": {
        "es": "Modelo no encontrado",
        "ca": "Model no trobat",
    },
    "Model already exists": {
        "es": "El modelo ya existe",
        "ca": "El model ja existeix",
    },
    "Invalid date format": {
        "es": "Formato de fecha invalido",
        "ca": "Format de data invalid",
    },
    "Item already exists or FK invalid": {
        "es": "El item ya existe o la FK es invalida",
        "ca": "L'item ja existeix o la FK es invalida",
    },
    "Item not found": {
        "es": "Item no encontrado",
        "ca": "Item no trobat",
    },
    "User already exists or FK invalid": {
        "es": "El usuario ya existe o la FK es invalida",
        "ca": "L'usuari ja existeix o la FK es invalida",
    },
    "Routing not found": {
        "es": "Ruta no encontrada",
        "ca": "Ruta no trobada",
    },
    "Routing already exists": {
        "es": "La ruta ya existe",
        "ca": "La ruta ja existeix",
    },
}

_MIN_LENGTH_RE = re.compile(r"String should have at least (\d+) characters")
_MAX_LENGTH_RE = re.compile(r"String should have at most (\d+) characters")


def _normalize_lang(value: str | None) -> str:
    if not value:
        return "es"
    for part in value.lower().split(","):
        code = part.strip().split(";")[0]
        if code in SUPPORTED_LANGS:
            return code
        if "-" in code:
            base = code.split("-")[0]
            if base in SUPPORTED_LANGS:
                return base
    return "es"


def get_lang(request: Request) -> str:
    return _normalize_lang(request.headers.get("accept-language"))


def translate_error(detail: str, lang: str) -> str:
    if lang == "en":
        return detail
    if detail.startswith("Unknown permissions: "):
        suffix = detail.split(": ", 1)[1]
        prefix = "Permisos desconocidos" if lang == "es" else "Permisos desconeguts"
        return f"{prefix}: {suffix}"
    if detail.startswith("Unknown roles: "):
        suffix = detail.split(": ", 1)[1]
        prefix = "Roles desconocidos" if lang == "es" else "Rols desconeguts"
        return f"{prefix}: {suffix}"
    translated = _ERROR_TRANSLATIONS.get(detail, {})
    return translated.get(lang, detail)


def translate_validation_msg(msg: str, lang: str) -> str:
    if lang == "en":
        return msg
    if msg == "Field required":
        return "Campo requerido" if lang == "es" else "Camp requerit"
    if msg in ("value is not a valid email address", "Input should be a valid email address"):
        return "Email no valido" if lang == "es" else "Email no valid"
    match = _MIN_LENGTH_RE.fullmatch(msg)
    if match:
        limit = match.group(1)
        return (
            f"La cadena debe tener al menos {limit} caracteres"
            if lang == "es"
            else f"La cadena ha de tenir almenys {limit} caracters"
        )
    match = _MAX_LENGTH_RE.fullmatch(msg)
    if match:
        limit = match.group(1)
        return (
            f"La cadena debe tener como maximo {limit} caracteres"
            if lang == "es"
            else f"La cadena ha de tenir com a maxim {limit} caracters"
        )
    return msg


def translate_validation(errors: list[dict[str, Any]], lang: str) -> list[dict[str, Any]]:
    if lang == "en":
        return errors
    translated = []
    for err in errors:
        new_err = dict(err)
        new_err["msg"] = translate_validation_msg(err.get("msg", ""), lang)
        translated.append(new_err)
    return translated
