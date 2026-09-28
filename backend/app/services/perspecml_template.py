"""Conteúdo do template de especificação PerSpecML publicado no Miro.

Fonte: Villamizar et al. (2023), "PerSpecML — machine learning", Miroverse
(https://miro.com/miroverse/perspecml-machine-learning/), citado no paper como
o template com exemplo ilustrativo (Seção 3.7).

Traz, traduzidos para o português:
- ``GOALS``: a frase de objetivo de cada perspectiva;
- ``TEMPLATE``: por concern, as perguntas do template (elemento 5 da Fig. 3),
  dicas, itens a considerar e o exemplo do caso do empréstimo bancário (o
  mesmo cenário da validação acadêmica, Seção 5.1 do paper).

O template do Miro reflete uma versão anterior do catálogo: 47 dos 60
concerns têm pergunta nele. Os demais usam a pergunta adaptada do catálogo
(`perspecml_catalog`). As tarefas seguem a estrutura final do paper; aqui o
conteúdo é importado no nível do concern.
"""

from __future__ import annotations

SOURCE = {
    "title": "PerSpecML — template de especificação (Miro)",
    "authors": "Villamizar et al.",
    "year": 2023,
    "url": "https://miro.com/miroverse/perspecml-machine-learning/",
}

GOALS = {
    "O": "Um bom sistema com ML conecta inteligência e experiência para alcançar "
    "os resultados desejados.",
    "U": "Um bom sistema com ML apresenta as saídas do modelo aos usuários, atinge os "
    "objetivos do sistema, minimiza possíveis falhas do modelo e gera dados para melhorá-lo.",
    "I": "Um bom sistema com ML transforma as saídas do modelo em um sistema totalmente "
    "funcional.",
    "M": "Construir um modelo de ML não é só treinar um algoritmo com dados para prever ou "
    "classificar um fenômeno. Vários outros aspectos determinam o seu sucesso.",
    "D": "Dados ruins resultam em predições imprecisas (“entra lixo, sai lixo”). Por isso, "
    "ML requer dados de entrada de alta qualidade.",
}

# Caso de exemplo do template (empréstimo bancário). A user story é a da
# validação acadêmica do paper (Seção 5.1).
EXAMPLE_SPEC = {
    "title": "Exemplo: classificação de bons e maus pagadores",
    "user_story": "Como gerente do banco, quero classificar automaticamente os clientes, "
    "para decidir sobre a concessão de um empréstimo solicitado.",
    "description": "Especificação de exemplo do template PerSpecML (caso do empréstimo "
    "bancário). Os concerns sem exemplo no template ficam pendentes.",
}

TEMPLATE: dict[str, dict] = {
    # --- Objetivos do sistema -------------------------------------------------
    "O1": {
        "questions": ["Em que contexto o ML vai funcionar?"],
        "example": "A aplicação com a nova funcionalidade de ML será usada inicialmente "
        "por agências selecionadas do banco.\nInicialmente, os usuários da aplicação têm "
        "mais de 20 anos de experiência no banco.",
    },
    "O2": {
        "questions": ["Qual é o problema que o ML pretende resolver?"],
        "example": "O banco está concedendo um número considerável de empréstimos que não "
        "são pagos. Em resumo, está emprestando dinheiro a maus pagadores.",
    },
    "O3": {
        "questions": ["Qual é a funcionalidade de ML?"],
        "example": "Classificar um cliente como bom ou mau pagador.",
    },
    "O5": {
        "questions": ["Como o ML vai contribuir para alcançar os objetivos organizacionais?"],
        "example": "Reduzir de 20% para 10% o número de clientes inadimplentes três meses "
        "após a concessão do empréstimo.\nAumentar em 10% o número de empréstimos "
        "concedidos nos últimos 30 dias.",
    },
    "O7": {
        "questions": ["Que metas dos usuários vão medir o sucesso do sistema com ML?"],
        "hint": "Por exemplo: se o sistema ajuda os usuários a encontrar conteúdo de que "
        "vão gostar, eles estão de fato encontrando esse conteúdo?",
        "example": "Aumentar a eficiência operacional dos operadores do banco, sugerindo "
        "uma classificação na concessão de empréstimos, o que reduz o tempo de concessão "
        "e aumenta a confiabilidade.",
    },
    "O8": {
        "questions": [
            "Que metas de desempenho do modelo serão usadas para medir a qualidade das "
            "predições?"
        ],
        "example": "Acurácia do modelo maior que 80%.\nRecall dos maus pagadores maior "
        "que 90%, para evitar conceder empréstimos a quem não paga.",
    },
    "O9": {
        "questions": ["Que indicadores vão medir o sucesso do sistema com ML?"],
        "hint": "Por exemplo: sentimento do cliente, engajamento do cliente.",
        "example": "Número de empréstimos concedidos pelos operadores seguindo a sugestão "
        "do modelo.",
    },
    "O10": {
        "questions": ["Qual é o trade-off de ML?"],
        "hint": "Por exemplo: um falso positivo é melhor que um falso negativo? É melhor "
        "perder acurácia ou ganhar desempenho?",
        "example": "É melhor errar ao não emprestar a um bom pagador do que emprestar a um "
        "mau pagador: é extremamente importante não conceder empréstimo a um mau "
        "pagador.\nO foco deve ser aumentar a confiabilidade do modelo. Não é problema o "
        "modelo demorar um pouco mais para responder, se isso aumentar a confiabilidade.",
    },
    # --- Experiência do usuário ----------------------------------------------
    "U1": {
        "questions": ["Qual é o valor agregado que os usuários percebem nas predições?"],
        "example": "Agilidade no processo de empréstimo com o apoio do modelo.\nConfiança "
        "na concessão ao usar o modelo como apoio à decisão.",
    },
    "U2": {
        "questions": ["Que tipo de ação o modelo vai exigir do usuário após uma predição?"],
        "example": "A classificação automática deve ser apenas uma sugestão: o gerente do "
        "banco toma a decisão final sobre conceder ou não o empréstimo.",
    },
    "U3": {
        "questions": ["Com que frequência o modelo interage com o usuário?"],
        "example": "Sempre que o usuário executa a funcionalidade “Análise de empréstimo "
        "do cliente X”.",
    },
    "U4": {
        "questions": ["Como as predições do modelo serão exibidas?"],
        "example": "O gerente deve identificar facilmente se o modelo sugere ou não "
        "conceder o empréstimo.",
    },
    "U5": {
        "questions": ["Como as interações dos usuários vão apoiar a melhoria do modelo?"],
        "hint": "Lembre que coletar e rotular dados é uma tarefa cara, que exige tempo e "
        "pessoas.",
        "example": "O gerente deve poder aumentar o score de empréstimo de um cliente, e o "
        "modelo leva esse ajuste em conta.",
    },
    "U7": {
        "questions": ["Quem será responsável pelos erros?"],
        "example": "Os gerentes responsáveis pela concessão dos empréstimos.",
    },
    "U8": {
        # O template agrupa estas duas perguntas na tarefa "Analisar predições
        # erradas"; a segunda não tem concern próprio na versão final do paper.
        "questions": [
            "Qual é o custo de uma predição errada?",
            "Como as interações dos usuários vão ajudá-los a perceber que houve um erro?",
        ],
        "example": "Dinheiro não recuperado quando emprestado a um mau pagador.\nJuros que "
        "o banco deixa de ganhar por não emprestar a um bom pagador.\nO operador do banco "
        "deve ter a opção de sinalizar classificações suspeitas para análise posterior.",
    },
    # --- Infraestrutura ---------------------------------------------------------
    "I1": {
        "questions": ["Como os dados serão transportados da origem até o modelo?"],
        "example": "Para treinar o modelo, será feita uma única coleta/consulta no banco de "
        "dados em nuvem.\nDurante a operação, o streaming de dados será feito por "
        "integrações entre o banco de dados em nuvem e o web service que consome o modelo.",
    },
    "I2": {
        "questions": ["Como o modelo será executado e consumido?"],
        "example": "O modelo de classificação será implantado como web service na nuvem "
        "contratada pelo banco.",
    },
    "I3": {
        "questions": [
            "Qual será a estratégia para atualizar o modelo e garantir o aprendizado "
            "incremental?"
        ],
        "example": "Todo mês, o modelo de classificação deve ser retreinado com os novos "
        "dados de pagamento dos clientes.\nO retreino será um processo offline.",
    },
    "I4": {
        "questions": [
            "Onde os artefatos de ML (modelos, dados, scripts, experimentos, ambientes) "
            "serão armazenados?"
        ],
        "example": "Todos os artefatos gerados durante o desenvolvimento serão armazenados "
        "na nuvem contratada pelo banco.",
    },
    "I5": {
        "questions": [
            "Como será identificado que o modelo perdeu desempenho ou que os dados deixaram "
            "de representar os dados de treino?"
        ],
        "example": "Deve ser desenvolvida uma solução de detecção de concept drift para "
        "identificar quando os dados de operação deixam de corresponder aos de treino.\n"
        "Um alarme de concept drift vai disparar o retreino do modelo.",
    },
    "I6": {
        "questions": ["Qual será a estratégia para obter dados de uso do sistema com ML?"],
        "hint": "Telemetria envolve coletar dados como cliques em botões específicos e pode "
        "incluir outros dados de uso e desempenho, como o número de consultas ao banco de "
        "dados e o percentual de uso do sistema.",
        "example": "Será acompanhado o número de requisições ao web service implantado na "
        "nuvem do banco.\nOs empréstimos concedidos automaticamente pela solução serão "
        "consultados e monitorados.",
    },
    "I7": {
        "questions": [
            "Qual é a estratégia para garantir a reprodutibilidade e a manutenção envolvidas "
            "em projetar, construir e monitorar o sistema com ML (MLOps)?"
        ],
        "hint": "No template, esta pergunta cobre juntas a reprodutibilidade (I7) e a "
        "manutenibilidade (I8).",
        "example": "Inicialmente, não será necessário criar pipelines automatizados.",
    },
    "I8": {
        "questions": [
            "Qual é a estratégia para garantir a reprodutibilidade e a manutenção envolvidas "
            "em projetar, construir e monitorar o sistema com ML (MLOps)?"
        ],
        "hint": "No template, esta pergunta cobre juntas a reprodutibilidade (I7) e a "
        "manutenibilidade (I8).",
        "example": "O código de notebooks e scripts deve seguir um padrão reconhecido pela "
        "indústria para a linguagem usada (documentação, princípios SOLID).",
    },
    "I9": {
        "questions": [
            "Como o modelo será integrado ao restante da funcionalidade do sistema e que "
            "propriedades serão avaliadas?"
        ],
        "hint": "Por exemplo: segurança da informação, segurança operacional, privacidade, "
        "entre outras.",
        "example": "As características de qualidade da ISO/IEC 25010 devem ser testadas "
        "após a integração da nova funcionalidade de ML, conforme a especificação dessas "
        "características para o restante do sistema.",
    },
    "I11": {
        "questions": ["Você estimou o custo envolvido com a infraestrutura?"],
        "hint": "O custo pode condicionar as decisões de arquitetura. Modelos excelentes "
        "podem ser inviáveis pelo custo de execução e manutenção.",
        "example": "O custo de infraestrutura não deve passar de R$ 40.000,00 por mês "
        "(uso de recursos de nuvem).",
    },
    # --- Modelo -------------------------------------------------------------------
    "M1": {
        "questions": [
            "Que conjunto de algoritmos pode ser usado/investigado, dado o tipo de problema "
            "de ML e outras restrições?"
        ],
        "example": "Inicialmente, serão testados algoritmos de árvores de decisão, KNN, "
        "Naive Bayes e SVM, além de ensembles como Random Forest e Extra-Trees.",
    },
    "M2": {
        "questions": ["Há necessidade de maximizar o desempenho do modelo? Com que estratégia?"],
        "hint": "Ajustar os parâmetros dos algoritmos e usar AutoML são opções.",
        "example": "Dependendo dos resultados iniciais ao longo do projeto, os parâmetros "
        "dos algoritmos serão ajustados.",
    },
    "M3": {
        "questions": ["Quais serão os dados de entrada e de saída do modelo?"],
        "hint": "O conjunto de entradas pode ser refinado durante as atividades de "
        "experimentação.",
        "example": "Entradas: renda mensal, valor dos empréstimos atuais, número de "
        "dependentes, idade, …\nSaída: classificação automática do cliente como bom ou "
        "mau pagador.",
    },
    "M4": {
        "questions": ["Qual é o tempo de treinamento esperado?"],
        "example": "Não há restrição significativa: o modelo pode levar dias para treinar, "
        "desde que as inferências sejam rápidas e confiáveis.",
    },
    "M5": {
        "questions": [
            "Que valores das métricas de desempenho vão medir a qualidade das predições?"
        ],
        "example": "Acurácia > 80%; recall dos maus pagadores > 90%.",
    },
    "M6": {
        "questions": [
            "Existe um modelo de referência (baseline) para comparar os resultados do "
            "modelo treinado?"
        ],
        "hint": "É o modelo simples e opcional que serve de referência. Sua função "
        "principal é contextualizar os resultados dos modelos treinados.",
        "example": "O banco não tem um modelo de referência.",
    },
    "M7": {
        "questions": [
            "Qual é o tempo de inferência esperado para o modelo calcular e entregar as "
            "predições?"
        ],
        "example": "No máximo 2 minutos.",
    },
    "M8": {
        "questions": [
            "Há alguma restrição sobre o tamanho do modelo, em armazenamento e complexidade?"
        ],
        "hint": "Por exemplo: árvores de decisão podem precisar de poda.",
        "example": "A complexidade do modelo deve permitir explicar razoavelmente a "
        "concessão do empréstimo.",
    },
    "M9": {
        "questions": ["Como a degradação do desempenho do modelo será avaliada?"],
        "example": "A equipe de desenvolvimento deve monitorar constantemente os dados e as "
        "saídas do modelo de classificação.",
    },
    "M11": {
        "questions": ["É preciso entender as razões das inferências do modelo?"],
        "hint": "Outros concerns relacionados, como transparência e interpretabilidade, "
        "podem se aplicar.",
        "example": "Por lei, o banco é obrigado a explicar por que um empréstimo não foi "
        "concedido.",
    },
    # --- Dados ----------------------------------------------------------------------
    "D1": {
        "questions": ["Qual é a fonte/origem em que os dados estão armazenados?"],
        "example": "Banco de dados na nuvem contratada pelo banco.",
    },
    "D2": {
        "questions": [
            "Quanto tempo passa entre o momento em que o dado é esperado e o momento em que "
            "ele está disponível?"
        ],
        "example": "Os dados serão coletados mensalmente.",
    },
    "D4": {
        "questions": ["O que significam os dados coletados?"],
        "hint": "Considere criar um dicionário de dados.",
        "example": "O projeto de desenvolvimento do modelo deve ter um dicionário de dados.",
    },
    "D5": {
        "questions": ["Quantos dados serão selecionados?"],
        "example": "Inicialmente, serão usados os dados de clientes dos últimos 10 anos.",
    },
    "D6": {
        "questions": ["Os dados estão corretos?"],
        "example": "Será verificado.",
    },
    "D7": {
        "questions": [
            "Os dados contêm observações suficientes de todas as situações em que o modelo "
            "vai operar?"
        ],
        "example": "Os dados dos clientes devem contemplar homens, mulheres e diferentes "
        "idades (jovens, idosos)…",
    },
    "D9": {
        "questions": ["Os dados são consistentes?"],
        "example": "Será verificado.",
    },
    "D11": {
        "questions": ["Os dados estão livres de viés?"],
        "example": "Será verificado.",
    },
    "D12": {
        "questions": ["Os dados podem ser usados e processados livremente (ética e privacidade)?"],
        "example": "Os dados podem ser usados, desde que respeitadas as definições da área "
        "de segurança da informação do banco.",
    },
    "D14": {
        "questions": [
            "Que operações serão aplicadas para converter os dados na representação do "
            "modelo?"
        ],
        "checklist": ["Limpeza de dados", "Feature engineering", "Rotulação", "Modelagem"],
        "example": "O processo de desenvolvimento deve definir o que fazer com dados "
        "faltantes. Dependendo da quantidade de dados, devem ser usadas técnicas de data "
        "augmentation.",
    },
    "D15": {
        "questions": ["Como os dados serão divididos?"],
        "checklist": ["Conjunto de treino", "Conjunto de validação", "Conjunto de teste"],
        "example": "Do total de dados de clientes disponíveis, 80% serão usados para treinar "
        "o modelo e os 20% restantes para testá-lo. Devem ser usadas técnicas de validação "
        "cruzada.",
    },
    "D16": {
        "questions": ["É necessário um golden dataset aprovado por um especialista de domínio?"],
        "example": "O projeto deve ter um dataset de altíssima qualidade (golden), aprovado "
        "pelo especialista de domínio, para monitorar os novos dados.",
    },
}
