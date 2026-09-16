export interface AppConfig {
  provider: string;
  model: string;
  apiKey?: string;
  customProviderUrl?: string;
  responseStyle?: string;
  responseInstructions?: string;
}

export interface ProviderConfig {
  name: string;
  requiresApiKey: boolean;
  supportsCustomUrl: boolean;
  models?: string[];
}

export const PROVIDER_CONFIGS: Record<string, ProviderConfig> = {
  groq: {
    name: 'Groq',
    requiresApiKey: true,
    supportsCustomUrl: false,
    models: ['mixtral-8x7b-32768', 'llama3-70b-8192', 'llama3-8b-8192']
  },
  openai: {
    name: 'OpenAI',
    requiresApiKey: true,
    supportsCustomUrl: false,
    models: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo']
  },
  anthropic: {
    name: 'Anthropic',
    requiresApiKey: true,
    supportsCustomUrl: false,
    models: ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-haiku-20240307']
  },
  gemini: {
    name: 'Gemini',
    requiresApiKey: true,
    supportsCustomUrl: false,
    models: ['gemini-pro', 'gemini-1.5-pro', 'gemini-1.5-flash']
  },
  openrouter: {
    name: 'OpenRouter',
    requiresApiKey: true,
    supportsCustomUrl: false,
  },
  ollama: {
    name: 'Ollama',
    requiresApiKey: false,
    supportsCustomUrl: true,
  },
  custom: {
    name: 'Custom Provider',
    requiresApiKey: true,
    supportsCustomUrl: true,
  }
};
