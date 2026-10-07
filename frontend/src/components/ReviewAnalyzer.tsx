import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Send,
  Trash2,
  CheckCircle2,
  AlertTriangle,
  Copy,
  Check,
  TrendingUp,
  TrendingDown,
  Info,
  RefreshCw
} from 'lucide-react';
import { predictSentiment, SentimentResponse, ApiError } from '../services/api';

interface ReviewAnalyzerProps {
  onAnalysisComplete?: (result: SentimentResponse, originalText: string) => void;
  isBackendOnline?: boolean | null;
  onRefreshHealth?: () => void;
}

const SAMPLE_REVIEWS = [
  {
    label: '⭐ Positivo (Elogio)',
    text: 'Amei o produto, entrega super rápida e a qualidade é fantástica! Super recomendo a todos.',
  },
  {
    label: '⭐ Positivo (Funcional)',
    text: 'Chegou dentro do prazo estabelecido, bem embalado e funcionando 100% como no anúncio.',
  },
  {
    label: '⚠️ Negativo (Defeito)',
    text: 'Péssima experiência de compra. O produto veio quebrado, acabamento frágil e suporte não responde.',
  },
  {
    label: '⚠️ Negativo (Atraso/Ruim)',
    text: 'Não comprem de jeito nenhum! Demorou mais de um mês para chegar e o material é de baixíssima qualidade.',
  },
];

export const ReviewAnalyzer: React.FC<ReviewAnalyzerProps> = ({
  onAnalysisComplete,
  isBackendOnline,
  onRefreshHealth,
}) => {
  const [reviewText, setReviewText] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [result, setResult] = useState<SentimentResponse | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  const charCount = reviewText.length;
  const wordCount = reviewText.trim() ? reviewText.trim().split(/\s+/).length : 0;

  const handleAnalyze = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    if (!reviewText.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await predictSentiment(reviewText);
      setResult(data);
      if (onAnalysisComplete) {
        onAnalysisComplete(data, reviewText);
      }
    } catch (err: any) {
      setError(err as ApiError);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectSample = (sample: string) => {
    setReviewText(sample);
    setError(null);
  };

  const handleClear = () => {
    setReviewText('');
    setResult(null);
    setError(null);
  };

  const handleCopyCleanText = () => {
    if (!result?.clean_text) return;
    navigator.clipboard.writeText(result.clean_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="glass-card analyzer-card">
      <form onSubmit={handleAnalyze} className="analyzer-form">
        {/* Header da Seção de Entrada */}
        <div className="section-label">
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={18} color="#818cf8" />
            Digite ou cole o texto da avaliação:
          </span>
          <span className="char-counter">
            {charCount} caracteres | {wordCount} palavras
          </span>
        </div>

        {/* Textarea */}
        <div className="textarea-container">
          <textarea
            className="review-textarea"
            rows={4}
            placeholder="Exemplo: O produto chegou antes do prazo e com acabamento impecável! Estou muito satisfeito..."
            value={reviewText}
            onChange={(e) => setReviewText(e.target.value)}
            disabled={isLoading}
          />
        </div>

        {/* Exemplos Rápidos */}
        <div className="examples-wrapper">
          <span className="examples-label">💡 Teste com exemplos rápidos:</span>
          <div className="examples-list">
            {SAMPLE_REVIEWS.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                className="example-btn"
                onClick={() => handleSelectSample(sample.text)}
                disabled={isLoading}
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>

        {/* Barra de Ações (Limpar e Analisar) */}
        <div className="actions-bar">
          {reviewText.length > 0 && (
            <button
              type="button"
              className="btn-secondary"
              onClick={handleClear}
              disabled={isLoading}
            >
              <Trash2 size={16} />
              Limpar
            </button>
          )}

          <button
            type="submit"
            className="btn-primary"
            disabled={isLoading || !reviewText.trim()}
          >
            {isLoading ? (
              <>
                <div className="spinner" />
                <span>Processando NLP...</span>
              </>
            ) : (
              <>
                <Send size={16} />
                <span>Analisar Sentimento</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Tratamento de Erros Amigável */}
      {error && (
        <div style={{ marginTop: '1.25rem' }}>
          <div className="error-banner">
            <AlertTriangle size={22} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              <div className="error-title">
                {error.isOffline ? 'Falha de Conexão com a API' : 'Não foi possível classificar a avaliação'}
              </div>
              <div>{error.message}</div>
              {error.isOffline && onRefreshHealth && (
                <button
                  type="button"
                  onClick={onRefreshHealth}
                  className="btn-secondary"
                  style={{
                    marginTop: '0.5rem',
                    padding: '0.4rem 0.8rem',
                    fontSize: '0.8rem',
                    alignSelf: 'flex-start',
                  }}
                >
                  <RefreshCw size={14} />
                  Tentar reconectar
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Exibição Destacada do Resultado */}
      {result && (
        <div className={`result-card ${result.sentiment.toLowerCase()}`}>
          <div className="result-header">
            <div className="result-title-group">
              <span style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                Sentimento Detectado:
              </span>
              <div className={`sentiment-badge ${result.sentiment.toLowerCase()}`}>
                {result.sentiment.toLowerCase() === 'positivo' ? (
                  <>
                    <TrendingUp size={22} />
                    <span>POSITIVO</span>
                  </>
                ) : (
                  <>
                    <TrendingDown size={22} />
                    <span>NEGATIVO</span>
                  </>
                )}
              </div>
            </div>

            {result.confidence !== undefined && result.confidence !== null && (
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  color: result.sentiment.toLowerCase() === 'positivo' ? '#34d399' : '#fb7185',
                }}
              >
                <CheckCircle2 size={16} />
                Confiança: {(result.confidence * 100).toFixed(1)}%
              </div>
            )}
          </div>

          {/* Medidor de Probabilidade */}
          {result.probabilities && (
            <div className="confidence-meter">
              <div className="progress-header">
                <span>Distribuição de Probabilidade do Modelo</span>
                <span>
                  Positivo: {((result.probabilities.positivo || 0) * 100).toFixed(1)}% | Negativo:{' '}
                  {((result.probabilities.negativo || 0) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="progress-track">
                <div
                  className={`progress-fill ${result.sentiment.toLowerCase()}`}
                  style={{
                    width: `${
                      result.sentiment.toLowerCase() === 'positivo'
                        ? ((result.probabilities.positivo || 0.5) * 100)
                        : ((result.probabilities.negativo || 0.5) * 100)
                    }%`,
                  }}
                />
              </div>
            </div>
          )}

          {/* Texto Higienizado pelo Módulo TextCleaner */}
          <div className="clean-text-box">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="clean-text-label">
                <Info size={13} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '4px' }} />
                Texto Higienizado pelo Pipeline NLP (TextCleaner):
              </span>
              <button
                type="button"
                onClick={handleCopyCleanText}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-secondary)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.3rem',
                  fontSize: '0.75rem',
                }}
              >
                {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
                {copied ? 'Copiado!' : 'Copiar'}
              </button>
            </div>
            <div className="clean-text-content">
              "{result.clean_text}"
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
