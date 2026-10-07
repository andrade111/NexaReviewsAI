import React from 'react';
import { Cpu, RefreshCw, CheckCircle2, XCircle } from 'lucide-react';
import { HealthResponse } from '../services/api';

interface HeaderProps {
  health: HealthResponse | null;
  isChecking: boolean;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({ health, isChecking, onRefresh }) => {
  const isOnline = health !== null && health.status === 'ok';

  return (
    <header className="header-wrapper">
      <div className="brand-badge">
        <span className="brand-dot" />
        <span>Machine Learning & NLP Production Suite</span>
      </div>

      <h1 className="main-title">
        NexaReviews <span className="gradient-text">AI</span>
      </h1>

      <p className="main-subtitle">
        Análise Inteligente de Sentimentos em Avaliações de E-commerce. Classifique o feedback
        dos seus clientes em tempo real através do pipeline de NLP e Regressão Logística.
      </p>

      {/* Status Bar */}
      <div className="status-bar" style={{ width: '100%', maxWidth: '800px', marginTop: '0.5rem' }}>
        <div className="status-indicator">
          <div
            className={`status-pulse ${
              isChecking ? 'checking' : isOnline ? 'online' : 'offline'
            }`}
          />
          <span>
            {isChecking
              ? 'Verificando conexão com a API...'
              : isOnline
              ? 'API FastAPI Conectada (http://localhost:8000)'
              : 'API Backend Offline'}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {isOnline && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: '#94a3b8' }}>
              <Cpu size={14} color="#818cf8" />
              <span>Modelo: {health.model_loaded ? 'Carregado em Memória' : 'Pendente'}</span>
            </div>
          )}

          <button
            type="button"
            onClick={onRefresh}
            className="btn-secondary"
            style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
            title="Atualizar status do backend"
            disabled={isChecking}
          >
            <RefreshCw size={13} className={isChecking ? 'spinner' : ''} />
            <span>Verificar</span>
          </button>
        </div>
      </div>
    </header>
  );
};
