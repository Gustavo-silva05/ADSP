import cv2
import pytesseract
import os

pytesseract.pytesseract.tesseract_cmd = (
    r'C:\Program Files\Tesseract-OCR\tesseract.exe'
)

diretorio = os.path.join(os.path.dirname(__file__), 'images')

img_path = r'C:\Users\Gabriel\Downloads\ADSP-main\images\214506\420253_11.jpg'
imagem = cv2.imread(img_path)

sizes_trials = [
    (0, 80, 0, 2000),
    (880, 1010, 0, 2000),
    (1040, 1190, 0, 2000)
]

if imagem is None:
    print("Erro ao carregar a imagem")
    exit()

TARGET_HEIGHT = 1200

h, w = imagem.shape[:2]
scale = TARGET_HEIGHT / h

imagem = cv2.resize(
    imagem,
    None,
    fx=scale,
    fy=scale,
    interpolation=cv2.INTER_CUBIC
)

config_tesseract = '--psm 6'

trials = 0
while trials < len(sizes_trials) + 1:
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    if trials > 0:
        y1, y2, x1, x2 = sizes_trials[trials - 1]
        cinza = cinza[y1:y2, x1:x2]

    if cinza.size == 0:
        trials += 1
        continue

    cinza = cv2.resize(
        cinza,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )

    resultado = pytesseract.image_to_string(
        cinza,
        config=config_tesseract,
        lang='por'
    )

    print(f'--- Trial {trials} ---')
    print(resultado)

    trials += 1