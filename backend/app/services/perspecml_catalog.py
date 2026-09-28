"""Catálogo PerSpecML — perspectivas, tarefas, concerns e stakeholders.

Fonte: Villamizar, Kalinowski, Lopes, Mendez. "Identifying concerns when
specifying machine learning-enabled systems: A perspective-based approach".
Journal of Systems and Software 213 (2024) 112053.
https://doi.org/10.1016/j.jss.2024.112053

- 5 perspectivas (ordem de análise do workflow da Fig. 5): O, U, I, M, D.
- 28 tarefas (Tabelas 1–5), cada uma com os stakeholders sugeridos (Fig. 2).
- 60 concerns (Tabelas 6–10). ``related`` são as relações entre concerns
  indicadas entre colchetes na Fig. 2 (o paper as trata como influências a
  considerar na análise; aqui ficam simétricas via ``related_map()``).
- ``experimental`` marca tarefas com o selo 'E' do template (Fig. 3/4):
  concerns dessas tarefas tendem a ser refinados durante a experimentação.
- Perguntas, dicas, itens a considerar e exemplos vêm do template publicado
  no Miro (`perspecml_template`); ``question_source`` indica se a pergunta é
  do template ou adaptada aqui (concerns que o template não cobre).

O catálogo é dado estático e versionado (CATALOG_VERSION): as especificações
guardam a versão com que foram criadas.
"""

from __future__ import annotations

from functools import lru_cache

from backend.app.services.perspecml_template import GOALS, TEMPLATE
from backend.app.services.perspecml_template import SOURCE as TEMPLATE_SOURCE

CATALOG_ID = "perspecml"
CATALOG_VERSION = "2024.2"

STAKEHOLDERS = [
    {
        "id": "BO",
        "name": "Dono do negócio",
        "description": "Entende quais propriedades são essenciais para os objetivos de negócio "
        "e as capacidades do ML, para fixar metas e expectativas realistas.",
    },
    {
        "id": "DE",
        "name": "Especialista de domínio",
        "description": "Define o problema de acordo com o cenário real, ajuda a escolher "
        "features e fontes de dados e a interpretar os resultados do modelo.",
    },
    {
        "id": "DG",
        "name": "Designer",
        "description": "Traduz conceitos e saídas do modelo em interfaces intuitivas "
        "que gerem valor para os usuários finais.",
    },
    {
        "id": "SE",
        "name": "Engenheiro(a) de software/ML",
        "description": "Transforma protótipos em sistemas que lidam com dados em escala, "
        "com escalabilidade e desempenho; decide como o modelo é servido.",
    },
    {
        "id": "DS",
        "name": "Cientista de dados",
        "description": "Analisa dados e desenvolve os modelos, considerando as restrições "
        "que o sistema impõe ao modelo.",
    },
    {
        "id": "RE",
        "name": "Engenheiro(a) de requisitos",
        "description": "Conduz a especificação: facilita a discussão entre os stakeholders "
        "e ajuda a resolver conflitos e trade-offs entre concerns.",
    },
]

# Cada perspectiva: tarefas -> concerns. Concern: (id, nome, "especificar ..."
# (Tabelas 6–10), pergunta adaptada, relacionados). A pergunta adaptada só é
# usada quando o template do Miro não traz pergunta para o concern.
_P = [
    {
        "id": "O",
        "name": "Objetivos do sistema",
        "color": "#8fd3c9",
        "description": "Analisa o contexto e o problema que o ML vai resolver, os benefícios "
        "mensuráveis esperados para a organização e os usuários, as metas do sistema e do "
        "modelo e o trade-off de ML em relação às expectativas do cliente.",
        "tasks": [
            {
                "id": "O.1",
                "name": "Entender o problema",
                "description": "Entender o domínio e o contexto real em que o modelo será "
                "implantado, e definir o problema de ML e a tarefa específica a resolver.",
                "stakeholders": ["BO", "DE", "DS"],
                "concerns": [
                    ("O1", "Contexto",
                     "as circunstâncias, o ambiente ou as condições em que o sistema com ML vai operar.",
                     "Em que contexto (ambiente, circunstâncias, restrições do domínio) o sistema com ML vai operar?",
                     ["M13", "M14"]),
                    ("O2", "Necessidade",
                     "a necessidade, o desejo ou a lacuna a ser atendida naquele contexto.",
                     "Qual necessidade ou lacuna o sistema precisa resolver nesse contexto?",
                     []),
                    ("O3", "Funcionalidade de ML",
                     "a natureza do problema de aprendizado e o resultado que o modelo deve alcançar (ex.: classificar clientes).",
                     "Qual é o problema de aprendizado (classificação, regressão, recomendação...) e o que o modelo deve produzir?",
                     ["M1", "M5"]),
                    ("O4", "Hipótese de lucro",
                     "como os resultados do sistema se traduzem em ganhos concretos para a organização.",
                     "Como as saídas do modelo vão gerar ganho concreto para a organização?",
                     ["O5", "O9"]),
                ],
            },
            {
                "id": "O.2",
                "name": "Definir metas em diferentes níveis",
                "description": "Definir metas do projeto em diferentes níveis para garantir que "
                "atendam às expectativas dos stakeholders.",
                "stakeholders": ["BO", "DE", "DS"],
                "concerns": [
                    ("O5", "Metas organizacionais",
                     "benefícios mensuráveis que o ML deve trazer à organização (ex.: aumentar a receita em X%).",
                     "Quais benefícios mensuráveis a organização espera (ex.: +X% de receita, −Y% de churn)?",
                     []),
                    ("O6", "Metas do sistema",
                     "o que o sistema busca alcançar, com o apoio do modelo, em termos de comportamento ou qualidade.",
                     "Que comportamento ou qualidade o sistema como um todo deve alcançar com o apoio do modelo?",
                     []),
                    ("O7", "Metas dos usuários",
                     "o que os usuários querem alcançar usando o ML.",
                     "O que os usuários querem conseguir ao usar a funcionalidade de ML?",
                     []),
                    ("O8", "Metas do modelo",
                     "métricas e valores aceitáveis que o modelo deve atingir (ex.: acurácia > X%, precisão > Y%).",
                     "Quais métricas e limiares o modelo deve atingir (ex.: acurácia > X%, recall > Z%)?",
                     []),
                ],
            },
            {
                "id": "O.3",
                "name": "Estabelecer indicadores de sucesso",
                "description": "Definir medidas que deem sinais antecipados do alcance dos objetivos.",
                "stakeholders": ["BO"],
                "concerns": [
                    ("O9", "Indicadores antecedentes",
                     "medidas que se correlacionam com o sucesso futuro, na visão do negócio (ex.: sentimento e engajamento).",
                     "Quais indicadores antecipam o sucesso do ponto de vista do negócio (engajamento, sentimento...)?",
                     []),
                ],
            },
            {
                "id": "O.4",
                "name": "Gerenciar expectativas",
                "description": "Definir o que o modelo pode e não pode fazer, evitando expectativas "
                "irreais sobre as capacidades do ML.",
                "stakeholders": ["BO", "DE", "DS"],
                "concerns": [
                    ("O10", "Trade-off de ML",
                     "o equilíbrio das expectativas do cliente (ex.: tempo de inferência vs. acurácia, falso positivo vs. falso negativo).",
                     "Que trade-offs são aceitáveis (tempo de inferência vs. acurácia, falso positivo vs. falso negativo)?",
                     ["M5", "M7", "M11", "M12", "D5", "I2", "I11"]),
                ],
            },
        ],
    },
    {
        "id": "U",
        "name": "Experiência do usuário",
        "color": "#f7b8ad",
        "description": "Apresenta as predições aos usuários de modo que alcancem os objetivos "
        "do sistema e gerem feedback para melhorar o modelo: valor percebido, força e frequência "
        "da interação, visualização, feedback e impacto de uma predição errada.",
        "tasks": [
            {
                "id": "U.1",
                "name": "Estabelecer o valor das predições",
                "description": "Determinar se as saídas do modelo são relevantes, corretas e "
                "impactantes e como contribuem para os objetivos do projeto.",
                "stakeholders": ["BO", "DG"],
                "concerns": [
                    ("U1", "Valor",
                     "o valor agregado percebido pelos usuários a partir das predições.",
                     "Que valor o usuário percebe nas predições? O que muda no trabalho dele?",
                     []),
                ],
            },
            {
                "id": "U.2",
                "name": "Definir a interação das predições com os usuários",
                "description": "Definir como os usuários vão interagir com as predições (frequência, "
                "força) para desenhar interfaces e fluxos adequados.",
                "stakeholders": ["DG", "BO"],
                "concerns": [
                    ("U2", "Força da interação",
                     "o quanto o sistema força o usuário a seguir o que o modelo indica (ações automáticas ou assistidas).",
                     "A predição executa uma ação automaticamente ou apenas sugere/assiste o usuário?",
                     []),
                    ("U3", "Frequência",
                     "com que frequência o sistema interage com os usuários (a pedido ou quando o sistema julga que o usuário vai responder).",
                     "Quando e com que frequência a predição aparece para o usuário?",
                     []),
                ],
            },
            {
                "id": "U.3",
                "name": "Visualizar predições",
                "description": "Apresentar as saídas do modelo em formato compreensível (gráficos, "
                "painéis).",
                "stakeholders": ["DG"],
                "concerns": [
                    ("U4", "Visualização",
                     "interfaces para exibir as saídas do modelo e integrá-las aos sistemas do cliente (dashboards, protótipos).",
                     "Como as predições serão exibidas (dashboards, protótipos) e integradas aos sistemas existentes?",
                     []),
                ],
            },
            {
                "id": "U.4",
                "name": "Coletar feedback de aprendizado dos usuários",
                "description": "Oferecer mecanismos de feedback para atualizar o modelo.",
                "stakeholders": ["SE", "DG"],
                "concerns": [
                    ("U5", "Feedback de aprendizado",
                     "as interações que fornecerão novos dados para aprendizado, ou human-in-the-loop.",
                     "Como o usuário vai fornecer novos dados/rótulos ao sistema? Há humano no loop?",
                     ["I3"]),
                ],
            },
            {
                "id": "U.5",
                "name": "Garantir a credibilidade das predições",
                "description": "Garantir que os usuários entendam as capacidades e as possíveis "
                "imprecisões do modelo.",
                "stakeholders": ["BO", "DS"],
                "concerns": [
                    ("U6", "Aceitação",
                     "o quão bem e como o modelo chega às suas decisões.",
                     "O que é preciso para que os usuários aceitem as decisões do modelo?",
                     ["M5", "M11", "M13"]),
                    ("U7", "Responsabilização",
                     "quem é responsável por resultados inesperados do modelo.",
                     "Quem responde por resultados inesperados ou errados do modelo?",
                     []),
                    ("U8", "Custo do erro",
                     "o impacto, para o usuário, de uma predição errada.",
                     "Qual é o impacto para o usuário de uma predição errada?",
                     []),
                    ("U9", "Educação e treinamento",
                     "a necessidade de educar os usuários sobre as limitações do sistema e como interpretar suas saídas.",
                     "Os usuários precisam de treinamento sobre as limitações do modelo e a interpretação das saídas?",
                     ["O10"]),
                ],
            },
        ],
    },
    {
        "id": "I",
        "name": "Infraestrutura",
        "color": "#f9dc8a",
        "description": "Cobre a execução do modelo, o monitoramento de dados e saídas e o "
        "aprendizado com novos dados: streaming, serving, armazenamento de artefatos, "
        "automação (MLOps), integração com o restante do sistema e custo.",
        "tasks": [
            {
                "id": "I.1",
                "name": "Transportar dados até o modelo",
                "description": "Levar os dados relevantes da origem até o modelo para análise, "
                "treino ou predição.",
                "stakeholders": ["SE"],
                "concerns": [
                    ("I1", "Streaming de dados",
                     "a estratégia de transporte de dados (ex.: tempo real ou em lotes).",
                     "Os dados chegam ao modelo em tempo real ou em lotes? Por qual mecanismo?",
                     ["M7", "M12", "D14", "I3"]),
                ],
            },
            {
                "id": "I.2",
                "name": "Disponibilizar o modelo",
                "description": "Implantar e expor o modelo treinado para que possa ser usado nas predições.",
                "stakeholders": ["SE", "DS"],
                "concerns": [
                    ("I2", "Serving do modelo",
                     "como o modelo será executado e consumido (client-side, back-end, nuvem, endpoint de web service).",
                     "Onde e como o modelo será executado e consumido (cliente, back-end, nuvem, API)?",
                     ["I11"]),
                ],
            },
            {
                "id": "I.3",
                "name": "Atualizar o modelo",
                "description": "Melhorar ou modificar um modelo existente para aprimorar seu desempenho.",
                "stakeholders": ["SE", "DS"],
                "concerns": [
                    ("I3", "Aprendizado incremental",
                     "a capacidade de aprender continuamente com novos dados, estendendo o conhecimento do modelo.",
                     "O modelo precisa aprender continuamente com novos dados? Com que gatilho e frequência?",
                     ["U6", "D6", "D7", "D8", "D9", "D10", "D11", "D12"]),
                ],
            },
            {
                "id": "I.4",
                "name": "Armazenar artefatos de ML",
                "description": "Armazenar e gerenciar os artefatos gerados no desenvolvimento de ML.",
                "stakeholders": ["SE"],
                "concerns": [
                    ("I4", "Armazenamento",
                     "onde os artefatos de ML (modelos, dados, scripts) serão armazenados.",
                     "Onde ficarão modelos, dados, experimentos e scripts? Com que retenção?",
                     ["M7", "M12", "I1", "I7", "I11"]),
                ],
            },
            {
                "id": "I.5",
                "name": "Observar o modelo",
                "description": "Analisar desempenho, comportamento e resultados do modelo e do sistema.",
                "stakeholders": ["SE"],
                "concerns": [
                    ("I5", "Monitorabilidade",
                     "a necessidade de monitorar dados e saídas do modelo para alertar/detectar drift ou mudanças.",
                     "O que monitorar nos dados e nas saídas para detectar drift? Quem recebe os alertas?",
                     ["M5", "M14", "D6", "D7", "D8", "D9", "D10", "D11", "D12"]),
                    ("I6", "Telemetria",
                     "quais dados de uso do sistema precisam ser coletados (ex.: cliques em botões).",
                     "Que dados de uso (cliques, interações) precisam ser coletados?",
                     ["U2", "U3", "U5"]),
                ],
            },
            {
                "id": "I.6",
                "name": "Automatizar o workflow de ML ponta a ponta",
                "description": "Projetar um processo automatizado do preparo dos dados à implantação "
                "e monitoramento do modelo.",
                "stakeholders": ["DS", "SE"],
                "concerns": [
                    ("I7", "Reprodutibilidade",
                     "a necessidade de reexecutar um processo de ML sobre os mesmos dados/experimentos e obter os mesmos resultados.",
                     "Como garantir que treinos e experimentos possam ser reexecutados com os mesmos resultados?",
                     []),
                    ("I8", "Manutenibilidade",
                     "a necessidade de modificar o sistema para melhorar o desempenho ou adaptá-lo a mudanças no ambiente.",
                     "Como o sistema será modificado/evoluído quando o ambiente ou o desempenho mudarem?",
                     []),
                ],
            },
            {
                "id": "I.7",
                "name": "Integrar o modelo",
                "description": "Incorporar o modelo treinado ao sistema maior em que será usado.",
                "stakeholders": ["SE"],
                "concerns": [
                    ("I9", "Integração",
                     "a integração do modelo com o restante da funcionalidade (segurança, privacidade, justiça, aspectos legais).",
                     "Como o modelo se integra ao restante do sistema (APIs, segurança, privacidade, requisitos legais)?",
                     []),
                    ("I10", "Inteligência de decisão híbrida",
                     "a combinação das saídas do modelo com regras ou heurísticas para decisões mais efetivas.",
                     "As saídas do modelo serão combinadas com regras de negócio ou heurísticas? Quais?",
                     []),
                ],
            },
            {
                "id": "I.8",
                "name": "Avaliar o custo financeiro da infraestrutura",
                "description": "Avaliar as despesas com recursos computacionais, hardware, software e serviços.",
                "stakeholders": ["BO", "SE"],
                "concerns": [
                    ("I11", "Custo",
                     "o custo financeiro das inferências e da infraestrutura, que pode afetar decisões de arquitetura.",
                     "Quanto custa executar e manter o modelo (inferência, treino, serviços)? Qual o orçamento?",
                     []),
                ],
            },
        ],
    },
    {
        "id": "M",
        "name": "Modelo",
        "color": "#b3cde8",
        "description": "Define entradas e saídas esperadas, algoritmos candidatos, ajuste de "
        "hiperparâmetros, métricas e expectativas de desempenho, explicabilidade, escalabilidade, "
        "viés/justiça e proteção de dados sensíveis.",
        "tasks": [
            {
                "id": "M.1",
                "name": "Selecionar e configurar o modelo",
                "description": "Pré-selecionar algoritmos adequados e experimentar combinações de "
                "hiperparâmetros para encontrar a melhor configuração.",
                "stakeholders": ["DS"],
                "experimental": True,
                "concerns": [
                    ("M1", "Seleção de algoritmo e modelo",
                     "o conjunto de algoritmos a investigar, considerando o problema e outros concerns (ex.: explicabilidade).",
                     "Quais algoritmos serão investigados, dadas as restrições do problema (ex.: explicabilidade)?",
                     ["M2", "M6", "M8", "D5"]),
                    ("M2", "Ajuste de hiperparâmetros",
                     "a necessidade de escolher um conjunto ótimo de hiperparâmetros.",
                     "Haverá ajuste de hiperparâmetros? Com que estratégia e orçamento de tempo?",
                     ["M4"]),
                ],
            },
            {
                "id": "M.2",
                "name": "Treinar o modelo",
                "description": "Criar um modelo que capture os padrões dos dados e generalize para "
                "exemplos não vistos.",
                "stakeholders": ["DS"],
                "experimental": True,
                "concerns": [
                    ("M3", "Entradas e saídas",
                     "as entradas (features) e as saídas esperadas do modelo; podem ser refinadas no pré-processamento.",
                     "Quais são as entradas (features) e a saída (rótulo) do modelo?",
                     ["M11", "D14", "I1", "I2", "I3", "I10"]),
                    ("M4", "Tempo de aprendizado",
                     "o tempo aceitável para treinar o modelo.",
                     "Qual é o tempo aceitável para treinar (e retreinar) o modelo?",
                     ["I3", "I11"]),
                ],
            },
            {
                "id": "M.3",
                "name": "Validar o modelo",
                "description": "Garantir que o modelo treinado atenda aos critérios desejados.",
                "stakeholders": ["DS", "DE"],
                "concerns": [
                    ("M5", "Métricas de desempenho",
                     "as métricas de avaliação (precisão, recall, F1, erro quadrático) e as expectativas mensuráveis.",
                     "Quais métricas avaliam o modelo e quais valores são esperados?",
                     ["M2"]),
                    ("M6", "Modelo de referência",
                     "o modelo simples opcional que serve de referência para contextualizar os resultados.",
                     "Qual modelo simples (baseline) servirá de referência para comparar os resultados?",
                     []),
                ],
            },
            {
                "id": "M.4",
                "name": "Implantar o modelo",
                "description": "Tornar o modelo disponível e operacional em produção para usuários "
                "ou outros sistemas.",
                "stakeholders": ["DS"],
                "concerns": [
                    ("M7", "Tempo de inferência",
                     "o tempo aceitável para executar o modelo e retornar as predições.",
                     "Qual é o tempo aceitável para o modelo responder uma predição?",
                     ["M12", "I1", "I2", "I11"]),
                    ("M8", "Tamanho e complexidade do modelo",
                     "o tamanho do modelo em armazenamento e sua complexidade (ex.: poda em árvores de decisão).",
                     "Há limites de tamanho/complexidade para o modelo (memória, dispositivo, poda)?",
                     ["M4", "M7", "M11"]),
                    ("M9", "Degradação de desempenho",
                     "a consciência de que o desempenho preditivo cai com o tempo em ambientes que mudam.",
                     "Como detectar e tratar a queda de desempenho do modelo ao longo do tempo?",
                     ["M10", "I3"]),
                    ("M10", "Versionamento",
                     "as versões de bibliotecas e a compatibilidade entre dependências, para reprodutibilidade e portabilidade.",
                     "Como versionar modelo, bibliotecas e dependências para garantir compatibilidade?",
                     ["I2", "I7"]),
                ],
            },
            {
                "id": "M.5",
                "name": "Avaliar outras características de qualidade",
                "description": "Avaliar aspectos além da acurácia, importantes para desempenho, "
                "confiabilidade e adequação ao mundo real.",
                "stakeholders": ["DS", "SE"],
                "concerns": [
                    ("M11", "Interpretabilidade e explicabilidade",
                     "a necessidade de entender as razões das inferências e de resumir as razões das decisões.",
                     "Os usuários ou reguladores precisam entender por que o modelo tomou cada decisão?",
                     ["M13", "I8", "U7"]),
                    ("M12", "Escalabilidade",
                     "a necessidade de o modelo manter o desempenho à medida que dados e complexidade crescem.",
                     "O modelo precisa manter o desempenho com mais dados, usuários ou complexidade? Em que escala?",
                     ["D5", "I1", "I2", "I11"]),
                    ("M13", "Viés e justiça",
                     "a necessidade de o modelo tratar grupos de pessoas ou entidades de forma justa.",
                     "Que grupos podem ser prejudicados por decisões do modelo? Como medir e mitigar o viés?",
                     ["D6", "D7", "D8", "D9", "D10", "D11", "D12", "D14"]),
                    ("M14", "Segurança e privacidade",
                     "a necessidade de o modelo proteger dados sensíveis e impedir acesso não autorizado.",
                     "Que dados sensíveis o modelo manipula e como protegê-los contra acesso não autorizado?",
                     ["D3", "D13", "I2", "I4"]),
                ],
            },
        ],
    },
    {
        "id": "D",
        "name": "Dados",
        "color": "#d2dc5a",
        "description": "Baseada no modelo de qualidade de dados da ISO/IEC 25012: de onde vêm "
        "os dados, como selecioná-los e descrevê-los, sua qualidade inerente, operações de "
        "preparo, distribuição e divisão, e a necessidade de um golden dataset.",
        "tasks": [
            {
                "id": "D.1",
                "name": "Coletar dados",
                "description": "Obter a tempo os dados necessários, das várias fontes, para "
                "desenvolver e avaliar o modelo.",
                "stakeholders": ["DS", "SE"],
                "concerns": [
                    ("D1", "Origem",
                     "de onde os dados serão obtidos.",
                     "De onde vêm os dados (planilhas, bancos, APIs, nuvem)? Quem é o dono?",
                     ["I1"]),
                    ("D2", "Tempestividade",
                     "o tempo entre quando o dado é esperado e quando está disponível para uso.",
                     "Quanto tempo leva entre o dado ser gerado e estar disponível para uso?",
                     []),
                ],
            },
            {
                "id": "D.2",
                "name": "Selecionar e descrever os dados",
                "description": "Escolher os dados de treino, validação e teste e descrever suas features.",
                "stakeholders": ["DS", "DE"],
                "concerns": [
                    ("D3", "Seleção de dados",
                     "o processo de determinar o tipo de dado e as amostras adequadas para coleta.",
                     "Como os dados e as amostras serão selecionados?",
                     []),
                    ("D4", "Dicionário de dados",
                     "os nomes, definições e atributos dos elementos de dados e modelos.",
                     "O que significa cada dado coletado? (considere criar um dicionário de dados)",
                     []),
                    ("D5", "Quantidade",
                     "a quantidade esperada de dados de acordo com o tipo de problema e a complexidade do algoritmo.",
                     "Quantos dados são necessários/estão disponíveis para o tipo de problema?",
                     []),
                ],
            },
            {
                "id": "D.3",
                "name": "Avaliar a qualidade dos dados",
                "description": "Avaliar os dados de treino e teste para garantir que atendam a "
                "critérios e padrões de qualidade.",
                "stakeholders": ["DS", "DE"],
                "concerns": [
                    ("D6", "Acurácia",
                     "a necessidade de obter dados corretos.",
                     "Como garantir que os dados estão corretos?", []),
                    ("D7", "Completude",
                     "a necessidade de dados com observações suficientes de todas as situações em que o modelo vai operar.",
                     "Os dados cobrem todas as situações em que o modelo vai operar?", []),
                    ("D8", "Credibilidade",
                     "a necessidade de dados verdadeiros, críveis e compreensíveis pelos usuários.",
                     "Os dados são confiáveis e compreensíveis para os usuários?", []),
                    ("D9", "Consistência",
                     "a necessidade de dados consistentes em um contexto específico.",
                     "Os dados são consistentes entre fontes e ao longo do tempo?", []),
                    ("D10", "Uso real",
                     "a necessidade de dados reais que representem o problema real.",
                     "Os dados representam o uso real do problema (e não apenas dados sintéticos)?", []),
                    ("D11", "Viés",
                     "a necessidade de amostras justas e distribuições representativas.",
                     "As amostras são representativas e sem viés entre grupos?", []),
                    ("D12", "Ética",
                     "a necessidade de dados que não causem impactos adversos à sociedade.",
                     "O uso desses dados pode causar impactos adversos à sociedade? Quais?", []),
                    ("D13", "Anonimização",
                     "a necessidade de anonimizar ou pseudonimizar identidades, mantendo a utilidade dos dados.",
                     "Há dados pessoais que precisam ser anonimizados ou pseudonimizados (ex.: LGPD)?", []),
                ],
            },
            {
                "id": "D.4",
                "name": "Converter dados na representação do modelo",
                "description": "Transformar os dados brutos em um formato que o algoritmo possa processar.",
                "stakeholders": ["DS", "DE"],
                "concerns": [
                    ("D14", "Operações e modelagem de dados",
                     "as operações sobre os dados (limpeza, rotulação) e o necessário para convertê-los na representação do modelo.",
                     "Que operações serão aplicadas aos dados (limpeza, rotulação, transformação)?",
                     ["O3"]),
                ],
            },
            {
                "id": "D.5",
                "name": "Dividir o dataset",
                "description": "Separar os dados disponíveis em conjuntos de treino, validação e teste.",
                "stakeholders": ["DS"],
                "concerns": [
                    ("D15", "Distribuição dos dados",
                     "as distribuições esperadas e como os dados serão divididos em treino, validação e teste.",
                     "Como os dados serão divididos em treino, validação e teste? Que distribuição se espera?",
                     ["M5"]),
                ],
            },
            {
                "id": "D.6",
                "name": "Definir um golden dataset",
                "description": "Criar um conjunto de alta qualidade, validado pelo especialista, que "
                "sirva de verdade de referência para treino e avaliação.",
                "stakeholders": ["DS", "DE"],
                "concerns": [
                    ("D16", "Golden dataset",
                     "a necessidade de um dataset de referência aprovado por um especialista de domínio para monitorar dados adquiridos depois.",
                     "Existe (ou será criado) um dataset de referência aprovado por um especialista de domínio?",
                     ["M5"]),
                ],
            },
        ],
    },
]

WORKFLOW = [
    {
        "step": 1,
        "name": "Analisar cada perspectiva",
        "description": "Percorrer as perspectivas na ordem: Objetivos do sistema, Experiência "
        "do usuário, Infraestrutura, Modelo e Dados.",
    },
    {
        "step": 2,
        "name": "Analisar cada tarefa da perspectiva",
        "description": "Quebrar a análise nas tarefas da perspectiva (28 no total) e entender "
        "os concerns associados, envolvendo os stakeholders sugeridos.",
    },
    {
        "step": 3,
        "name": "Analisar os concerns (verificação de aplicabilidade)",
        "description": "Usando o diagrama de tarefas e concerns, decidir se cada concern é "
        "relevante para o sistema, considerando suas relações com outros concerns.",
    },
    {
        "step": 4,
        "name": "Especificar os concerns aplicáveis",
        "description": "Responder à pergunta-guia de cada concern aplicável no template de "
        "especificação. Concerns de tarefas marcadas com 'E' tendem a ser refinados durante a "
        "experimentação.",
    },
]


def _concern(cid, name, desc, question, related, task_id, perspective_id) -> dict:
    tpl = TEMPLATE.get(cid)
    return {
        "id": cid,
        "name": name,
        "description": desc,
        # perguntas do template (Miro) quando existem; senão, a adaptada.
        "questions": tpl["questions"] if tpl else [question],
        "question_source": "template" if tpl else "adapted",
        "hint": (tpl or {}).get("hint"),
        "checklist": (tpl or {}).get("checklist", []),
        "example": (tpl or {}).get("example"),
        "related": related,
        "task_id": task_id,
        "perspective_id": perspective_id,
    }


def _build() -> dict:
    perspectives = []
    for p in _P:
        tasks = []
        for t in p["tasks"]:
            concerns = [_concern(*c, t["id"], p["id"]) for c in t["concerns"]]
            tasks.append(
                {
                    "id": t["id"],
                    "name": t["name"],
                    "description": t["description"],
                    "stakeholders": t["stakeholders"],
                    "experimental": t.get("experimental", False),
                    "concerns": concerns,
                }
            )
        perspectives.append(
            {k: p[k] for k in ("id", "name", "color", "description")}
            | {"goal": GOALS[p["id"]], "tasks": tasks}
        )
    return {
        "id": CATALOG_ID,
        "version": CATALOG_VERSION,
        "source": {
            "title": "Identifying concerns when specifying machine learning-enabled systems: "
            "A perspective-based approach",
            "authors": "Villamizar, Kalinowski, Lopes, Mendez",
            "venue": "Journal of Systems and Software 213 (2024) 112053",
            "doi": "10.1016/j.jss.2024.112053",
        },
        "template_source": TEMPLATE_SOURCE,
        "stakeholders": STAKEHOLDERS,
        "perspectives": perspectives,
        "workflow": WORKFLOW,
    }


@lru_cache(maxsize=1)
def get_catalog() -> dict:
    """Catálogo completo (estrutura aninhada, pronta para a API)."""
    return _build()


@lru_cache(maxsize=1)
def concerns_by_id() -> dict[str, dict]:
    return {c["id"]: c for p in get_catalog()["perspectives"] for t in p["tasks"] for c in t["concerns"]}


@lru_cache(maxsize=1)
def ordered_concern_ids() -> list[str]:
    """Ordem do workflow (Fig. 5): perspectiva -> tarefa -> concern."""
    return [c["id"] for p in get_catalog()["perspectives"] for t in p["tasks"] for c in t["concerns"]]


@lru_cache(maxsize=1)
def related_map() -> dict[str, list[str]]:
    """Relações simétricas entre concerns, na ordem do workflow."""
    order = {cid: i for i, cid in enumerate(ordered_concern_ids())}
    rel: dict[str, set[str]] = {cid: set() for cid in order}
    for cid, c in concerns_by_id().items():
        for other in c["related"]:
            if other in rel and other != cid:
                rel[cid].add(other)
                rel[other].add(cid)
    return {cid: sorted(others, key=order.__getitem__) for cid, others in rel.items()}
