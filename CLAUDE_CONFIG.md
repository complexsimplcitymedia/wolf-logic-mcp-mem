# Example Claude Desktop Configuration

This is an example configuration for integrating the Wolf Logic MCP Memory Server with Claude Desktop.

## Configuration File Location

- **MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## Example Configuration

Replace `/absolute/path/to/wolf-logic-mcp-mem` with the actual path where you cloned this repository.

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

## Multiple Servers

If you already have other MCP servers configured, you can add this one alongside them:

```json
{
  "mcpServers": {
    "memory": {
      "command": "node",
      "args": [
        "/absolute/path/to/wolf-logic-mcp-mem/dist/index.js"
      ]
    },
    "other-server": {
      "command": "...",
      "args": ["..."]
    }
  }
}
```

## Verification

After adding the configuration:

1. Restart Claude Desktop
2. Look for the 🔌 icon in the Claude interface
3. Click it to see available MCP servers
4. You should see "memory" listed with the available tools

## Testing

Try asking Claude:
- "Remember that I prefer TypeScript for backend development"
- "What programming preferences have I mentioned?"
- "I work at Acme Corp as a senior engineer"
- "What do you know about my job?"

Claude will use the memory server to store and recall this information across sessions.
