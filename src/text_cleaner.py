"""
Módulo de limpeza e normalização de texto para NLP.

Este módulo contém a classe TextCleaner projetada para padronizar textos de avaliações (reviews),
removendo ruídos, acentuações, caracteres especiais, números e espaços redundantes.
"""

import re
import unicodedata


class TextCleaner:
    """
    Classe utilitária para higienização e padronização de textos em pipelines de NLP.
    """

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Executa a limpeza completa de uma string de texto.

        Etapas realizadas:
        1. Validação de tipo e conversão segura para string.
        2. Conversão de todos os caracteres para letras minúsculas.
        3. Remoção de acentuação gráfica utilizando normalização Unicode (NFKD).
        4. Remoção de pontuações, caracteres especiais e números (mantém apenas letras e espaços).
        5. Remoção de múltiplos espaços em branco e espaços nas extremidades (strip).

        Args:
            text (str): Texto original a ser higienizado.

        Returns:
            str: Texto limpo, normalizado e sem caracteres especiais ou números.

        Example:
            >>> cleaner = TextCleaner()
            >>> cleaner.clean_text("Ótimo produto! Entrega 100% rápida e recomendo muito!!")
            'otimo produto entrega rapida e recomendo muito'
        """
        if text is None or not isinstance(text, str):
            return ""

        # 1. Converter para minúsculas
        cleaned = text.lower()

        # 2. Remover acentos via unicodedata 
        cleaned = unicodedata.normalize("NFKD", cleaned)
        cleaned = "".join([c for c in cleaned if not unicodedata.combining(c)])

        # 3. Remover caracteres especiais
        cleaned = re.sub(r"[^a-zA-Z\s]", " ", cleaned)

        # 4. Remover múltiplos espaços internos e espaços nas extremidades
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return cleaned
