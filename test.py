import cv2
import pytesseract
import os

pytesseract.pytesseract.tesseract_cmd = (
    r'C:\Program Files\Tesseract-OCR\tesseract.exe'
)

diretorio = os.path.join(os.path.dirname(__file__), 'images')
img = '12345MFR10100-263174-2409070746140332.jpg'

img_path = os.path.join(diretorio, img)
imagem = cv2.imread(img_path)

if imagem is None:
    print("Erro ao carregar a imagem")
    exit()

# ==========================================================
# NORMALIZA TODAS AS IMAGENS PARA A MESMA ALTURA
# ==========================================================

TARGET_HEIGHT = 1200

h_original, w_original = imagem.shape[:2]

scale = TARGET_HEIGHT / h_original

imagem = cv2.resize(
    imagem,
    None,
    fx=scale,
    fy=scale,
    interpolation=cv2.INTER_CUBIC
)

h, w = imagem.shape[:2]

print(f"\nOriginal : {w_original}x{h_original}")
print(f"Resize   : {w}x{h}")

cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

# ==========================================================
# TRIAL 0 - IMAGEM COMPLETA
# ==========================================================

trials = [
    ("FULL", cinza),

    (
        "TOP",
        cinza[
            int(h * 0.00):int(h * 0.08),
            :
        ]
    ),

    (
        "BOTTOM_1",
        cinza[
            int(h * 0.74):int(h * 0.84),
            :
        ]
    ),

    (
        "BOTTOM_2",
        cinza[
            int(h * 0.90):int(h * 0.99),
            :
        ]
    )
]

for nome, crop in trials:

    print("\n" + "=" * 80)
    print(nome)
    print("=" * 80)

    if crop.size == 0:
        print("Crop vazio")
        continue

    # ======================================================
    # UPSCALE 3X
    # ======================================================

    crop_up = cv2.resize(
        crop,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )

    resultado = pytesseract.image_to_string(
        crop_up,
        config='--psm 6',
        lang='por'
    )

    print(resultado)