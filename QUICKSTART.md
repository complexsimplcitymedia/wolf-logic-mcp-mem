# Quick Start Guide

Get up and running with Wolf Logic MCP Memory Server in 5 minutes.

## Prerequisites

- Node.js 18 or higher
- Claude Desktop (or another MCP-compatible client)

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/complexsimplcitymedia/wolf-logic-mcp-mem.git
cd wolf-logic-mcp-mem

# 2. Install dependencies
npm install

# 3. Build the server
npm run build
```

## Configuration

### MacOS

1. Open: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Add this configuration (update the path):

```json
{
  "mcpServers": {
    "memory": {
      "command": "node",
      "args": ["/FULL/PATH/TO/wolf-logic-mcp-mem/dist/index.js"]
    }
  }
}
```

### Windows

1. Open: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add this configuration (update the path):

```json
{
  "mcpServers": {
    "memory": {
      "command": "node",
      "args": ["C:\\FULL\\PATH\\TO\\wolf-logic-mcp-mem\\dist\\index.js"]
    }
  }
}
```

### Linux

1. Open: `~/.config/Claude/claude_desktop_config.json`
2. Add this configuration (update the path):

```json
{
  "mcpServers": {
    "memory": {
      "command": "node",
      "args": ["/full/path/to/wolf-logic-mcp-mem/dist/index.js"]
    }
  }
}
```

## Verify Installation

1. Restart Claude Desktop completely
2. Start a new conversation
3. Look for the 🔌 icon (usually in the bottom-right or settings)
4. You should see "memory" with 9 tools listed

## First Steps

Try these commands with Claude:

```
You: "Remember that I prefer TypeScript for backend development."
You: "I work at Acme Corp as a Senior Engineer."
You: "What do you remember about me?"
```

Claude will store and recall this information across all future conversations!

## Where's My Data?

All your data is stored locally at:
- **MacOS/Linux**: `~/.wolf-logic-mcp-mem/knowledge-graph.json`
- **Windows**: `%USERPROFILE%\.wolf-logic-mcp-mem\knowledge-graph.json`

## Troubleshooting

### Server not showing up?
- Verify the path in your config is absolute (full path)
- Make sure you restarted Claude Desktop after config changes
- Check the path points to the `dist/index.js` file

### Permission errors?
```bash
chmod +x dist/index.js
```

### Want to start fresh?
```bash
# Delete the knowledge graph
rm ~/.wolf-logic-mcp-mem/knowledge-graph.json  # MacOS/Linux
del %USERPROFILE%\.wolf-logic-mcp-mem\knowledge-graph.json  # Windows
```

## Next Steps

- Read [EXAMPLES.md](EXAMPLES.md) for detailed usage examples
- Read [README.md](README.md) for complete documentation
- Check [CLAUDE_CONFIG.md](CLAUDE_CONFIG.md) for advanced configuration

## Support

Issues? Open an issue on GitHub: https://github.com/complexsimplcitymedia/wolf-logic-mcp-mem/issues

---

**Remember**: This is 100% local and open source. Your data never leaves your machine! 🔒
