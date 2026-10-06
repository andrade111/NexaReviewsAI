# NexaReviews AI 🚀

> **Sistema Modular de Análise de Sentimentos em Avaliações de E-commerce com Processamento de Linguagem Natural (NLP) e Machine Learning.**

---

## 📌 Visão Geral do Projeto

O **NexaReviews AI** foi desenvolvido para automatizar a classificação de sentimentos (*positivo* ou *negativo*) em avaliações de produtos de plataformas de e-commerce. A solução substitui processos lentos e custosos de auditoria manual por um pipeline inteligente, de alta performance e pronto para produção, viabilizando tomadas de decisão ágeis no monitoramento da satisfação de clientes.

### Principais Benefícios:
- ⚡ **Redução de Custo e Tempo:** Classificação instantânea de milhares de reviews.
- 🧱 **Arquitetura Modular e Limpa:** Separação clara entre limpeza de texto, ingestão de dados e modelagem estatística.
- 🎯 **Pipeline Otimizado:** Vetorização textual via **TF-IDF** (N-grams de 1 e 2 termos) e classificação linear via **Regressão Logística**.
- 📊 **Visualização Integrada:** Geração automática de gráficos estatísticos com **Seaborn** e **Matplotlib**.

---

## 📁 Estrutura do Diretório

```text
NexaReviews-AI/
│
├── data/
│   ├── raw/
│   │   └── dataset.csv                     # Dados brutos das avaliações
│   └── processed/
│       └── dataset_cleaned.csv             # Dados tratados com coluna texto_limpo
│
├── notebooks/
│   └── 01_analise_exploratoria.ipynb       # Análise exploratória e experimentos
│
├── src/
│   ├── __init__.py                         # Inicializador do pacote e exportações
│   ├── text_cleaner.py                     # Classe TextCleaner (normalização e regex)
│   ├── data_processor.py                   # Classe DataProcessor (carga, auditoria e limpeza)
│   └── model_pipeline.py                   # Classe SentimentModel (TF-IDF + Regressão Logística)
│
├── models/
│   ├── sentiment_model.pkl                 # Modelo treinado e serializado via Joblib
│   └── distribuicao_sentimentos.png        # Gráfico de distribuição de classes gerado
│
├── .gitignore                              # Arquivos e diretórios ignorados pelo Git
├── requirements.txt                        # Versões fixadas das dependências do projeto
├── README.md                               # Documentação técnica do projeto
└── main.py                                 # Script principal de execução ponta a ponta
```

---

## ⚙️ Especificação dos Módulos

### 1. `src/text_cleaner.py` (`TextCleaner`)
- **`clean_text(text: str) -> str`**: Método estático que normaliza o texto:
  - Conversão para letras minúsculas.
  - Remoção de acentos através de decomposição Unicode (`unicodedata.normalize`).
  - Remoção de números, pontuações e caracteres especiais mantendo apenas letras e espaços.
  - Eliminação de espaços em branco duplicados e remoção de espaços nas extremidades (`strip`).

### 2. `src/data_processor.py` (`DataProcessor`)
- **`load_data()`**: Ingestão do dataset CSV em `data/raw/dataset.csv`.
- **`get_info()`**: Diagnóstico de dimensões (shape) e contagem/porcentagem de valores ausentes (nulos).
- **`clean_data()`**: Elimina linhas nulas, aplica o `TextCleaner` na coluna `texto_review` e gera a coluna tratada `texto_limpo`.

### 3. `src/model_pipeline.py` (`SentimentModel`)
- **`__init__()`**: Constrói o `Pipeline` do Scikit-Learn integrando:
  1. `TfidfVectorizer(max_features=5000, ngram_range=(1, 2))`
  2. `LogisticRegression(random_state=42, C=1.0)`
- **`train(X, y, test_size=0.2)`**: Particiona treino/teste de forma estratificada, ajusta o pipeline e dispara a avaliação.
- **`evaluate(y_true, y_pred)`**: Emite métricas completas (Acurácia, `classification_report`, `confusion_matrix`).
- **`save_model(filepath)`**: Serializa o pipeline com `joblib`.
- **`load_model(filepath)`**: Carrega o modelo persistido para inferência rápida.

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
Recomenda-se o uso do **Python 3.10+** ou ambiente virtual dedicado.

### 2. Clonar ou Acessar o Diretório
```bash
cd NexaReviewsAI
```

### 3. Criar e Ativar o Ambiente Virtual (Opcional, mas Recomendado)
No Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

No Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Instalar as Dependências
```bash
pip install -r requirements.txt
```

### 5. Executar o Pipeline Completo
```bash
python main.py
```

O comando executará todo o fluxo:
1. Validação de diretórios (`data/raw`, `data/processed`, `models`, `notebooks`).
2. Carga e auditoria dos dados.
3. Higienização dos textos de review.
4. Geração do gráfico Seaborn salvo em `models/distribuicao_sentimentos.png`.
5. Treinamento estratificado do modelo TF-IDF + Regressão Logística.
6. Avaliação detalhada de métricas.
7. Salvamento do modelo em `models/sentiment_model.pkl`.
8. Demonstração de inferência em tempo real com predição de novos exemplos.

---

## 📓 Análise Exploratória (Jupyter Notebook)

Para interagir com o fluxo passo a passo e visualizar os gráficos detalhados:

```bash
jupyter notebook notebooks/01_analise_exploratoria.ipynb
```

---

## 📊 Exemplo de Inferência

```python
from src.text_cleaner import TextCleaner
from src.model_pipeline import SentimentModel

# 1. Carregar modelo salvo
model = SentimentModel()
model.load_model("models/sentiment_model.pkl")

# 2. Higienizar e prever
novo_review = "Entrega super rápida, produto maravilhoso e de excelente qualidade!"
review_limpo = TextCleaner.clean_text(novo_review)
predicao = model.predict(review_limpo)[0]

print(f"Sentimento detectado: {predicao}")
# Saída: Sentimento detectado: positivo
```

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Manipulação de Dados:** Pandas, NumPy
- **Machine Learning & NLP:** Scikit-Learn, Joblib
- **Visualização de Dados:** Matplotlib, Seaborn
- **Controle de Versão:** Git

---

## 📄 Licença
Este projeto foi desenvolvido sob a licença MIT. Sinta-se livre para utilizar, modificar e distribuir.
