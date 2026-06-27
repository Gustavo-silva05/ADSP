import cv2
import pytesseract
import re
import os
import csv
import time
from concurrent.futures import ProcessPoolExecutor

def resultado_valido(dados):
    try:
        reg = int(dados["Vel_Regulamentada (Km/h)"])
        med = int(dados["Vel_Medida (Km/h)"])
        cons_raw = dados.get("Vel_Considerada (Km/h)")
        cons = int(cons_raw) if cons_raw else None

        if med < reg:
            return False  
        if cons is not None:
            if cons > med:
                return False 
            if cons < reg:
                return False  
        return True
    except (ValueError, TypeError):
        return False

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# pytesseract.pytesseract.tesseract_cmd = r'C:\Users\g.rebello\AppData\Local\Programs\Tesseract-OCR\tesseract.exe' 
# os.environ['TESSDATA_PREFIX'] = r'C:\Users\g.rebello\AppData\Local\Programs\Tesseract-OCR\tessdata'

diretorio = os.path.join(os.path.dirname(__file__), 'images')
output_dir = './output'
os.makedirs(output_dir, exist_ok=True)
csv_path = os.path.join(output_dir, 'resultados.csv')

extensoes_suportadas = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff')

arquivos_com_caminho = []
for raiz, diretorios, arquivos_nomes in os.walk(diretorio):
    for f in arquivos_nomes:
        if f.lower().endswith(extensoes_suportadas):
            caminho_relativo = os.path.relpath(os.path.join(raiz, f), diretorio)
            arquivos_com_caminho.append(caminho_relativo)

arquivos_com_caminho.sort(key=lambda x: x.lower())

sizes_trials = [
    (1040, 1190, 0, 2000),
    (880, 1010, 0, 2000),
    (0, 80, 0, 2000)
]

def processar_imagem(arquivo):
    img_path = os.path.join(diretorio, arquivo)
    imagem = cv2.imread(img_path)
    
    if imagem is None:
        return {"Arquivo": arquivo, "Erro": "Erro ao carregar a imagem"}

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

    print(f"--- Processando: {arquivo} ---")
    
    trials = 0

    dados_parseados = {
        "Arquivo": arquivo,
        "Data": None,
        "Hora": None,
        "Vel_Regulamentada (Km/h)": None,
        "Vel_Medida (Km/h)": None,
        "Vel_Considerada (Km/h)": None,
        "Erro": None
    }

    ultimo_parcial = None
    
    while trials < len(sizes_trials)+1:

        cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        
        if trials > 0 and trials <= len(sizes_trials):
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
        config_tesseract = '--psm 6'
        resultado = pytesseract.image_to_string(cinza, config=config_tesseract, lang='por')
        linhas = [
            ''.join(linha.upper().replace('.', '').split())
            for linha in resultado.split('\n')
            if linha.strip()
        ]

        try:
            for linha in linhas:
                if not dados_parseados["Data"]:
                    m = re.search(r'DATA:\s*([\d/]+)', linha)
                    if m:
                        dados_parseados["Data"] = m.group(1)

                if not dados_parseados["Hora"]:
                    m = re.search(r'HORA:\s*([\dHMINS]+)', linha)
                    if m:
                        dados_parseados["Hora"] = m.group(1)

                if not dados_parseados["Vel_Regulamentada (Km/h)"]:
                    m = re.search(r'VELREG[^0-9]*(\d+)', linha)
                    if not m:
                        m = re.search(r'VELMAX[^0-9]*(\d+)', linha)
                    if m:
                        dados_parseados["Vel_Regulamentada (Km/h)"] = m.group(1)

                if not dados_parseados["Vel_Medida (Km/h)"]:
                    m = re.search(r'VELMEDIDA[^0-9]*(\d+)', linha)
                    if not m:
                        m = re.search(r'VELMED[^0-9]*(\d+)', linha)
                    if m:
                        dados_parseados["Vel_Medida (Km/h)"] = m.group(1)

                if not dados_parseados["Vel_Considerada (Km/h)"]:
                    m = re.search(r'VELCONSIDERADA[^0-9]*(\d+)', linha)
                    if not m:
                        m = re.search(r'VELCONSID[^0-9]*(\d+)', linha)
                    if m:
                        dados_parseados["Vel_Considerada (Km/h)"] = m.group(1)

                if dados_parseados["Vel_Regulamentada (Km/h)"] and dados_parseados["Vel_Medida (Km/h)"] and dados_parseados["Data"] and dados_parseados["Hora"]:
                    if resultado_valido(dados_parseados):
                        return dados_parseados
                    else:
                        if (
                            dados_parseados["Vel_Regulamentada (Km/h)"] or
                            dados_parseados["Vel_Medida (Km/h)"] or
                            dados_parseados["Vel_Considerada (Km/h)"]
                        ):
                            ultimo_parcial = dados_parseados.copy()

                        dados_parseados["Vel_Regulamentada (Km/h)"] = None
                        dados_parseados["Vel_Medida (Km/h)"] = None
                        dados_parseados["Vel_Considerada (Km/h)"] = None

            if trials == len(sizes_trials):
                if ultimo_parcial:
                    ultimo_parcial["Erro"] = "Resultado parcial"
                    return ultimo_parcial

                dados_parseados["Erro"] = "Dados não encontrados"
                return dados_parseados
                
        except Exception as e:
            print(f"Erro em {arquivo}: {e}")
        finally:
            trials += 1
            
    return None


if __name__ == "__main__":
    start_time = time.perf_counter()
    if not arquivos_com_caminho:
        print(f"Nenhuma imagem encontrada no diretório: {diretorio}")
    else:
        dados_finais = []
        cpus = os.cpu_count() - 2 if os.cpu_count() > 2 else 1
        print(f"Total de imagens a processar: {len(arquivos_com_caminho)} - CPUS disponíveis: {cpus}")
        with ProcessPoolExecutor(max_workers=cpus) as executor:
            resultados = executor.map(processar_imagem, arquivos_com_caminho)
            
            for resultado in resultados:
                if resultado:
                    dados_finais.append(resultado)

        print("\nProcessamento finalizado.")

        if dados_finais:
            dados_finais.sort(key=lambda x: x["Arquivo"])
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                campos = ["Arquivo", "Data", "Hora", "Vel_Regulamentada (Km/h)", "Vel_Medida (Km/h)", "Vel_Considerada (Km/h)", "Erro"]
                
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                writer.writerows(dados_finais)
                
            print(f"Resultados salvos em: {csv_path}")

        end_time = time.perf_counter()
        print(f"Tempo total de processamento: {end_time - start_time:.2f} segundos")
