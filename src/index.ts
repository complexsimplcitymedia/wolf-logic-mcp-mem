#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import * as fs from "fs";
import * as path from "path";

interface Entity {
  name: string;
  entityType: string;
  observations: string[];
}

interface Relation {
  from: string;
  to: string;
  relationType: string;
}

interface KnowledgeGraph {
  entities: Entity[];
  relations: Relation[];
}

class MemoryManager {
  private graph: KnowledgeGraph;
  private dataPath: string;

  constructor(dataPath: string) {
    this.dataPath = dataPath;
    this.graph = this.loadGraph();
  }

  private loadGraph(): KnowledgeGraph {
    try {
      if (fs.existsSync(this.dataPath)) {
        const data = fs.readFileSync(this.dataPath, "utf-8");
        return JSON.parse(data);
      }
    } catch (error) {
      console.error("Error loading knowledge graph:", error);
    }
    return { entities: [], relations: [] };
  }

  private saveGraph(): void {
    try {
      const dir = path.dirname(this.dataPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(this.dataPath, JSON.stringify(this.graph, null, 2), "utf-8");
    } catch (error) {
      console.error("Error saving knowledge graph:", error);
      throw error;
    }
  }

  createEntities(entities: Entity[]): { created: string[] } {
    const created: string[] = [];
    for (const entity of entities) {
      if (!this.graph.entities.find((e) => e.name === entity.name)) {
        this.graph.entities.push(entity);
        created.push(entity.name);
      }
    }
    this.saveGraph();
    return { created };
  }

  createRelations(relations: Relation[]): { created: number } {
    let created = 0;
    for (const relation of relations) {
      const exists = this.graph.relations.find(
        (r) =>
          r.from === relation.from &&
          r.to === relation.to &&
          r.relationType === relation.relationType
      );
      if (!exists) {
        this.graph.relations.push(relation);
        created++;
      }
    }
    this.saveGraph();
    return { created };
  }

  addObservations(
    observations: { entityName: string; contents: string[] }[]
  ): { added: Record<string, number> } {
    const added: Record<string, number> = {};
    for (const obs of observations) {
      const entity = this.graph.entities.find((e) => e.name === obs.entityName);
      if (!entity) {
        throw new Error(`Entity ${obs.entityName} not found`);
      }
      let count = 0;
      for (const content of obs.contents) {
        if (!entity.observations.includes(content)) {
          entity.observations.push(content);
          count++;
        }
      }
      added[obs.entityName] = count;
    }
    this.saveGraph();
    return { added };
  }

  deleteEntities(entityNames: string[]): { deleted: number } {
    let deleted = 0;
    for (const name of entityNames) {
      const index = this.graph.entities.findIndex((e) => e.name === name);
      if (index !== -1) {
        this.graph.entities.splice(index, 1);
        deleted++;
        // Remove related relations
        this.graph.relations = this.graph.relations.filter(
          (r) => r.from !== name && r.to !== name
        );
      }
    }
    this.saveGraph();
    return { deleted };
  }

  deleteObservations(
    deletions: { entityName: string; observations: string[] }[]
  ): { deleted: Record<string, number> } {
    const deleted: Record<string, number> = {};
    for (const deletion of deletions) {
      const entity = this.graph.entities.find((e) => e.name === deletion.entityName);
      if (entity) {
        let count = 0;
        for (const obs of deletion.observations) {
          const index = entity.observations.indexOf(obs);
          if (index !== -1) {
            entity.observations.splice(index, 1);
            count++;
          }
        }
        deleted[deletion.entityName] = count;
      }
    }
    this.saveGraph();
    return { deleted };
  }

  deleteRelations(relations: Relation[]): { deleted: number } {
    let deleted = 0;
    for (const relation of relations) {
      const index = this.graph.relations.findIndex(
        (r) =>
          r.from === relation.from &&
          r.to === relation.to &&
          r.relationType === relation.relationType
      );
      if (index !== -1) {
        this.graph.relations.splice(index, 1);
        deleted++;
      }
    }
    this.saveGraph();
    return { deleted };
  }

  readGraph(): KnowledgeGraph {
    return this.graph;
  }

  searchNodes(query: string): { entities: Entity[] } {
    const lowerQuery = query.toLowerCase();
    const entities = this.graph.entities.filter(
      (e) =>
        e.name.toLowerCase().includes(lowerQuery) ||
        e.entityType.toLowerCase().includes(lowerQuery) ||
        e.observations.some((o) => o.toLowerCase().includes(lowerQuery))
    );
    return { entities };
  }

  openNodes(names: string[]): { entities: Entity[] } {
    const entities = this.graph.entities.filter((e) => names.includes(e.name));
    return { entities };
  }
}

// Initialize memory manager with data path in user's home directory
const homedir = process.env.HOME || process.env.USERPROFILE || "/tmp";
const dataDir = path.join(homedir, ".wolf-logic-mcp-mem");
const dataPath = path.join(dataDir, "knowledge-graph.json");
const memoryManager = new MemoryManager(dataPath);

// Create MCP server
const server = new Server(
  {
    name: "wolf-logic-mcp-mem",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define available tools
const TOOLS: Tool[] = [
  {
    name: "create_entities",
    description:
      "Create multiple new entities in the knowledge graph. Each entity represents a person, place, concept, or thing that can have observations.",
    inputSchema: {
      type: "object",
      properties: {
        entities: {
          type: "array",
          items: {
            type: "object",
            properties: {
              name: {
                type: "string",
                description: "Unique identifier for the entity (use underscores for spaces)",
              },
              entityType: {
                type: "string",
                description: "Type of entity (e.g., person, organization, event, concept)",
              },
              observations: {
                type: "array",
                items: { type: "string" },
                description: "List of observations about this entity",
              },
            },
            required: ["name", "entityType", "observations"],
          },
        },
      },
      required: ["entities"],
    },
  },
  {
    name: "create_relations",
    description:
      "Create multiple new directed relations between entities. Relations should be in active voice.",
    inputSchema: {
      type: "object",
      properties: {
        relations: {
          type: "array",
          items: {
            type: "object",
            properties: {
              from: {
                type: "string",
                description: "Source entity name",
              },
              to: {
                type: "string",
                description: "Target entity name",
              },
              relationType: {
                type: "string",
                description: "Type of relationship in active voice (e.g., works_at, knows, manages)",
              },
            },
            required: ["from", "to", "relationType"],
          },
        },
      },
      required: ["relations"],
    },
  },
  {
    name: "add_observations",
    description: "Add new observations to existing entities in the knowledge graph.",
    inputSchema: {
      type: "object",
      properties: {
        observations: {
          type: "array",
          items: {
            type: "object",
            properties: {
              entityName: {
                type: "string",
                description: "Name of the entity to add observations to",
              },
              contents: {
                type: "array",
                items: { type: "string" },
                description: "New observations to add",
              },
            },
            required: ["entityName", "contents"],
          },
        },
      },
      required: ["observations"],
    },
  },
  {
    name: "delete_entities",
    description:
      "Delete entities and their associated relations from the knowledge graph.",
    inputSchema: {
      type: "object",
      properties: {
        entityNames: {
          type: "array",
          items: { type: "string" },
          description: "Names of entities to delete",
        },
      },
      required: ["entityNames"],
    },
  },
  {
    name: "delete_observations",
    description: "Delete specific observations from entities.",
    inputSchema: {
      type: "object",
      properties: {
        deletions: {
          type: "array",
          items: {
            type: "object",
            properties: {
              entityName: {
                type: "string",
                description: "Name of the entity",
              },
              observations: {
                type: "array",
                items: { type: "string" },
                description: "Observations to delete",
              },
            },
            required: ["entityName", "observations"],
          },
        },
      },
      required: ["deletions"],
    },
  },
  {
    name: "delete_relations",
    description: "Delete specific relations from the knowledge graph.",
    inputSchema: {
      type: "object",
      properties: {
        relations: {
          type: "array",
          items: {
            type: "object",
            properties: {
              from: { type: "string" },
              to: { type: "string" },
              relationType: { type: "string" },
            },
            required: ["from", "to", "relationType"],
          },
        },
      },
      required: ["relations"],
    },
  },
  {
    name: "read_graph",
    description:
      "Read the entire knowledge graph including all entities and relations. Use this to get a complete view of stored knowledge.",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "search_nodes",
    description:
      "Search for entities in the knowledge graph by name, type, or observations.",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search query to match against entity names, types, and observations",
        },
      },
      required: ["query"],
    },
  },
  {
    name: "open_nodes",
    description: "Retrieve specific entities by their exact names.",
    inputSchema: {
      type: "object",
      properties: {
        names: {
          type: "array",
          items: { type: "string" },
          description: "List of entity names to retrieve",
        },
      },
      required: ["names"],
    },
  },
];

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools: TOOLS };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const { name, arguments: args } = request.params;

    if (!args) {
      throw new Error("Missing arguments");
    }

    switch (name) {
      case "create_entities": {
        const result = memoryManager.createEntities(args.entities as Entity[]);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "create_relations": {
        const result = memoryManager.createRelations(args.relations as Relation[]);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "add_observations": {
        const result = memoryManager.addObservations(
          args.observations as { entityName: string; contents: string[] }[]
        );
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "delete_entities": {
        const result = memoryManager.deleteEntities(args.entityNames as string[]);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "delete_observations": {
        const result = memoryManager.deleteObservations(
          args.deletions as { entityName: string; observations: string[] }[]
        );
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "delete_relations": {
        const result = memoryManager.deleteRelations(args.relations as Relation[]);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "read_graph": {
        const result = memoryManager.readGraph();
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "search_nodes": {
        const result = memoryManager.searchNodes(args.query as string);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "open_nodes": {
        const result = memoryManager.openNodes(args.names as string[]);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return {
      content: [
        {
          type: "text",
          text: `Error: ${errorMessage}`,
        },
      ],
      isError: true,
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Wolf Logic MCP Memory Server running on stdio");
  console.error(`Data stored in: ${dataPath}`);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
