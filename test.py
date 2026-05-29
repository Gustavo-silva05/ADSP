import cv2
import pytesseract
import os
import numpy as np

sizes_trials = [
    (0, 70, 0, 1000),       # Trial 1: Parte superior
    (850, 950, 0, 950),     # Trial 2: Parte inferior para imagem menor
    (1080, 1160, 0, 1100)   # Trial 3: Parte inferior
]

diretorio = os.path.join(os.path.dirname(__file__), 'images')
img = '12345MFS10100-052882-2409021728480332.jpg'
img_path = os.path.join(diretorio, img)
imagem = cv2.imread(img_path)

trials = 0
if imagem is not None:
    while trials < len(sizes_trials)+1:
        cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        
        ##
        cinza_invertido = cv2.bitwise_not(cinza)
        
        # 2. Ênfase de bordas (Filtro de Nitidez / Sharpening)
        kernel_sharpening = np.array([[-1, -1, -1],
                                      [-1,  9, -1],
                                      [-1, -1, -1]])
        cinza_realcado = cv2.filter2D(cinza_invertido, -1, kernel_sharpening)
        
        # 3. Binarização Otsu (Força contraste máximo para o OCR)
        _, imagem_final = cv2.threshold(cinza_realcado, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        ##
        cinza = imagem_final
        if trials > 0 and trials <= len(sizes_trials):
            y1, y2, x1, x2 = sizes_trials[trials - 1]
            cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
            cinza = cinza[y1:y2, x1:x2]
        config_tesseract = '--psm 6'
        resultado = pytesseract.image_to_string(cinza, config=config_tesseract, lang='por')
        cv2.imshow(f'trial {trials}', cinza)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        print(resultado)
        trials += 1
else:
    print("Erro ao carregar a imagem")