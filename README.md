# NexaReviews AI 🚀

> **Plataforma Full-Stack de Análise Inteligente de Sentimentos em Avaliações de E-commerce com Machine Learning (Scikit-Learn), API RESTful de Alta Performance (FastAPI) e Frontend Interativo em TypeScript (Vite + React).**

---

## 📌 Visão Geral do Projeto

O **NexaReviews AI** é uma solução completa ponta a ponta desenvolvida para automatizar e acelerar a classificação de sentimentos (**positivo** ou **negativo**) em avaliações de produtos em plataformas de e-commerce.

A plataforma integra:
1. **Pipeline de NLP & Machine Learning:** Vetorização estatística via TF-IDF e classificação linear calibrada com Regressão Logística.
2. **API Backend RESTful (FastAPI):** Servidor assíncrono com Uvicorn, validação estrita de esquemas via Pydantic, CORS configurado e ciclo de vida otimizado.
3. **Frontend Interativo (Vite + React + TypeScript):** Interface web moderna, responsiva, estilizada com tema escuro (Dark Slate) e efeitos de Glassmorphism, medidor de probabilidade em tempo real e histórico de análises.

---

## 🏗️ Arquitetura da Solução

```
[ Usuário / Navegador ]
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│     Frontend Web (React 18 + TypeScript + Vite)         │
│  - ReviewAnalyzer Component (Textarea & Validações)     │
│  - Indicadores Visuais (Badges Verde/Positivo e Vermelho/Negativo)
│  - Medidor de Confiança e Histórico em LocalStorage     │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP POST /predict (JSON)
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Backend API (FastAPI + Uvicorn)            │
│  - CORSMiddleware (http://localhost:5173)               │
│  - Pydantic Request/Response Models                     │
│  - Endpoint GET /health & POST /predict                 │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│          Pipeline de NLP e Modelo Pré-Treinado          │
│  1. TextCleaner: Normalização NFKD, Regex, Minúsculas   │
│  2. TF-IDF Vectorizer: N-grams (1 e 2 termos, 5000 feat)│
│  3. Regressão Logística: Previsão de classe e proba     │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura do Projeto

```text
NexaReviews-AI/
│
├── data/
│   ├── raw/
│   │   └── dataset.csv                     # Dados brutos das avaliações
│   └── processed/
│       └── dataset_cleaned.csv             # Dados tratados com coluna texto_limpo
│
├── models/
│   ├── modelo_sentimentos.pkl              # Modelo treinado e serializado via Joblib
│   ├── sentiment_model.pkl                 # Cópia compatível do pipeline serializado
│   └── distribuicao_sentimentos.png        # Gráfico estatístico gerado com Seaborn
│
├── notebooks/
│   └── 01_analise_exploratoria.ipynb       # Análise exploratória e experimentos
│
├── src/
│   ├── __init__.py                         # Inicializador do pacote e exportações
│   ├── text_cleaner.py                     # Classe TextCleaner (normalização e regex)
│   ├── data_processor.py                   # Classe DataProcessor (carga, auditoria e limpeza)
│   ├── model_pipeline.py                   # Classe SentimentModel (TF-IDF + Regressão Logística)
│   └── api.py                              # [NOVO] API Backend RESTful com FastAPI
│
├── frontend/                               # [NOVO] Aplicação Web em TypeScript
│   ├── src/
│   │   ├── components/
│   │   │   ├── ReviewAnalyzer.tsx          # Componente principal de análise e badges
│   │   │   ├── Header.tsx                  # Cabeçalho com indicador de status da API
│   │   │   ├── HistoryList.tsx             # Histórico de avaliações analisadas
│   │   │   └── MetricsCards.tsx            # Cards explicativos da arquitetura
│   │   ├── services/
│   │   │   └── api.ts                      # Cliente tipado de comunicação com a API
│   │   ├── App.tsx                         # Componente raiz da aplicação
│   │   ├── main.tsx                        # Ponto de entrada do React
│   │   ├── index.css                       # Sistema de design moderno e responsivo
│   │   └── vite-env.d.ts                   # Definições de tipos do Vite
│   ├── index.html                          # HTML com fontes Google (Outfit / Inter)
│   ├── package.json                        # Dependências e scripts do Frontend
│   ├── tsconfig.json                       # Configurações do TypeScript
│   ├── tsconfig.node.json                  # Configuração do compilador Node/Vite
│   └── vite.config.ts                      # Configurações do servidor de desenvolvimento
│
├── requirements.txt                        # Dependências Python (ML + FastAPI + Uvicorn)
├── README.md                               # Documentação técnica completa
└── main.py                                 # Pipeline ponta a ponta de treino e inferência
```

---

## ⚙️ Especificação Técnica da API (`src/api.py`)

A API foi projetada para alta disponibilidade e tolerância a falhas, com inicialização automática do modelo e suporte a CORS para o frontend local.

### Endpoints Disponíveis:

#### 1. `GET /health`
Verifica se a API e o modelo preditivo estão prontos para inferência.
- **Resposta (`200 OK`):**
  ```json
  {
    "status": "ok",
    "model_loaded": true,
    "model_path": "models/modelo_sentimentos.pkl"
  }
  ```

#### 2. `POST /predict`
Executa o pré-processamento de texto (`TextCleaner.clean_text`) e a classificação de sentimento.
- **Request Body:**
  ```json
  {
    "text": "Produto excelente, entrega super rápida e recomendo muito!"
  }
  ```
- **Response Body (`200 OK`):**
  ```json
  {
    "sentiment": "positivo",
    "clean_text": "produto excelente entrega super rapida e recomendo muito",
    "confidence": 0.9824,
    "probabilities": {
      "positivo": 0.9824,
      "negativo": 0.0176
    }
  }
  ```

#### 3. `GET /docs` (Swagger UI) & `GET /redoc`
Documentação interativa OpenAPI gerada automaticamente pelo FastAPI.

---

## 💻 Interface Web Interativa (`frontend/`)

O frontend oferece uma experiência de usuário rica e fluida:
- 📝 **Área de Digitação:** Campo de texto dinâmico com contagem de caracteres e palavras.
- 💡 **Exemplos Rápidos:** Botões de teste rápido com avaliações positivas e negativas.
- 🟢 **Badge Positivo:** Destaque em verde esmeralda com ícone de tendência alta.
- 🔴 **Badge Negativo:** Destaque em vermelho carmim com ícone de alerta.
- 📊 **Distribuição de Probabilidade:** Barra de progresso visual com a certeza do modelo.
- 🧹 **Preview do Texto Higienizado:** Visualização do texto após a etapa de limpeza do NLP.
- 📜 **Histórico de Avaliações:** Persistência automática das análises recentes com clique para reanálise.
- 📡 **Monitor de Conexão:** Verificação automática e periódica do status do backend FastAPI.

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
- **Python 3.10+** (recomendado Python 3.10 a 3.13)
- **Node.js 18+** e **npm**

---

### 2. Configuração do Backend (Python / FastAPI)

1. Clone ou acesse o diretório raiz do projeto:
   ```bash
   cd NexaReviewsAI
   ```

2. Crie e ative o ambiente virtual (opcional, mas recomendado):
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Instale as dependências do projeto:
   ```bash
   pip install -r requirements.txt
   ```

4. *(Opcional)* Treine o modelo executando o script principal:
   ```bash
   python main.py
   ```
   > **Nota:** A API também conta com carregamento automático inteligente; caso o arquivo `.pkl` ainda não exista, ela treina e salva o modelo automaticamente ao iniciar.

5. Inicie o servidor da API FastAPI:
   ```bash
   uvicorn src.api:app --reload
   ```
   A API estará disponível em: **`http://localhost:8000`**  
   Documentação interativa Swagger: **`http://localhost:8000/docs`**

---

### 3. Configuração do Frontend (Vite + React + TypeScript)

1. Abra um novo terminal e navegue até a pasta `frontend`:
   ```bash
   cd frontend
   ```

2. Instale os pacotes npm:
   ```bash
   npm install
   ```

3. Inicie o servidor de desenvolvimento do Vite:
   ```bash
   npm run dev
   ```

4. Acesse a aplicação no seu navegador:
   👉 **`http://localhost:5173`**

---

## 🧪 Exemplos de Teste via cURL / Terminal

### Verificação de Saúde (Health Check):
```bash
curl -X GET "http://localhost:8000/health"
```

### Análise de Review Positivo:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Amei o produto, entrega super rápida e qualidade excelente!"}'
```

### Análise de Review Negativo:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Péssimo produto, quebrou no primeiro dia e não recomendo."}'
```

---

## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologias |
|---|---|
| **Machine Learning & NLP** | Python, Scikit-Learn, Pandas, NumPy, Joblib, Regex, Unicode NFKD |
| **Backend API** | FastAPI, Uvicorn, Pydantic, CORSMiddleware |
| **Frontend Web** | React 18, TypeScript, Vite, Lucide React, Modern CSS (Glassmorphism) |
| **Visualização & Análise** | Matplotlib, Seaborn, Jupyter Notebook |
| **Controle de Versão** | Git |

---

## 📄 Licença

Este projeto é de código aberto sob a licença [MIT](LICENSE). Sinta-se livre para usar, estudar e evoluir!
