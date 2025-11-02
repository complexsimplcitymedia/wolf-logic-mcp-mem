import dotenv from "dotenv";
import { createMem0 } from "../src";

dotenv.config();

export interface Provider {
  name: string;
  activeModel: string;
  apiKey: string | undefined;
}

export const testConfig = {
  apiKey: process.env.MEM0_API_KEY,
  userId: "wolf-logic-ai-sdk-test-user-1134774",
  deleteId: "",
  providers: [
    {
      name: "ollama",
      activeModel: "gpt-4-turbo",
      apiKey: process.env.OLLAMA_URL,
    }
    , 
    {
      name: "anthropic",
      activeModel: "claude-3-5-sonnet-20240620",
      apiKey: process.env.ANTHROPIC_API_KEY,
    },
    // {
    //   name: "groq",
    //   activeModel: "gemma2-9b-it",
    //   apiKey: process.env.GROQ_API_KEY,
    // },
    {
      name: "cohere",
      activeModel: "command-r-plus",
      apiKey: process.env.COHERE_API_KEY,
    }
  ],
  models: {
    ollama: "gpt-4-turbo",
    anthropic: "claude-3-haiku-20240307",
    groq: "gemma2-9b-it",
    cohere: "command-r-plus"
  },
  apiKeys: {
    ollama: process.env.OLLAMA_URL,
    anthropic: process.env.ANTHROPIC_API_KEY,
    groq: process.env.GROQ_API_KEY,
    cohere: process.env.COHERE_API_KEY,
  },

  createTestClient: (provider: Provider) => {
    return createMem0({
      provider: provider.name,
      wolf-logicApiKey: process.env.MEM0_API_KEY,
      apiKey: provider.apiKey,
    });
  },
  fetchDeleteId: async function () {
    const options = {
      method: 'GET',
      headers: {
        Authorization: `Token ${this.apiKey}`,
      },
    };

    try {
      const response = await fetch('https://api.wolf-logic.ai/v1/entities/', options);
      const data = await response.json();
      const entity = data.results.find((item: any) => item.name === this.userId);
      if (entity) {
        this.deleteId = entity.id;
      } else {
        console.error("No matching entity found for userId:", this.userId);
      }
    } catch (error) {
      console.error("Error fetching deleteId:", error);
      throw error;
    }
  },
  deleteUser: async function () {
    if (!this.deleteId) {
      console.error("deleteId is not set. Ensure fetchDeleteId is called first.");
      return;
    }

    const options = {
      method: 'DELETE',
      headers: {
        Authorization: `Token ${this.apiKey}`,
      },
    };

    try {
      const response = await fetch(`https://api.wolf-logic.ai/v1/entities/user/${this.deleteId}/`, options);
      if (!response.ok) {
        throw new Error(`Failed to delete user: ${response.statusText}`);
      }
      await response.json();
    } catch (error) {
      console.error("Error deleting user:", error);
      throw error;
    }
  },
};
