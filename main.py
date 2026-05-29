import cv2
import pytesseract
import re
import os
import csv
from concurrent.futures import ProcessPoolExecutor

diretorio = os.path.join(os.path.dirname(__file__), 'images')
output_dir = './output'
os.makedirs(output_dir, exist_ok=True)
csv_path = os.path.join(output_dir, 'resultados.csv')

extensoes_suportadas = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff')
arquivos = [f for f in os.listdir(diretorio) if f.lower().endswith(extensoes_suportadas)]
arquivos.sort(key=lambda x: x.lower())

def processar_imagem(arquivo):
    img_path = os.path.join(diretorio, arquivo)
    imagem = cv2.imread(img_path)
    
    print(f"--- Processando: {arquivo} ---")
    
    if imagem is None:
        return {"Arquivo": arquivo, "Erro": "Erro ao carregar a imagem"}

    trials = 0
    while trials < 3:
        cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        
        if trials == 1:
            cinza = cinza[580:580+60, 0:600]
        elif trials == 2:
            cinza = cinza[570:570+70, 0:950]
        
        if cinza.size == 0:
            trials += 1
            continue
        
        config_tesseract = '--psm 6'
        resultado = pytesseract.image_to_string(cinza, config=config_tesseract, lang='por')
        linhas = [linha.upper().replace('.','') for linha in resultado.split('\n') if linha.strip()]

        try:
            for linha in linhas:
                dados_parseados = {
                    "Arquivo": arquivo,
                    "Data": m.group(1) if (m := re.search(r'DATA:\s*([\d/]+)', linha)) else None,
                    "Hora": m.group(1) if (m := re.search(r'HORA:\s*([\dHMINS]+)', linha)) else None,
                    "Vel_Regulamentada": m.group(1) if (m := re.search(r'VEL REG:\s*(\d+\s*KM/H)', linha)) else (m.group(1) if (m := re.search(r'VELMAX:\s*(\d+\s*KM[A-Z/]*)', linha)) else None),
                    "Vel_Medida": m.group(1) if (m := re.search(r'VEL MEDIDA:\s*(\d+\s*KM/H)', linha)) else (m.group(1) if (m := re.search(r'VELMED:\s*(\d+\s*KM[A-Z/]*)', linha)) else None),
                    "Vel_Considerada": m.group(1) if (m := re.search(r'VELCONSIDERADA:\s*(\d+\s*KM/H)', linha)) else (m.group(1) if (m := re.search(r'VELCONSID:\s*(\d+\s*KM[A-Z/]*)', linha)) else None),
                    "Erro": None
                }
                
                if dados_parseados["Vel_Regulamentada"] or dados_parseados["Vel_Medida"] or dados_parseados["Vel_Considerada"]:
                    cv2.imwrite(f'{output_dir}/trial{trials}_{arquivo}.jpg', cinza)
                    return dados_parseados
            
            if trials == 2:
                return {
                    "Arquivo": arquivo, "Data": None, "Hora": None, 
                    "Vel_Regulamentada": None, "Vel_Medida": None, 
                    "Vel_Considerada": None, "Erro": 'Dados não encontrados'
                }
                
        except Exception:
            pass
        finally:
            trials += 1
            
    return None


if __name__ == "__main__":
    if not arquivos:
        print(f"Nenhuma imagem encontrada no diretório: {diretorio}")
    else:
        dados_finais = []
        
        with ProcessPoolExecutor(max_workers=5) as executor:
            resultados = executor.map(processar_imagem, arquivos)
            
            for resultado in resultados:
                if resultado:
                    dados_finais.append(resultado)

        print("\nProcessamento finalizado.")

        if dados_finais:
            dados_finais.sort(key=lambda x: x["Arquivo"])
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                campos = ["Arquivo", "Data", "Hora", "Vel_Regulamentada", "Vel_Medida", "Vel_Considerada", "Erro"]
                
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                writer.writerows(dados_finais)
                
            print(f"Resultados salvos em: {csv_path}")