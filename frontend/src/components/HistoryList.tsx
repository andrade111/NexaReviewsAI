import React from 'react';
import { History, Trash2, TrendingUp, TrendingDown } from 'lucide-react';
import { SentimentResponse } from '../services/api';

export interface HistoryItem {
  id: string;
  timestamp: string;
  originalText: string;
  result: SentimentResponse;
}

interface HistoryListProps {
  history: HistoryItem[];
  onClearHistory: () => void;
  onSelectReview: (text: string) => void;
}

export const HistoryList: React.FC<HistoryListProps> = ({
  history,
  onClearHistory,
  onSelectReview,
}) => {
  if (history.length === 0) return null;

  return (
    <div className="glass-card" style={{ padding: '1.5rem 1.75rem' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>
          <History size={18} color="#818cf8" />
          <span>Histórico Recente de Avaliações ({history.length})</span>
        </div>

        <button
          type="button"
          onClick={onClearHistory}
          className="btn-secondary"
          style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
        >
          <Trash2 size={13} />
          Limpar Histórico
        </button>
      </div>

      <div className="history-list">
        {history.slice(0, 6).map((item) => {
          const isPos = item.result.sentiment.toLowerCase() === 'positivo';
          return (
            <div
              key={item.id}
              className="history-item"
              onClick={() => onSelectReview(item.originalText)}
              style={{ cursor: 'pointer' }}
              title="Clique para carregar esta avaliação no analisador"
            >
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem', minWidth: 0 }}>
                <span className="history-text">"{item.originalText}"</span>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  {item.timestamp}
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexShrink: 0 }}>
                <span className={`mini-badge ${item.result.sentiment.toLowerCase()}`}>
                  {isPos ? (
                    <TrendingUp size={12} style={{ display: 'inline', marginRight: '3px' }} />
                  ) : (
                    <TrendingDown size={12} style={{ display: 'inline', marginRight: '3px' }} />
                  )}
                  {item.result.sentiment}
                </span>
                {item.result.confidence && (
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    {(item.result.confidence * 100).toFixed(0)}%
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
