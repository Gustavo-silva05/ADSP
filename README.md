# Sistema de Extração Automatizada de Dados de Radar

Desenvolvido por Gabriel Dorneles Rebello e Gustavo Souza da Silva — PUCRS, em parceria com a LABELO.

Este sistema processa automaticamente imagens de autuações de radar de trânsito e extrai os dados de velocidade, data e hora de cada registro, exportando tudo para um arquivo CSV.

---

## Requisitos

### 1. Python

Instale o Python 3.10 ou superior a partir do site oficial:
https://www.python.org/downloads/

Durante a instalação, marque a opção **"Add Python to PATH"**.

Para verificar se a instalação foi bem-sucedida, abra o Prompt de Comando e execute:

```
python --version
```

### 2. Tesseract OCR

O Tesseract é o motor de reconhecimento de texto utilizado pelo sistema. Instale a versão para Windows disponível em:
https://github.com/UB-Mannheim/tesseract/wiki

Durante a instalação, anote o caminho onde o Tesseract foi instalado. O padrão é:

```
C:\Program Files\Tesseract-OCR\tesseract.exe
```

Se a instalação foi feita em outro local (por exemplo, na pasta do usuário), será necessário ajustar o código conforme descrito na seção de configuração abaixo.

Certifique-se também de que o pacote de idioma **Português** (`por`) está instalado. Durante o instalador do Tesseract, selecione "Additional language data" e marque o português.

### 3. Bibliotecas Python

Com o Python instalado, abra o Prompt de Comando e execute o seguinte comando para instalar todas as dependências necessárias:

```
pip install opencv-python pytesseract
```

---

## Configuração

Antes de executar o sistema, é necessário verificar dois pontos no arquivo `main.py`:

### Caminho do Tesseract

Abra o arquivo `main.py` em qualquer editor de texto (o Bloco de Notas funciona). Localize a linha:

```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

Se o Tesseract foi instalado em um caminho diferente no seu computador, substitua o trecho entre aspas pelo caminho correto. Por exemplo:

```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\SeuUsuario\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
```

### Pasta de imagens

O sistema lê as imagens a partir de uma pasta chamada `images` localizada no mesmo diretório que o arquivo `main.py`. Crie essa pasta caso ela não exista e coloque as imagens de radar dentro dela.

A estrutura de pastas deve ficar assim:

```
pasta-do-projeto/
    main.py
    images/
        imagem1.jpg
        imagem2.jpg
        ...
```

As imagens podem estar em subpastas dentro de `images` — o sistema as encontra automaticamente.

Formatos de imagem suportados: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`, `.tiff`

---

## Como executar

1. Abra o Prompt de Comando
2. Navegue até a pasta onde o arquivo `main.py` está salvo. Por exemplo:

```
cd C:\Users\SeuUsuario\Desktop\radar
```

3. Execute o script:

```
python main.py
```

O sistema exibirá o progresso no terminal conforme processa cada imagem. Ao final, uma mensagem indicará o tempo total de processamento.

---

## Resultado

Após a execução, uma pasta chamada `output` será criada automaticamente no mesmo diretório do script. Dentro dela estará o arquivo:

```
resultados.csv
```

Este arquivo pode ser aberto diretamente no Excel. Ele contém as seguintes colunas:

| Coluna | Descrição |
|---|---|
| Arquivo | Nome do arquivo de imagem processado |
| Data | Data da autuação extraída da imagem |
| Hora | Hora da autuação extraída da imagem |
| Vel_Regulamentada (Km/h) | Velocidade máxima permitida no local |
| Vel_Medida (Km/h) | Velocidade medida pelo radar |
| Vel_Considerada (Km/h) | Velocidade considerada para fins de autuação |
| Erro | Vazio se a extração foi completa; "Resultado parcial" se algum campo não foi encontrado |

Registros com a coluna "Erro" preenchida indicam imagens que precisam de revisão manual.

---

## Dúvidas frequentes

**O sistema está retornando erro "tesseract is not installed or not in PATH"**
O caminho do Tesseract no arquivo `main.py` está incorreto. Verifique onde o Tesseract foi instalado e atualize a linha correspondente conforme descrito na seção de configuração.

**O sistema não encontrou nenhuma imagem**
Verifique se a pasta `images` existe e está no mesmo diretório que o arquivo `main.py`, e se as imagens estão em um formato suportado.

**Algumas linhas do CSV estão com "Resultado parcial"**
Isso ocorre em imagens com qualidade de impressão degradada ou layout atípico. Esses registros devem ser revisados manualmente.
