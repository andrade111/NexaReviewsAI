/**
 * Serviço de comunicação com a API Backend do NexaReviews AI.
 * Endpoints: GET /health e POST /predict
 */

export interface SentimentRequest {
  text: string;
}

export interface SentimentResponse {
  sentiment: 'positivo' | 'negativo' | string;
  clean_text: string;
  confidence?: number | null;
  probabilities?: Record<string, number> | null;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  model_path?: string | null;
}

export interface ApiError {
  message: string;
  statusCode?: number;
  isOffline?: boolean;
}

// URL base configurável via variável de ambiente do Vite ou fallback local
const API_BASE_URL = (import.meta.env.VITE_API_URL as string) || 'http://localhost:8000';

/**
 * Envia uma avaliação textual para a API de Machine Learning e retorna a classificação.
 *
 * @param text - Texto bruto da avaliação (review) a ser analisado
 * @returns Promessa com o resultado da inferência e detalhes
 */
export async function predictSentiment(text: string): Promise<SentimentResponse> {
  const trimmed = text.trim();
  if (!trimmed) {
    throw {
      message: 'O texto da avaliação não pode estar vazio.',
      statusCode: 400,
    } as ApiError;
  }

  const endpoint = `${API_BASE_URL}/predict`;

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({ text: trimmed } as SentimentRequest),
    });

    if (!response.ok) {
      let errorMessage = `Erro na API (${response.status} ${response.statusText})`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = typeof errorData.detail === 'string'
            ? errorData.detail
            : JSON.stringify(errorData.detail);
        }
      } catch {
        // Usa a mensagem padrão caso o JSON falhe
      }

      throw {
        message: errorMessage,
        statusCode: response.status,
      } as ApiError;
    }

    const data: SentimentResponse = await response.json();
    return data;
  } catch (error: unknown) {
    // Se o erro já for nosso objeto ApiError
    if (typeof error === 'object' && error !== null && 'statusCode' in error) {
      throw error;
    }

    // Erro de rede / servidor inacessível
    throw {
      message:
        'Não foi possível conectar ao servidor da API em ' +
        API_BASE_URL +
        '. Certifique-se de que o backend FastAPI está em execução (uvicorn src.api:app --reload).',
      isOffline: true,
    } as ApiError;
  }
}

/**
 * Verifica o status de saúde da API e o carregamento do modelo.
 *
 * @returns Promessa com o status e metadados do modelo
 */
export async function checkHealth(): Promise<HealthResponse> {
  const endpoint = `${API_BASE_URL}/health`;

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000);

    const response = await fetch(endpoint, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`Health check falhou: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    throw {
      message: 'API Backend offline ou inacessível.',
      isOffline: true,
    } as ApiError;
  }
}
