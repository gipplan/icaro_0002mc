import os
import sys
import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from google import genai
from google.genai import types

def extrair_texto_boxnet(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()
        
    texto_limpo = soup.get_text(separator='\n')
    linhas = [line.strip() for line in texto_limpo.splitlines() if line.strip()]
    return "\n".join(linhas)

def carregar_playbook():
    path = "playbook.md"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "Playbook padrão."

def carregar_oportunidades_existentes():
    path = "oportunidades.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def analisar_clipping(url_clipping):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY não configurada.")

    client = genai.Client(api_key=api_key)
    playbook_context = carregar_playbook()
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    print(f"Lendo clipping da Boxnet: {url_clipping}")
    conteudo_clipping = extrair_texto_boxnet(url_clipping)
    print(f"Texto extraído ({len(conteudo_clipping)} caracteres). Enviando ao Gemini...")

    prompt = f"""
    Você é o robô Í.C.A.R.O., central autônoma de PR e inteligência de reputação do iFood.
    Data da análise: {data_hoje}
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.1)
    )

    print(f"Sucesso! Clipping processado.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url_input = sys.argv[1]
        analisar_clipping(url_input)
