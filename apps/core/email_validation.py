"""Validacion de correos con Hunter API.

La validacion es tolerante: bloquea correos confirmados como invalidos, pero
no impide el flujo si Hunter no esta configurado o no responde.
"""

import json
import logging
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings

logger = logging.getLogger(__name__)


class EmailValidationError(Exception):
    """Error recuperable al consultar el servicio externo."""


@dataclass(frozen=True)
class HunterEmailResult:
    email: str
    status: str
    score: int
    disposable: bool = False
    webmail: bool = False

    @property
    def is_deliverable(self) -> bool:
        if self.disposable or self.status == "invalid":
            return False
        if self.status == "unknown" and self.score < 50:
            return False
        return True


class HunterEmailVerifier:
    endpoint = "https://api.hunter.io/v2/email-verifier"

    def __init__(self, api_key=None, timeout=None):
        self.api_key = api_key if api_key is not None else getattr(settings, "HUNTER_API_KEY", "")
        self.timeout = timeout if timeout is not None else getattr(settings, "HUNTER_TIMEOUT_SECONDS", 10)

    def verify(self, email: str) -> HunterEmailResult | None:
        if not getattr(settings, "HUNTER_VALIDATE_EMAILS", True):
            return None
        if not self.api_key:
            logger.warning("HUNTER_API_KEY no configurada; se omite validacion externa de correo")
            return None

        params = urlencode({"email": email, "api_key": self.api_key})
        request = Request(f"{self.endpoint}?{params}", headers={"Accept": "application/json"})

        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            logger.warning("Hunter API respondio HTTP %s al validar %s", exc.code, email)
            raise EmailValidationError("No se pudo validar el correo con Hunter")
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            logger.warning("Error al validar %s con Hunter: %s", email, exc)
            raise EmailValidationError("No se pudo validar el correo con Hunter")

        data = payload.get("data") or {}
        result = HunterEmailResult(
            email=email,
            status=str(data.get("status") or "unknown").lower(),
            score=int(data.get("score") or 0),
            disposable=bool(data.get("disposable")),
            webmail=bool(data.get("webmail")),
        )
        logger.info(
            "Hunter API - %s -> status=%s score=%s disposable=%s webmail=%s",
            email,
            result.status,
            result.score,
            result.disposable,
            result.webmail,
        )
        return result


def is_email_deliverable(email: str) -> bool:
    result = HunterEmailVerifier().verify(email)
    return True if result is None else result.is_deliverable


def validate_email_or_raise(email: str) -> None:
    try:
        if not is_email_deliverable(email):
            raise ValueError("El correo proporcionado no es valido o no existe")
    except EmailValidationError:
        # Politica tolerante: si el servicio falla, no se bloquea la operacion.
        logger.warning("Validacion Hunter omitida por error recuperable para %s", email)
