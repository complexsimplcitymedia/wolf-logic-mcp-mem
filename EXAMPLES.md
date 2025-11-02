# Usage Examples

This document provides examples of how to use the Wolf Logic MCP Memory Server with Claude Desktop.

## Getting Started

After configuring the server in Claude Desktop (see CLAUDE_CONFIG.md), restart Claude and the memory tools will be available.

## Basic Examples

### Example 1: Storing Personal Preferences

**User:** "Remember that I prefer Python for data analysis and JavaScript for web development."

Claude will use the `create_entities` tool to create an entity representing you, and use `add_observations` to store your programming preferences.

Behind the scenes:
```json
{
  "entities": [{
    "name": "User",
    "entityType": "person",
    "observations": [
      "Prefers Python for data analysis",
      "Prefers JavaScript for web development"
    ]
  }]
}
```

### Example 2: Storing Work Information

**User:** "I work at Acme Corporation as a Senior Software Engineer in the Platform team."

Claude creates entities and relations:
```json
{
  "entities": [
    {
      "name": "User",
      "entityType": "person",
      "observations": ["Senior Software Engineer", "Works in Platform team"]
    },
    {
      "name": "Acme_Corporation",
      "entityType": "organization",
      "observations": ["User's employer"]
    }
  ],
  "relations": [
    {
      "from": "User",
      "to": "Acme_Corporation",
      "relationType": "works_at"
    }
  ]
}
```

### Example 3: Recalling Information

**User:** "What do you know about my programming preferences?"

Claude will use `search_nodes` or `open_nodes` to retrieve your information:

**Response:** "Based on what you've told me, you prefer Python for data analysis and JavaScript for web development."

### Example 4: Storing Project Information

**User:** "I'm working on a project called 'DataViz Pro' that uses React and D3.js for visualizations."

```json
{
  "entities": [{
    "name": "DataViz_Pro",
    "entityType": "project",
    "observations": [
      "Uses React for UI",
      "Uses D3.js for visualizations",
      "User is working on this project"
    ]
  }],
  "relations": [{
    "from": "User",
    "to": "DataViz_Pro",
    "relationType": "works_on"
  }]
}
```

### Example 5: Adding Information Over Time

**First conversation:**
**User:** "I like hiking."

**Later conversation:**
**User:** "I also enjoy photography, especially landscape photography."

Claude uses `add_observations` to append new information to your existing entity rather than creating duplicates.

### Example 6: Updating Information

**User:** "Actually, I don't work at Acme Corporation anymore. I now work at TechStart Inc."

Claude will:
1. Use `delete_relations` to remove the old employment relation
2. Use `create_entities` to create TechStart Inc if needed
3. Use `create_relations` to establish the new employment relation
4. Use `add_observations` to update your work history

## Knowledge Graph Exploration

### Searching

**User:** "Show me everything related to programming."

Claude uses `search_nodes` with query "programming" to find all entities and observations containing that term.

### Getting Full Context

**User:** "Show me everything you remember about me."

Claude uses `read_graph` to retrieve the entire knowledge graph and presents relevant information.

## Complex Scenarios

### Team Relationships

**User:** "Remember that Alice is my team lead, Bob is a colleague, and Carol is in the Design team."

Creates multiple entities and relations:
```json
{
  "entities": [
    {"name": "Alice", "entityType": "person", "observations": ["Team lead"]},
    {"name": "Bob", "entityType": "person", "observations": ["Colleague"]},
    {"name": "Carol", "entityType": "person", "observations": ["In Design team"]}
  ],
  "relations": [
    {"from": "Alice", "to": "User", "relationType": "manages"},
    {"from": "User", "to": "Bob", "relationType": "works_with"},
    {"from": "Carol", "to": "Design_Team", "relationType": "member_of"}
  ]
}
```

### Learning Paths

**User:** "I'm learning Rust and trying to understand ownership and borrowing. I find it challenging but interesting."

```json
{
  "entities": [{
    "name": "Rust_Learning",
    "entityType": "learning_path",
    "observations": [
      "Currently learning Rust",
      "Studying ownership and borrowing concepts",
      "Finds it challenging but interesting"
    ]
  }],
  "relations": [{
    "from": "User",
    "to": "Rust_Learning",
    "relationType": "pursuing"
  }]
}
```

## Data Privacy

All information is stored locally on your machine in:
- MacOS/Linux: `~/.wolf-logic-mcp-mem/knowledge-graph.json`
- Windows: `%USERPROFILE%\.wolf-logic-mcp-mem\knowledge-graph.json`

You can:
- View the file directly to see what's stored
- Back it up by copying the file
- Delete it to clear all memory
- Move it to another machine

## Tips for Best Results

1. **Be specific**: Instead of "I like coding," say "I prefer Python for backend development"
2. **Provide context**: "I work at Acme Corp as a Senior Engineer" is better than "I'm an engineer"
3. **Use natural language**: The system handles conversational input well
4. **Review periodically**: Ask "What do you remember about X?" to verify stored information
5. **Update when needed**: Correct information by explicitly stating changes

## Troubleshooting

### Memory Not Persisting?

Check that:
1. The server is properly configured in Claude Desktop config
2. Claude Desktop was restarted after configuration
3. The data directory is writable (`~/.wolf-logic-mcp-mem/`)

### Want to Start Fresh?

Delete the knowledge graph file:
```bash
rm ~/.wolf-logic-mcp-mem/knowledge-graph.json
```

### Viewing Stored Data

```bash
cat ~/.wolf-logic-mcp-mem/knowledge-graph.json | jq .
```

(Requires `jq` for pretty formatting, or just open in any text editor)
