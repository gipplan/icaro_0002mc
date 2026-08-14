import os
import json
import difflib
from datetime import datetime
from google import genai
from google.genai import types

def carregar_playbook():
    path = "playbook.md"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "Playbook padrão não encontrado."

def carregar_oportunidades_existentes():
    path = "oportunidades.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def sao_similares(texto1, texto2, limite=0.70):
    """
    Motor anti-repetição: Calcula a similaridade entre duas strings.
    Se forem mais de 70% iguais, consideramos como a mesma notícia.
    """
    return difflib.SequenceMatcher(None, texto1, texto2).ratio() > limite

def executar_varredura():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY não encontrada.")

    client = genai.Client(api_key=api_key)
    playbook_context = carregar_playbook()
    hoje = datetime.now()
    data_hoje_str = hoje.strftime("%d/%m/%Y")

    prompt = f"""
    Você é o robô Í.C.A.R.O., a central autônoma de inteligência de PR e reputação corporativa do McDonald's (Arcos Dorados) no Brasil.
    Data da varredura: {data_hoje_str}

    DIRETRIZES DO PLAYBOOK CORPORATIVO (SEU CÉREBRO TÁTICO):
    {playbook_context}

    INSTRUÇÕES DE PESQUISA (PRIORIDADE MÁXIMA):
    Faça uma busca na web por notícias recentes no Brasil.
    1. É OBRIGATÓRIO incluir resultados recentes para McDonald's, Arcos Dorados e seus principais concorrentes diretos (ex: Burger King/Zamp). 
    2. Identifique pautas quentes (5 a 10) abrangendo também os setores: QSR (Quick Service Restaurants), Franquias e Varejo Alimentar, Supply Chain/Agronegócio, Empregabilidade Jovem e ESG.
    3. REGRA DE OURO DA DIVERSIDADE: NUNCA repita o mesmo evento ou fato noticioso com títulos diferentes. Cada pauta no JSON deve tratar de um assunto completamente distinto da outra.
    4. Classifique as pautas nas frentes estratégicas (`regulacao`, `franqueados`, `inovacao`, `operacao`, `concorrencia`, `esg`, `crise`).

    DIRETRIZES PARA A TÁTICA SUGERIDA (COMO LER O PLAYBOOK):
    Atue como um Diretor Sênior de Comunicação criativo. Não copie e cole a tática do playbook de forma mecânica. Adapte-a para a realidade específica da notícia. FUJA DO ÓBVIO: NUNCA sugira "fazer press release" ou "postar nas redes". Comece SEMPRE o campo "recomendacao" com um verbo no gerúndio.

    FORMATO DE SAÍDA OBRIGATÓRIO (JSON Puro):
    Retorne uma lista JSON válida com as pautas detectadas.
    [
      {{
        "titulo": "Título conciso e direto",
        "resumo_fato": "Resumo executivo, direto e neutro sobre o fato noticiado.",
        "recomendacao": "Sua tática estratégica baseada nos gatilhos (começando com verbo no gerúndio).",
        "tipo": "regulacao" | "franqueados" | "inovacao" | "operacao" | "concorrencia" | "esg" | "crise",
        "data": "{data_hoje_str}",
        "setor": "Sub-área específica ou veículo",
        "marcas": ["Marcas envolvidas"],
        "produtos": ["Entregáveis recomendados inspirados no playbook"],
        "link_noticia": "URL real da notícia",
        "imagem": ""
      }}
    ]

    ATENÇÃO: Responda APENAS com o código JSON válido.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0.4
        )
    )

    texto_resposta = response.text.strip()
    
    if texto_resposta.startswith("```json"):
        texto_resposta = texto_resposta[7:]
    elif texto_resposta.startswith("```"):
        texto_resposta = texto_resposta[3:]

    if texto_resposta.endswith("```"):
        texto_resposta = texto_resposta[:-3]

    texto_resposta = texto_resposta.strip()

    try:
        novas_pautas = json.loads(texto_resposta)
    except json.JSONDecodeError as e:
        print("Erro ao decodificar JSON retornado pelo Gemini:", e)
        return

    pautas_existentes = carregar_oportunidades_existentes()
    
    # ---------------------------------------------------------
    # MOTOR DE BLOQUEIO POR SIMILARIDADE COM JANELA DE 75 DIAS
    # ---------------------------------------------------------
    textos_recentes = []
    for p in pautas_existentes:
        texto_limpo = f"{p.get('titulo', '')} {p.get('resumo_fato', '')}".strip().lower()
        data_str = p.get("data", "")
        
        try:
            # Converte a data da pauta salva e calcula a diferença de dias
            data_pauta = datetime.strptime(data_str, "%d/%m/%Y")
            diff_dias = (hoje - data_pauta).days
            
            # Se for menor ou igual a 75 dias, entra na lista restritiva
            if diff_dias <= 75:
                textos_recentes.append(texto_limpo)
        except ValueError:
            # Se a data estiver corrompida, adiciona na restrição por segurança
            textos_recentes.append(texto_limpo)

    pautas_adicionadas = 0
    for pauta in novas_pautas:
        texto_novo = f"{pauta.get('titulo', '')} {pauta.get('resumo_fato', '')}".strip().lower()
        
        eh_duplicada = False
        # Compara a nova pauta APENAS com as pautas dos últimos 75 dias
        for txt_ext in textos_recentes:
            if sao_similares(texto_novo, txt_ext, limite=0.70):
                eh_duplicada = True
                print(f"Pauta bloqueada por similaridade (>70% nos últimos 75 dias): {pauta.get('titulo')}")
                break
                
        if not eh_duplicada:
            pautas_existentes.insert(0, pauta)
            # Adiciona o texto novo na lista recente para impedir que a IA repita a mesma pauta no mesmo dia
            textos_recentes.append(texto_novo)
            pautas_adicionadas += 1

    pautas_finais = pautas_existentes[:50]

    with open("oportunidades.json", "w", encoding="utf-8") as f:
        json.dump(pautas_finais, f, ensure_ascii=False, indent=2)

    print(f"Sucesso! Varredura web concluída. {pautas_adicionadas} novas pautas exclusivas adicionadas.")

if __name__ == "__main__":
    executar_varredura()
