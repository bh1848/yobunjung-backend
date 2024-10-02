def generate_qr_code(data, qrcode=None):
    """
    사용자의 이메일을 기반으로 QR 코드를 생성
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img_path = f"./qr_codes/{data}.png"
    img.save(img_path)

    return img_path
