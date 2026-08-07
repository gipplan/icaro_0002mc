import os
import json
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

def executar_varredura():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY não encontrada.")

    client = genai.Client(api_key=api_key)
    playbook_context = carregar_playbook()
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    prompt = f"""
    Você é o robô Í.C.A.R.O., a central autônoma de inteligência de PR e reputação corporativa do McDonald's (Arcos Dorados) no Brasil.
    Data da varredura: {data_hoje}

    DIRETRIZES DO PLAYBOOK CORPORATIVO (SEU CÉREBRO TÁTICO):
    {playbook_context}

    INSTRUÇÕES DE PESQUISA (PRIORIDADE MÁXIMA):
    Faça uma busca na web por notícias recentes no Brasil.
    1. É OBRIGATÓRIO incluir resultados recentes para McDonald's, Arcos Dorados e seus principais concorrentes diretos (ex: Burger King). Caso a varredura inicial geral não identifique fatos relevantes sobre essas marcas, execute uma busca adicional e direcionada exclusivamente a elas. O JSON final DEVE conter pautas focadas no ecossistema Arcos Dorados.
    2. Identifique pautas quentes (5 a 10) abrangendo também os setores: QSR (Quick Service Restaurants), Franquias e Varejo Alimentar, Supply Chain/Agronegócio, Empregabilidade Jovem e ESG.
    3. Classifique as pautas nas frentes estratégicas (`regulacao`, `franqueados`, `inovacao`, `operacao`, `concorrencia`, `esg`, `crise`).

    DIRETRIZES PARA A TÁTICA SUGERIDA (COMO LER O PLAYBOOK):
    Atue como um Diretor Sênior de Comunicação criativo e focado em negócios da Arcos Dorados. 
    O Playbook fornecido acima contém Táticas, Formatos e "Gatilhos para a IA". 
    
    COMO AGIR:
    1. ATIVAÇÃO DE GATILHOS: Cruze o contexto da notícia encontrada com os "Gatilhos" do playbook. Se houver match, direcione sua recomendação baseada na tática correspondente do playbook.
    2. CRIATIVIDADE APLICADA: Não copie e cole a tática do playbook de forma mecânica. Adapte-a para a realidade específica da notícia, adicionando a ousadia de um Diretor (pense em Dark Social, PR Stunts B2B/B2C, Fóruns Proprietários, Op-Eds e Advocacy voltado para ESG e Receita do Futuro).
    3. FUJA DO ÓBVIO: NUNCA sugira "fazer press release", "postar nas redes", "monitorar" ou "fazer Q&A".
    4. ESTRUTURA: Comece SEMPRE o campo "recomendacao" com um verbo no gerúndio, justificando o impacto na percepção de marca, expansão de franquias, vendas (Same Store Sales) ou blindagem reputacional.

    FORMATO DE SAÍDA OBRIGATÓRIO (JSON Puro):
    Retorne uma lista JSON válida com as pautas detectadas.
    [
      {{
        "titulo": "Título conciso e direto",
        "resumo_fato": "Resumo executivo, direto e neutro sobre o fato noticiado.",
        "recomendacao": "Sua tática estratégica baseada nos gatilhos (começando com verbo no gerúndio).",
        "tipo": "regulacao" | "franqueados" | "inovacao" | "operacao" | "concorrencia" | "esg" | "crise",
        "data": "{data_hoje}",
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
            temperature=0.3
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
        print("Conteúdo recebido:")
        print(texto_resposta)
        return

    pautas_existentes = carregar_oportunidades_existentes()
    titulos_existentes = {p.get("titulo", "").strip().lower() for p in pautas_existentes}
    
    pautas_adicionadas = 0
    for pauta in novas_pautas:
        titulo_limpo = pauta.get("titulo", "").strip().lower()
        if titulo_limpo not in titulos_existentes:
            pautas_existentes.insert(0, pauta)
            titulos_existentes.add(titulo_limpo)
            pautas_adicionadas += 1

    pautas_finais = pautas_existentes[:50]

    with open("oportunidades.json", "w", encoding="utf-8") as f:
        json.dump(pautas_finais, f, ensure_ascii=False, indent=2)

    print(f"Sucesso! Varredura web concluída. {pautas_adicionadas} novas pautas adicionadas.")

if __name__ == "__main__":
    executar_varredura()
