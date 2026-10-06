"""
Módulo do pipeline de Machine Learning para Análise de Sentimentos.

Este módulo encapsula a classe SentimentModel, que implementa um pipeline completo do
Scikit-Learn (TF-IDF + Regressão Logística) para treinamento, avaliação, persistência e inferência.
"""

from pathlib import Path
from typing import Union, Tuple, Dict, Any, Sequence, Optional
import numpy as np
import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)


class SentimentModel:
    """
    Classe para encapsular o pipeline de NLP e Classificação de Sentimentos.

    Utiliza TfidfVectorizer para vetorização e LogisticRegression para modelagem estatística.

    Attributes:
        pipeline (Pipeline): Pipeline do Scikit-Learn (TF-IDF + Regressão Logística).
        is_trained (bool): Indicador se o modelo foi treinado ou carregado.
    """

    def __init__(
        self,
        max_features: int = 5000,
        random_state: int = 42,
        c_param: float = 1.0,
        max_iter: int = 1000,
    ) -> None:
        """
        Inicializa o SentimentModel construindo o Pipeline do Scikit-Learn.

        Args:
            max_features (int): Quantidade máxima de features no TF-IDF. Padrão: 5000.
            random_state (int): Semente de aleatoriedade para reprodutibilidade. Padrão: 42.
            c_param (float): Parâmetro de regularização inversa do LogisticRegression. Padrão: 1.0.
            max_iter (int): Número máximo de iterações do otimizador. Padrão: 1000.
        """
        self.pipeline: Pipeline = Pipeline(
            steps=[
                (
                    "tfidf",
                    TfidfVectorizer(
                        max_features=max_features,
                        ngram_range=(1, 2),
                        sublinear_tf=True,
                    ),
                ),
                (
                    "classifier",
                    LogisticRegression(
                        C=c_param,
                        random_state=random_state,
                        max_iter=max_iter,
                        solver="lbfgs",
                    ),
                ),
            ]
        )
        self.is_trained: bool = False

    def train(
        self,
        X: Union[pd.Series, Sequence[str]],
        y: Union[pd.Series, Sequence[Union[str, int]]],
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """
        Divide os dados em conjuntos de treino e teste, treina o pipeline e avalia o desempenho.

        Args:
            X (Union[pd.Series, Sequence[str]]): Textos pré-processados (features).
            y (Union[pd.Series, Sequence[Union[str, int]]]): Rótulos/classes de sentimento (target).
            test_size (float): Proporção da base destinada para teste. Padrão: 0.2 (20%).
            random_state (int): Semente para divisão estratificada dos dados. Padrão: 42.

        Returns:
            Dict[str, Any]: Dicionário contendo as métricas de avaliação e conjuntos particionados.
        """
        print("\n" + "=" * 60)
        print("          INICIANDO TREINAMENTO DO MODELO")
        print("=" * 60)
        print(f"[INFO] Total de amostras: {len(X)}")
        print(f"[INFO] Divisão treino/teste: {(1 - test_size) * 100:.0f}% / {test_size * 100:.0f}%")

        # Divisão estratificada para manter proporção de classes
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
            stratify=y,
        )

        print(f"[INFO] Treinando pipeline (TF-IDF + LogisticRegression) em {len(X_train)} amostras...")
        self.pipeline.fit(X_train, y_train)
        self.is_trained = True
        print("[INFO] Treinamento finalizado com sucesso!")

        print("\n[INFO] Realizando predições na base de teste...")
        y_pred = self.pipeline.predict(X_test)

        # Avaliação
        metrics = self.evaluate(y_true=y_test, y_pred=y_pred)
        metrics["X_train"] = X_train
        metrics["X_test"] = X_test
        metrics["y_train"] = y_train
        metrics["y_test"] = y_test
        metrics["y_pred"] = y_pred

        return metrics

    def evaluate(
        self,
        y_true: Union[pd.Series, Sequence[Union[str, int]], np.ndarray],
        y_pred: Union[pd.Series, Sequence[Union[str, int]], np.ndarray],
    ) -> Dict[str, Any]:
        """
        Calcula e exibe a acurácia, relatório de classificação e matriz de confusão.

        Args:
            y_true: Rótulos reais.
            y_pred: Rótulos preditos pelo modelo.

        Returns:
            Dict[str, Any]: Dicionário com métricas calculadas.
        """
        acc = accuracy_score(y_true, y_pred)
        report_str = classification_report(y_true, y_pred)
        report_dict = classification_report(y_true, y_pred, output_dict=True)
        cm = confusion_matrix(y_true, y_pred)

        print("\n" + "=" * 60)
        print("              AVALIAÇÃO DO MODELO")
        print("=" * 60)
        print(f"Acurácia Geral: {acc * 100:.2f}%\n")
        print("Relatório de Classificação:")
        print(report_str)
        print("Matriz de Confusão:")
        print(cm)
        print("=" * 60 + "\n")

        return {
            "accuracy": acc,
            "classification_report_str": report_str,
            "classification_report_dict": report_dict,
            "confusion_matrix": cm,
        }

    def predict(self, X: Union[str, Sequence[str], pd.Series]) -> np.ndarray:
        """
        Realiza predições de classe de sentimento para um ou mais textos.

        Args:
            X (Union[str, Sequence[str], pd.Series]): Texto ou coleção de textos pré-processados.

        Returns:
            np.ndarray: Classes preditas ('positivo', 'negativo', etc.).
        """
        if not self.is_trained:
            raise RuntimeError("O modelo precisa ser treinado ou carregado antes de fazer predições.")

        if isinstance(X, str):
            X = [X]

        return self.pipeline.predict(X)

    def predict_proba(self, X: Union[str, Sequence[str], pd.Series]) -> np.ndarray:
        """
        Retorna as probabilidades calculadas para cada classe.

        Args:
            X (Union[str, Sequence[str], pd.Series]): Texto ou coleção de textos.

        Returns:
            np.ndarray: Matriz de probabilidades de cada classe.
        """
        if not self.is_trained:
            raise RuntimeError("O modelo precisa ser treinado ou carregado antes de fazer predições.")

        if isinstance(X, str):
            X = [X]

        return self.pipeline.predict_proba(X)

    def save_model(self, filepath: str = "models/sentiment_model.pkl") -> Path:
        """
        Salva o pipeline treinado em disco utilizando a biblioteca joblib.

        Args:
            filepath (str): Caminho onde o arquivo .pkl será salvo.

        Returns:
            Path: Caminho do arquivo salvo.
        """
        if not self.is_trained:
            raise RuntimeError("Não é possível salvar um modelo não treinado.")

        out_path = Path(filepath)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(self.pipeline, out_path)
        print(f"[INFO] Modelo salvo com sucesso em: {out_path.resolve()}")
        return out_path

    def load_model(self, filepath: str = "models/sentiment_model.pkl") -> Pipeline:
        """
        Carrega um modelo pré-treinado do disco.

        Args:
            filepath (str): Caminho do arquivo .pkl do modelo.

        Returns:
            Pipeline: O pipeline do Scikit-Learn carregado.
        """
        in_path = Path(filepath)
        if not in_path.exists():
            raise FileNotFoundError(f"Arquivo do modelo não encontrado: {in_path.resolve()}")

        self.pipeline = joblib.load(in_path)
        self.is_trained = True
        print(f"[INFO] Modelo carregado com sucesso de: {in_path.resolve()}")
        return self.pipeline
