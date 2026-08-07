# I.C.A.R.O. - Arcos Dorados PR Intelligence Hub

Este repositório contém o sistema de Inteligência de PR e Reputação corporativa da **Arcos Dorados (McDonald's)** no Brasil. 

O Í.C.A.R.O. atua como um radar autônomo, varrendo a web em busca de notícias sobre a marca, concorrência (QSR) e setor de franquias, utilizando Inteligência Artificial (Gemini) para cruzar esses fatos com o playbook estratégico da companhia e sugerir táticas de Relações Públicas em tempo real.

## 🏗️ Estrutura do Projeto

*   **`index.html`**: O Dashboard visual de monitoramento (Vitrine), onde a liderança visualiza as pautas quentes, filtradas por frentes como *Receita do Futuro*, *Franqueados* e *Inovação*.
*   **`admin.html` / `busca.html`**: Painéis de controle em Modo DEV para acionamento manual do motor de busca e processamento de clipping via Boxnet.
*   **`gerar_oportunidades.py`**: O "Motor" do sistema. Script em Python executado via GitHub Actions que realiza as varreduras, consome a API do Gemini e consolida os dados.
*   **`playbook.md`**: O "Cérebro Tático". Documento Markdown contínuo que contém as regras de compliance, tom de voz e os *Gatilhos de IA* extraídos dos feedbacks da diretoria.
*   **`oportunidades.json`**: O banco de dados alimentado automaticamente pelo motor com as pautas estruturadas.

## 🚀 Como Funciona o Fluxo (RLHF)

1. O Motor (`gerar_oportunidades.py`) caça as notícias e consulta o `playbook.md` para saber como agir.
2. O Dashboard exibe as notícias e recomendações táticas.
3. A equipe de PR consome os dados e envia feedbacks (áudios/transcrições).
4. Uma GEM (IA configurada separadamente) processa esses feedbacks e atualiza o `playbook.md` com novas diretrizes de tom e compliance.
5. O ciclo recomeça, tornando o sistema cada vez mais inteligente e alinhado aos objetivos de negócio da Arcos Dorados.
