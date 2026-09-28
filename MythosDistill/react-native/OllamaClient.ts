#!/usr/bin/env python3
"""react-native/OllamaClient.ts - React Native client for Ollama HTTP API."""

import { Platform } from 'react-native';

export interface OllamaMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface OllamaChatRequest {
  model: string;
  messages: OllamaMessage[];
  stream?: boolean;
  options?: {
    temperature?: number;
    top_p?: number;
    num_predict?: number;
    repeat_penalty?: number;
  };
}

export interface OllamaChatResponse {
  model: string;
  created_at: string;
  message: OllamaMessage;
  done: boolean;
  total_duration?: number;
  load_duration?: number;
  eval_count?: number;
  eval_duration?: number;
}

export interface OllamaModel {
  name: string;
  modified_at: string;
  size: number;
  details: {
    parent_model: string;
    format: string;
    family: string;
    families: string[];
    parameter_size: string;
    quantization_level: string;
  };
}

export interface OllamaListResponse {
  models: OllamaModel[];
}

class OllamaClient {
  private baseUrl: string;
  private abortController: AbortController | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  /**
   * List locally available models.
   */
  async listModels(): Promise<OllamaModel[]> {
    const res = await fetch(`${this.baseUrl}/api/tags`);
    if (!res.ok) {
      throw new Error(`Ollama listModels failed: ${res.status} ${res.statusText}`);
    }
    const data: OllamaListResponse = await res.json();
    return data.models ?? [];
  }

  /**
   * Non-streaming chat completion.
   */
  async chat(req: OllamaChatRequest): Promise<OllamaChatResponse> {
    this.abortController = new AbortController();
    const res = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...req, stream: false }),
      signal: this.abortController.signal,
    });
    if (!res.ok) {
      throw new Error(`Ollama chat failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  /**
   * Streaming chat completion via SSE.
   * Calls onChunk for each partial response.
   */
  async chatStream(
    req: OllamaChatRequest,
    onChunk: (chunk: OllamaChatResponse) => void,
    onError?: (err: Error) => void,
    onComplete?: () => void,
  ): Promise<void> {
    this.abortController = new AbortController();
    try {
      const res = await fetch(`${this.baseUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...req, stream: true }),
        signal: this.abortController.signal,
      });

      if (!res.ok) {
        throw new Error(`Ollama chatStream failed: ${res.status} ${res.statusText}`);
      }

      const reader = res.body?.getReader();
      if (!reader) {
        throw new Error('No response body available for streaming');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;
          try {
            const json: OllamaChatResponse = JSON.parse(trimmed);
            onChunk(json);
          } catch {
            // Ignore malformed JSON lines
          }
        }
      }

      onComplete?.();
    } catch (err: any) {
      if (err.name === 'AbortError') {
        // Intentionally cancelled
        return;
      }
      onError?.(err);
    }
  }

  /**
   * Cancel any in-flight request.
   */
  cancel(): void {
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
  }
}

// Default instance for the local Ollama server on the dev machine.
// Override via `OllamaClient` constructor for remote hosts or custom ports.
export const defaultOllamaClient = new OllamaClient(
  Platform.OS === 'android' ? 'http://10.0.2.2:11434' : 'http://localhost:11434',
);

export default OllamaClient;