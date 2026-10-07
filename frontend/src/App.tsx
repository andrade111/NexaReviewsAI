import React, { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { ReviewAnalyzer } from './components/ReviewAnalyzer';
import { MetricsCards } from './components/MetricsCards';
import { HistoryList, HistoryItem } from './components/HistoryList';
import { checkHealth, HealthResponse, SentimentResponse } from './services/api';

const HISTORY_STORAGE_KEY = 'nexareviews_ai_history_v1';

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isCheckingHealth, setIsCheckingHealth] = useState<boolean>(false);
  const [history, setHistory] = useState<HistoryItem[]>(() => {
    try {
      const saved = localStorage.getItem(HISTORY_STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const fetchHealthStatus = useCallback(async () => {
    setIsCheckingHealth(true);
    try {
      const status = await checkHealth();
      setHealth(status);
    } catch {
      setHealth(null);
    } finally {
      setIsCheckingHealth(false);
    }
  }, []);

  // Checa status de saúde ao iniciar e a cada 15 segundos
  useEffect(() => {
    fetchHealthStatus();
    const interval = setInterval(fetchHealthStatus, 15000);
    return () => clearInterval(interval);
  }, [fetchHealthStatus]);

  // Salva histórico no localStorage
  useEffect(() => {
    try {
      localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(history));
    } catch (e) {
      console.warn('Falha ao salvar histórico no localStorage', e);
    }
  }, [history]);

  const handleAnalysisComplete = (result: SentimentResponse, originalText: string) => {
    const newItem: HistoryItem = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      originalText,
      result,
    };
    setHistory((prev) => [newItem, ...prev.slice(0, 19)]); // Guarda os últimos 20
  };

  const handleClearHistory = () => {
    setHistory([]);
    try {
      localStorage.removeItem(HISTORY_STORAGE_KEY);
    } catch {
      // Ignora erro
    }
  };

  return (
    <div className="app-container">
      {/* Cabeçalho da Aplicação */}
      <Header
        health={health}
        isChecking={isCheckingHealth}
        onRefresh={fetchHealthStatus}
      />

      {/* Componente Principal de Análise de Reviews */}
      <main>
        <ReviewAnalyzer
          onAnalysisComplete={handleAnalysisComplete}
          isBackendOnline={health !== null && health.status === 'ok'}
          onRefreshHealth={fetchHealthStatus}
        />
      </main>

      {/* Histórico Recente */}
      <HistoryList
        history={history}
        onClearHistory={handleClearHistory}
        onSelectReview={(text) => {
          // Copia ou pode ser estendido
          const textarea = document.querySelector('textarea') as HTMLTextAreaElement;
          if (textarea) {
            textarea.value = text;
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
            textarea.focus();
          }
        }}
      />

      {/* Cards Informativos sobre a Arquitetura */}
      <MetricsCards />

      {/* Rodapé Profissional */}
      <footer className="app-footer">
        <p>
          <strong>NexaReviews AI</strong> &copy; {new Date().getFullYear()} &mdash; Sistema de
          Inteligência Artificial para E-commerce | FastAPI + Scikit-Learn + React TypeScript
        </p>
      </footer>
    </div>
  );
};

export default App;
