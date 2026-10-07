"""
NexaReviews AI - Pacote de Processamento de Linguagem Natural e Classificação de Sentimentos.

Este pacote fornece módulos para limpeza de texto, ingestão e pré-processamento de dados,
pipeline de modelagem preditiva utilizando TF-IDF e Regressão Logística, além da API FastAPI.
"""

from src.text_cleaner import TextCleaner
from src.data_processor import DataProcessor
from src.model_pipeline import SentimentModel
from src.api import app

__version__ = "1.0.0"
__all__ = ["TextCleaner", "DataProcessor", "SentimentModel", "app"]
