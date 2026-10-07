import React from 'react';
import { Layers, Database, Zap, ShieldCheck } from 'lucide-react';

export const MetricsCards: React.FC = () => {
  return (
    <div className="info-grid">
      <div className="info-card">
        <div className="info-card-header">
          <Zap size={18} color="#6366f1" />
          <span>Inferência em Tempo Real</span>
        </div>
        <p className="info-card-text">
          API RESTful em FastAPI com latência sub-milisegundo, validada via Pydantic e pronta para alto volume de requisições.
        </p>
      </div>

      <div className="info-card">
        <div className="info-card-header">
          <Layers size={18} color="#06b6d4" />
          <span>Pipeline NLP TF-IDF</span>
        </div>
        <p className="info-card-text">
          Vetorização de n-grams (1 e 2 termos) com 5.000 features e normalização estatística sublinear de frequências.
        </p>
      </div>

      <div className="info-card">
        <div className="info-card-header">
          <Database size={18} color="#a855f7" />
          <span>Regressão Logística</span>
        </div>
        <p className="info-card-text">
          Classificador linear calibrado para cálculo de probabilidades e identificação precisa de sentimentos positivos e negativos.
        </p>
      </div>

      <div className="info-card">
        <div className="info-card-header">
          <ShieldCheck size={18} color="#10b981" />
          <span>TextCleaner Higienizador</span>
        </div>
        <p className="info-card-text">
          Normalização Unicode NFKD, remoção de caracteres especiais, números e padronização sem perda semântica.
        </p>
      </div>
    </div>
  );
};
