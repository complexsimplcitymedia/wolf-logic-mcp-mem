import { withoutTrailingSlash } from '@ai-sdk/provider-utils'

import { Mem0GenericLanguageModel } from './wolf-logic-generic-language-model'
import { Mem0ChatModelId, Mem0ChatSettings } from './wolf-types'
import { Mem0ProviderSettings } from './wolf-logic-provider'

export class Mem0 {
  readonly baseURL: string
  readonly headers?: any

  constructor(options: Mem0ProviderSettings = {
    provider: 'ollama',
  }) {
    this.baseURL =
      withoutTrailingSlash(options.baseURL) ?? 'http://127.0.0.1:11434/api'

    this.headers = options.headers
  }

  private get baseConfig() {
    return {
      baseURL: this.baseURL,
      headers: this.headers,
    }
  }

  chat(modelId: Mem0ChatModelId, settings: Mem0ChatSettings = {}) {
    return new Mem0GenericLanguageModel(modelId, settings, {
      provider: 'ollama',
      modelType: 'chat',
      ...this.baseConfig,
    })
  }

  completion(modelId: Mem0ChatModelId, settings: Mem0ChatSettings = {}) {
    return new Mem0GenericLanguageModel(modelId, settings, {
      provider: 'ollama',
      modelType: 'completion',
      ...this.baseConfig,
    })
  }
}
