"""
Módulo de processamento e preparação de dados para NLP.

Este módulo contém a classe DataProcessor, responsável por carregar os dados brutos,
inspecionar a integridade das informações e aplicar o pipeline de limpeza aos reviews.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd

from src.text_cleaner import TextCleaner


class DataProcessor:
    """
    Classe responsável pelo carregamento, inspeção e pré-processamento de datasets de reviews.

    Attributes:
        file_path (Path): Caminho para o arquivo CSV de entrada.
        df (pd.DataFrame): DataFrame contendo os dados carregados e/ou processados.
    """

    def __init__(self, file_path: str = "data/raw/dataset.csv") -> None:
        """
        Inicializa o DataProcessor com o caminho do dataset.

        Args:
            file_path (str): Caminho relativo ou absoluto para o arquivo CSV.
        """
        self.file_path = Path(file_path)
        self.df: Optional[pd.DataFrame] = None

    def load_data(self) -> pd.DataFrame:
        """
        Carrega o arquivo CSV a partir do caminho especificado.

        Returns:
            pd.DataFrame: DataFrame com os dados brutos carregados.

        Raises:
            FileNotFoundError: Se o arquivo não for encontrado no caminho especificado.
            ValueError: Se o arquivo estiver vazio ou inválido.
        """
        if not self.file_path.exists():
            raise FileNotFoundError(
                f"Arquivo de dados não encontrado no caminho: {self.file_path.resolve()}"
            )

        print(f"[INFO] Carregando dataset a partir de: {self.file_path}")
        self.df = pd.read_csv(self.file_path)
        print(f"[INFO] Dataset carregado com sucesso. Total de linhas: {len(self.df)}")
        return self.df

    def get_info(self) -> Dict[str, Any]:
        """
        Exibe e retorna o formato (shape) do DataFrame e a contagem de valores nulos por coluna.

        Returns:
            Dict[str, Any]: Dicionário contendo shape, colunas e contagem de nulos.

        Raises:
            ValueError: Se o dataset ainda não tiver sido carregado.
        """
        if self.df is None:
            raise ValueError("O dataset ainda não foi carregado. Execute load_data() primeiro.")

        shape = self.df.shape
        null_counts = self.df.isnull().sum().to_dict()

        print("\n" + "=" * 50)
        print("          INFORMAÇÕES DO DATASET")
        print("=" * 50)
        print(f"Dimensões (Linhas, Colunas): {shape}")
        print("\nValores Nulos por Coluna:")
        for col, nulos in null_counts.items():
            pct = (nulos / shape[0]) * 100 if shape[0] > 0 else 0
            print(f" - {col:20s}: {nulos:5d} ({pct:5.2f}%)")
        print("=" * 50 + "\n")

        return {
            "shape": shape,
            "columns": list(self.df.columns),
            "null_counts": null_counts,
        }

    def clean_data(
        self,
        text_column: str = "texto_review",
        target_column: Optional[str] = "sentimento",
        save_path: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Trata valores ausentes, aplica a limpeza de texto via TextCleaner e gera a coluna 'texto_limpo'.

        Args:
            text_column (str): Nome da coluna contendo os textos dos reviews. Padrão: 'texto_review'.
            target_column (Optional[str]): Nome da coluna alvo de sentimento. Padrão: 'sentimento'.
            save_path (Optional[str]): Caminho opcional para salvar o CSV processado.

        Returns:
            pd.DataFrame: DataFrame processado com a coluna 'texto_limpo' adicionada e nulos tratados.

        Raises:
            ValueError: Se o dataset não foi carregado ou a coluna especificada não existir.
        """
        if self.df is None:
            raise ValueError("O dataset ainda não foi carregado. Execute load_data() primeiro.")

        if text_column not in self.df.columns:
            raise ValueError(
                f"Coluna '{text_column}' não encontrada no DataFrame. Colunas disponíveis: {list(self.df.columns)}"
            )

        print(f"[INFO] Iniciando tratamento e limpeza na coluna '{text_column}'...")
        initial_len = len(self.df)

        # 1. Remover valores nulos na coluna de texto e na coluna alvo
        cols_to_check = [text_column]
        if target_column and target_column in self.df.columns:
            cols_to_check.append(target_column)

        self.df = self.df.dropna(subset=cols_to_check).copy()
        dropped_nulls = initial_len - len(self.df)
        if dropped_nulls > 0:
            print(f"[INFO] Removidas {dropped_nulls} linhas com valores nulos.")

        # 2. Aplicar a limpeza de texto
        self.df["texto_limpo"] = self.df[text_column].astype(str).apply(TextCleaner.clean_text)

        # 3. Filtrar registros onde o texto limpo 
        valid_mask = self.df["texto_limpo"].str.strip().str.len() > 0
        dropped_empty = len(self.df) - valid_mask.sum()
        self.df = self.df[valid_mask].reset_index(drop=True)

        if dropped_empty > 0:
            print(f"[INFO] Removidos {dropped_empty} registros que ficaram vazios após a higienização.")

        print(f"[INFO] Processamento concluído! Registros finais válidos: {len(self.df)}")

        # 4. Salvar dataset processado se solicitado
        if save_path:
            out_file = Path(save_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            self.df.to_csv(out_file, index=False, encoding="utf-8")
            print(f"[INFO] Dataset processado salvo com sucesso em: {out_file}")

        return self.df
