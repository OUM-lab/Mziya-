"""Service de génération des QR codes personnels Mziya."""

from io import BytesIO
from typing import Optional

from utils.formatting import format_client_qr_id


def get_client_qr_payload(user_id: int, existing_qr_code: Optional[str] = None) -> str:
    """Retourne uniquement l'identifiant non sensible du client (ex: MZIYA-CLIENT-0001)."""
    if existing_qr_code and existing_qr_code.startswith("MZIYA-CLIENT-"):
        return existing_qr_code
    return format_client_qr_id(user_id)


def generate_qr_image_bytes(qr_payload: str) -> bytes:
    """Génère une image PNG du QR code à partir d'un identifiant non sensible."""
    import qrcode
    from PIL import Image

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(qr_payload)
    qr.make(fit=True)
    img: Image.Image = qr.make_image(fill_color="#0F2942", back_color="white").convert(
        "RGB"
    )

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
