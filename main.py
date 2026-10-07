"""
NexaReviews AI - Pipeline Principal de Execução.

Este script executa o fluxo ponta a ponta:
1. Verificação e criação dos diretórios necessários.
2. Carregamento dos dados brutos com DataProcessor.
3. Exibição de informações e diagnóstico do dataset.
4. Higienização e padronização dos textos com TextCleaner via DataProcessor.
5. Geração e salvamento do gráfico de distribuição de classes com Seaborn/Matplotlib.
6. Divisão de dados, treinamento do pipeline TF-IDF + Logistic Regression e avaliação completa.
7. Persistência do modelo treinado em formato .pkl no diretório models/.
8. Demonstração de inferência em tempo real com novos reviews de exemplo.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_processor import DataProcessor
from src.model_pipeline import SentimentModel


def create_directories() -> None:
    """Cria os diretórios do projeto caso ainda não existam."""
    directories = [
        Path("data/raw"),
        Path("data/processed"),
        Path("models"),
        Path("notebooks"),
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    print("[INFO] Estrutura de diretórios validada com sucesso.")


def plot_sentiment_distribution(df, target_column: str = "sentimento", output_path: str = "models/distribuicao_sentimentos.png") -> None:
    """
    Gera e salva o gráfico de contagem (countplot) da distribuição de classes de sentimento.

    Args:
        df: DataFrame com os dados.
        target_column (str): Nome da coluna alvo.
        output_path (str): Caminho para salvar a imagem do gráfico.
    """
    print(f"\n[INFO] Gerando visualização da distribuição de classes ('{target_column}')...")
    
    # Configuração estética do Seaborn
    sns.set_theme(style="whitegrid", palette="muted")
    fig, ax = plt.subplots(figsize=(8, 5))

    palette_colors = {"positivo": "#2ecc71", "negativo": "#e74c3c"}
    # Verifica se as classes no dataframe coincidem com a paleta
    unique_classes = df[target_column].unique()
    custom_palette = [palette_colors.get(c, "#3498db") for c in unique_classes]

    sns.countplot(
        data=df,
        x=target_column,
        palette=custom_palette,
        hue=target_column,
        legend=False,
        ax=ax,
    )

    ax.set_title("NexaReviews AI - Distribuição das Classes de Sentimento", fontsize=14, weight="bold", pad=15)
    ax.set_xlabel("Sentimento", fontsize=12, labelpad=10)
    ax.set_ylabel("Quantidade de Reviews", fontsize=12, labelpad=10)

    # Adicionar rótulos numéricos sobre as barras
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(
            f"{int(height)}",
            (p.get_x() + p.get_width() / 2.0, height),
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="semibold",
            xytext=(0, 4),
            textcoords="offset points",
        )

    plt.tight_layout()
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_file, dpi=300)
    print(f"[INFO] Gráfico salvo com sucesso em: {out_file.resolve()}")
    plt.close()


def main() -> None:
    """Função principal que orquestra o pipeline completo."""
    print("=" * 70)
    print("                 NEXAREVIEWS AI - PIPELINE DE ML")
    print("=" * 70)

    # 1. Garantir diretórios
    create_directories()

    # 2. Carregar dados brutos
    raw_data_path = "data/raw/dataset.csv"
    processor = DataProcessor(file_path=raw_data_path)
    processor.load_data()

    # 3. Exibir diagnóstico e estatísticas básicas
    processor.get_info()

    # 4. Tratar nulos e aplicar limpeza com TextCleaner
    processed_data_path = "data/processed/dataset_cleaned.csv"
    df_clean = processor.clean_data(
        text_column="texto_review",
        target_column="sentimento",
        save_path=processed_data_path,
    )

    # 5. Visualizar distribuição das classes com Seaborn
    plot_sentiment_distribution(
        df=df_clean,
        target_column="sentimento",
        output_path="models/distribuicao_sentimentos.png",
    )

    # 6. Treinamento e avaliação do modelo
    model = SentimentModel(max_features=5000, random_state=42)
    X = df_clean["texto_limpo"]
    y = df_clean["sentimento"]

    metrics = model.train(X=X, y=y, test_size=0.2, random_state=42)

    # 7. Salvar artefato do modelo
    model_output_path = "models/modelo_sentimentos.pkl"
    model.save_model(filepath=model_output_path)
    model.save_model(filepath="models/sentiment_model.pkl")

    # 8. Demonstração de inferência em tempo real
    print("\n" + "=" * 70)
    print("          DEMONSTRAÇÃO DE INFERÊNCIA EM NOVOS REVIEWS")
    print("=" * 70)

    novos_reviews = [
        "Amei o produto, entrega super rápida e qualidade excelente!",
        "Péssimo atendimento, o produto veio quebrado e não recomendo.",
        "Chegou dentro do prazo e funciona direitinho. Recomendo a compra.",
        "Não comprem, material muito frágil e estragou em dois dias.",
    ]

    for review in novos_reviews:
        # Limpeza do novo review
        from src.text_cleaner import TextCleaner
        review_limpo = TextCleaner.clean_text(review)
        pred = model.predict(review_limpo)[0]
        prob = model.predict_proba(review_limpo)[0]
        classes = model.pipeline.classes_
        prob_dict = {cls: f"{p * 100:.1f}%" for cls, p in zip(classes, prob)}

        print(f"\nReview Original: \"{review}\"")
        print(f"Texto Limpo    : \"{review_limpo}\"")
        print(f"Classificação  : >>> {pred.upper()} <<< | Probabilidades: {prob_dict}")

    print("\n" + "=" * 70)
    print("    PIPELINE NEXAREVIEWS AI EXECUTADO COM SUCESSO TOTAL!")
    print("=" * 70)


if __name__ == "__main__":
    main()
