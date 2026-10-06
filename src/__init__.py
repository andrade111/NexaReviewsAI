"""
NexaReviews AI - Pacote de Processamento de Linguagem Natural e Classificação de Sentimentos.

Este pacote fornece módulos para limpeza de texto, ingestão e pré-processamento de dados,
e pipeline de modelagem preditiva utilizando TF-IDF e Regressão Logística.
"""

from src.text_cleaner import TextCleaner
from src.data_processor import DataProcessor
from src.model_pipeline import SentimentModel

__version__ = "1.0.0"
__all__ = ["TextCleaner", "DataProcessor", "SentimentModel"]
