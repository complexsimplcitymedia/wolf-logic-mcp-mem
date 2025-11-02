# Wolf Logic MCP Memory Server

A truly open source, local-first memory MCP server that enables persistent memory for AI assistants through a knowledge graph. **If I say open source and I say local, that's what it is** - no cloud dependencies, no external services, just pure local storage.

## Features

✅ **100% Local** - All data stored locally on your machine  
✅ **Open Source** - Apache 2.0 license, fully transparent  
✅ **Privacy First** - Your data never leaves your computer  
✅ **Knowledge Graph** - Store entities, relations, and observations  
✅ **Persistent Memory** - Maintains context across AI assistant sessions  
✅ **Simple Setup** - Works with Claude Desktop and other MCP-compatible clients  

## What is MCP?

MCP (Model Context Protocol) is a standardized protocol by Anthropic that enables AI assistants like Claude to interact with external data sources and tools. This memory server gives AI assistants persistent memory capabilities by maintaining a local knowledge graph.

## Installation

```bash
# Clone the repository
git clone https://github.com/complexsimplcitymedia/wolf-logic-mcp-mem.git
cd wolf-logic-mcp-mem

# Install dependencies
npm install

# Build the server
npm run build
```

## Usage

### Configuration for Claude Desktop

Add this to your Claude Desktop configuration file:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "memory": {
      "command": "node",
      "args": [
        "/absolute/path/to/wolf-logic-mcp-mem/dist/index.js"
      ]
    }
  }
}
```

Replace `/absolute/path/to/wolf-logic-mcp-mem` with the actual path where you cloned this repository.

### Standalone Usage

You can also run the server directly:

```bash
npm start
```

## How It Works

The memory server maintains a knowledge graph with two main components:

### Entities
Entities are nodes in the knowledge graph representing people, places, concepts, or things:

```json
{
  "name": "John_Doe",
  "entityType": "person",
  "observations": [
    "Prefers TypeScript over JavaScript",
    "Works remotely",
    "Interested in AI development"
  ]
}
```

### Relations
Relations are directed connections between entities:

```json
{
  "from": "John_Doe",
  "to": "Acme_Corp",
  "relationType": "works_at"
}
```

## Available Tools

The server provides these tools to AI assistants:

- **create_entities** - Create new entities in the knowledge graph
- **create_relations** - Define relationships between entities
- **add_observations** - Add facts/observations to existing entities
- **delete_entities** - Remove entities and their relations
- **delete_observations** - Remove specific observations
- **delete_relations** - Remove specific relationships
- **read_graph** - Get the complete knowledge graph
- **search_nodes** - Search entities by name, type, or content
- **open_nodes** - Retrieve specific entities by name

## Data Storage

All data is stored locally in:
- **MacOS/Linux**: `~/.wolf-logic-mcp-mem/knowledge-graph.json`
- **Windows**: `%USERPROFILE%\.wolf-logic-mcp-mem\knowledge-graph.json`

The knowledge graph is stored as a simple JSON file, making it:
- Easy to backup
- Easy to inspect
- Easy to migrate
- Completely portable

## Example Interaction

Once connected to Claude Desktop, you can ask Claude to:

- "Remember that I prefer morning meetings"
- "I work at Anthropic as a software engineer"
- "What do you know about my work preferences?"
- "Create a note that I'm learning Rust"

Claude will use the memory tools to store and retrieve this information across sessions.

## Development

```bash
# Watch mode for development
npm run watch

# Build
npm run build

# Run after building
npm start
```

## Why This Implementation?

This implementation emphasizes:

1. **Local-First**: No cloud services, APIs, or external dependencies
2. **Open Source**: Apache 2.0 license, transparent code
3. **Simplicity**: Plain JSON storage, easy to understand
4. **Privacy**: Your data stays on your machine
5. **Portability**: Simple file-based storage you can backup/move

## License

Apache License 2.0 - See LICENSE file for details.

## Contributing

This is an open source project. Contributions, issues, and feature requests are welcome!

## Acknowledgments

Inspired by the MCP memory server from Anthropic's official servers repository, reimplemented with a focus on local-first, open source principles.
