"""
API Backend para Classificação de Sentimentos em Avaliações - NexaReviews AI.

Este módulo implementa uma API RESTful utilizando FastAPI e Uvicorn,
fornecendo endpoints para verificação de integridade (/health) e predição
de sentimentos (/predict) com base em modelos de Machine Learning pré-treinados.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional, Dict, Any, List
import os

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.text_cleaner import TextCleaner
from src.model_pipeline import SentimentModel
from src.data_processor import DataProcessor


# -----------------------------------------------------------------------------
# Esquemas Pydantic para Validação de Dados (Request / Response)
# -----------------------------------------------------------------------------

class ReviewRequest(BaseModel):
    """Esquema de entrada para requisição de análise de sentimento."""
    text: str = Field(
        ...,
        min_length=1,
        description="Texto da avaliação do produto a ser analisado",
        examples=["Produto excelente! Chegou muito rápido e atendeu todas as expectativas."]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Produto maravilhoso, entrega rápida e super recomendo!"
                }
            ]
        }
    }


class ReviewResponse(BaseModel):
    """Esquema de resposta com o sentimento classificado e detalhes da inferência."""
    sentiment: str = Field(
        ...,
        description="Classificação do sentimento predito ('positivo' ou 'negativo')",
        examples=["positivo"]
    )
    clean_text: str = Field(
        ...,
        description="Texto da avaliação após higienização e normalização",
        examples=["produto maravilhoso entrega rapida e super recomendo"]
    )
    confidence: Optional[float] = Field(
        default=None,
        description="Nível de confiança da classificação (0.0 a 1.0)",
        examples=[0.985]
    )
    probabilities: Optional[Dict[str, float]] = Field(
        default=None,
        description="Distribuição de probabilidades por classe",
        examples=[{"positivo": 0.985, "negativo": 0.015}]
    )


class HealthResponse(BaseModel):
    """Esquema de resposta para o endpoint de integridade do serviço."""
    status: str = Field(default="ok", description="Status operacional da API")
    model_loaded: bool = Field(..., description="Indica se o modelo preditivo está pronto em memória")
    model_path: Optional[str] = Field(default=None, description="Caminho do arquivo do modelo carregado")


# -----------------------------------------------------------------------------
# Gerenciamento de Estado Global do Modelo de ML
# -----------------------------------------------------------------------------

class ModelService:
    """Serviço singleton para carregamento e inferência com o modelo de NLP."""
    
    def __init__(self):
        self.model: Optional[SentimentModel] = None
        self.model_file_used: Optional[str] = None

    def find_and_load_model(self) -> bool:
        """
        Tenta carregar o modelo a partir dos caminhos candidatos padrão.
        Se nenhum modelo existir, treina automaticamente usando data/raw/dataset.csv.
        """
        candidate_paths = [
            Path("models/modelo_sentimentos.pkl"),
            Path("models/sentiment_model.pkl"),
            Path("../models/modelo_sentimentos.pkl"),
            Path("../models/sentiment_model.pkl"),
        ]

        # 1. Tenta carregar arquivo existente
        for path in candidate_paths:
            if path.exists():
                try:
                    sentiment_model = SentimentModel()
                    sentiment_model.load_model(str(path))
                    self.model = sentiment_model
                    self.model_file_used = str(path.resolve())
                    print(f"[API INFO] Modelo carregado com sucesso de: {self.model_file_used}")
                    return True
                except Exception as exc:
                    print(f"[API WARN] Falha ao carregar modelo de {path}: {exc}")

        # 2. Se não encontrar modelo treinado, tenta treinar a partir de data/raw/dataset.csv
        data_paths = [
            Path("data/raw/dataset.csv"),
            Path("../data/raw/dataset.csv"),
        ]
        
        for dpath in data_paths:
            if dpath.exists():
                try:
                    print(f"[API INFO] Modelo salvo não encontrado. Treinando novo modelo com {dpath}...")
                    processor = DataProcessor(file_path=str(dpath))
                    processor.load_data()
                    df_clean = processor.clean_data()
                    
                    sentiment_model = SentimentModel(max_features=5000, random_state=42)
                    sentiment_model.train(
                        X=df_clean["texto_limpo"],
                        y=df_clean["sentimento"],
                        test_size=0.2,
                        random_state=42
                    )
                    
                    # Salva em ambos os nomes para garantir compatibilidade
                    save_path_1 = Path("models/modelo_sentimentos.pkl")
                    save_path_2 = Path("models/sentiment_model.pkl")
                    save_path_1.parent.mkdir(parents=True, exist_ok=True)
                    sentiment_model.save_model(str(save_path_1))
                    sentiment_model.save_model(str(save_path_2))
                    
                    self.model = sentiment_model
                    self.model_file_used = str(save_path_1.resolve())
                    print(f"[API INFO] Modelo treinado e salvo com sucesso em: {self.model_file_used}")
                    return True
                except Exception as exc:
                    print(f"[API ERROR] Falha ao treinar modelo automático: {exc}")

        print("[API ERROR] Não foi possível carregar nem treinar o modelo de sentimentos.")
        return False

    def predict(self, raw_text: str) -> Dict[str, Any]:
        """
        Executa a higienização do texto e a classificação preditiva.
        """
        if not self.model or not self.model.is_trained:
            # Tenta carregar novamente sob demanda
            if not self.find_and_load_model():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Modelo preditivo não disponível no momento. Execute o treinamento primeiro."
                )

        clean_text = TextCleaner.clean_text(raw_text)
        
        # Se após a limpeza o texto ficar totalmente vazio
        if not clean_text or len(clean_text.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O texto fornecido não contém caracteres alfabéticos válidos para análise."
            )

        try:
            pred = self.model.predict(clean_text)[0]
            sentiment_str = str(pred).lower()
            
            probabilities_dict = {}
            confidence = None
            
            # Cálculo de probabilidades se suportado pelo pipeline
            try:
                probs = self.model.predict_proba(clean_text)[0]
                classes = self.model.pipeline.classes_
                for cls_name, p in zip(classes, probs):
                    probabilities_dict[str(cls_name).lower()] = round(float(p), 4)
                
                # Confiança na classe vencedora
                if sentiment_str in probabilities_dict:
                    confidence = probabilities_dict[sentiment_str]
                else:
                    confidence = round(float(max(probs)), 4)
            except Exception:
                probabilities_dict = None
                confidence = None

            return {
                "sentiment": sentiment_str,
                "clean_text": clean_text,
                "confidence": confidence,
                "probabilities": probabilities_dict,
            }
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno durante a inferência do modelo: {str(exc)}"
            )


# Instância global do serviço de modelo
model_service = ModelService()


# -----------------------------------------------------------------------------
# Ciclo de Vida da Aplicação (Lifespan Context Manager)
# -----------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia a inicialização e o encerramento da API FastAPI."""
    print("[API LIFESPAN] Inicializando API NexaReviews AI...")
    model_service.find_and_load_model()
    yield
    print("[API LIFESPAN] Encerrando API NexaReviews AI...")


# -----------------------------------------------------------------------------
# Instanciação do FastAPI e Middlewares
# -----------------------------------------------------------------------------

app = FastAPI(
    title="NexaReviews AI - Sentiment Analysis API",
    description=(
        "API de alta performance para inferência em tempo real de sentimentos "
        "em avaliações de e-commerce utilizando Natural Language Processing (NLP) "
        "e Machine Learning (Scikit-Learn TF-IDF + Regressão Logística)."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS para permitir requisições do frontend Vite/React
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Endpoints da API
# -----------------------------------------------------------------------------

@app.get(
    "/",
    summary="Informações da API",
    tags=["Root"]
)
async def root() -> Dict[str, Any]:
    """Retorna dados gerais sobre a API e links para documentação interativa."""
    return {
        "app": "NexaReviews AI - Análise Inteligente de Sentimentos",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "predict": "/predict"
        }
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificação de Integridade (Health Check)",
    tags=["Health"]
)
async def health_check() -> HealthResponse:
    """
    Retorna o status operacional da API e a disponibilidade do modelo preditivo em memória.
    """
    is_loaded = (model_service.model is not None and model_service.model.is_trained)
    return HealthResponse(
        status="ok",
        model_loaded=is_loaded,
        model_path=model_service.model_file_used
    )


@app.post(
    "/predict",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Predição de Sentimento em Avaliação",
    tags=["Inference"]
)
async def predict_sentiment(request: ReviewRequest) -> ReviewResponse:
    """
    Recebe o texto de uma avaliação, aplica o pré-processamento/higienização de texto
    e retorna o sentimento predito ('positivo' ou 'negativo') com métricas de probabilidade.
    """
    result = model_service.predict(request.text)
    return ReviewResponse(
        sentiment=result["sentiment"],
        clean_text=result["clean_text"],
        confidence=result.get("confidence"),
        probabilities=result.get("probabilities")
    )


# -----------------------------------------------------------------------------
# Bloco de Execução Direta
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)
