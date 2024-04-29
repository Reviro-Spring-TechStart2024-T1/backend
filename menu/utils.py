from io import BytesIO

import qrcode


def generate_qr_code(data):
    """
    Generate a QR code image from given data and return it as a BytesIO object.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill='black', back_color='white')

    # Save QR code to a BytesIO buffer and return it
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer
