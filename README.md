# Dashboard de Análise de Vendas e Performance

## Visão Geral

Este é um dashboard interativo de Business Intelligence construído em Python com o framework Streamlit. A aplicação transforma dados brutos de vendas, comissões e atividades de corretores em insights visuais e acionáveis, projetado para auxiliar gestores de vendas, analistas e a diretoria financeira na tomada de decisões estratégicas.

O dashboard oferece uma visão consolidada da performance de vendas, segmentação de corretores com Machine Learning, análise de inatividade e uma visão financeira das contas a pagar.

---

## ✨ Principais Funcionalidades

-   **📊 Visão Geral Dinâmica:** KPIs de vendas e atividade que se atualizam com base em filtros de período, supervisor e tipo de corretor.
-   **🧠 Segmentação com Machine Learning:** Utiliza o algoritmo **K-Means Clustering** para agrupar corretores em perfis de desempenho (Superestrelas, Grande Potencial, etc.), permitindo ações de gestão direcionadas.
-   **📉 Análise de Inatividade:** Identifica corretores que não venderam no período selecionado, analisando tendências e a distribuição por tipo de corretor.
-   ** individuale Profunda do Corretor:** Uma página dedicada para analisar a performance, o histórico de atividade e o foco de produtos de cada corretor individualmente.
-   **🏢 Análise por Canal de Vendas:** Compara a eficácia e produtividade dos diferentes "Tipos de Corretor" (escritórios, salão, etc.).
-   **💰 Visão Financeira:** Uma página exclusiva para a gestão financeira, com projeção de fluxo de caixa (contas a pagar), análise de despesas por categoria e centro de custo.
-   **💾 Exportação de Dados:** Funcionalidade para baixar os dados filtrados em formato CSV em diversas seções do dashboard.

---

## 🛠️ Tecnologias e Bibliotecas Utilizadas

-   **Linguagem:** Python 3.10+
-   **Framework Web:** Streamlit
-   **Análise de Dados:** Pandas
-   **Visualização de Dados:** Plotly, Matplotlib
-   **Machine Learning:** Scikit-learn

---

## 📂 Estrutura do Projeto

O projeto é organizado em uma estrutura modular para facilitar a manutenção e a escalabilidade:

```
.
├── 1_Visão_Geral.py             # Página principal do dashboard
├── utils.py                        # Funções de suporte (carregar dados, formatação, etc.)
├── requirements.txt                # Lista de dependências do projeto
├── .streamlit/
│   └── config.toml                 # Arquivo de configuração de tema do Streamlit
├── data/
│   ├── vendas.csv                  # Dados de vendas
│   ├── comissao.csv                # Dados de comissões pagas
│   ├── corretores_inativos.csv     # Dados de corretores sem vendas
│   └── contas_a_pagar_set24_set25.csv # Dados financeiros
├── imagens/
│   └── logo_usina_white.png        # Logo da empresa
└── pages/
    ├── 2_Análise_Individual_do_Corretor.py
    ├── 3_Análise_por_Tipo_de_Corretor.py
    └── 4_Análise_Financeira.py
```

---

## ⚙️ Configuração e Instalação Local

Siga os passos abaixo para executar o projeto em sua máquina local.

**Pré-requisitos:**
-   Python 3.10 ou superior
-   Git (opcional, para clonar o repositório)

**1. Clone o Repositório:**
```bash
git clone [URL-DO-SEU-REPOSITORIO-GITHUB]
cd [NOME-DO-SEU-REPOSITORIO]
```

**2. Crie e Ative um Ambiente Virtual (`venv`):**
É uma boa prática isolar as dependências do projeto.
```bash
# Criar o ambiente
python3 -m venv venv

# Ativar o ambiente
# No Linux/macOS:
source venv/bin/activate
# No Windows (PowerShell):
.\venv\Scripts\activate
```

**3. Instale as Dependências:**
Com o ambiente virtual ativo, instale todas as bibliotecas necessárias.
```bash
pip install -r requirements.txt
```

**4. Execute a Aplicação:**
```bash
streamlit run 1_Visão_Geral.py
```
A aplicação abrirá automaticamente no seu navegador padrão.



