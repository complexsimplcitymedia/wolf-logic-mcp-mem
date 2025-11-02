# Contributing to Wolf Logic MCP Memory Server

Thank you for your interest in contributing! This project is truly open source and we welcome contributions from everyone.

## Code of Conduct

Be respectful, constructive, and collaborative. We're all here to build something useful together.

## How to Contribute

### Reporting Issues

Found a bug or have a feature request? Please open an issue on GitHub with:
- Clear description of the problem or feature
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- Your environment (OS, Node.js version, etc.)

### Contributing Code

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/wolf-logic-mcp-mem.git
   cd wolf-logic-mcp-mem
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, readable code
   - Follow the existing code style
   - Add comments where necessary
   - Keep changes focused and minimal

4. **Test your changes**
   ```bash
   npm run build
   # Test manually with Claude Desktop or your own test scripts
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

6. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Setup

```bash
# Install dependencies
npm install

# Build the project
npm run build

# Watch mode for development
npm run watch
```

## Project Structure

```
wolf-logic-mcp-mem/
├── src/
│   └── index.ts          # Main server implementation
├── dist/                 # Built files (generated, not committed)
├── README.md            # Main documentation
├── QUICKSTART.md        # Quick start guide
├── EXAMPLES.md          # Usage examples
├── CLAUDE_CONFIG.md     # Configuration instructions
├── package.json         # Project metadata
└── tsconfig.json        # TypeScript configuration
```

## Code Style

- Use TypeScript for type safety
- Use meaningful variable and function names
- Follow the existing code formatting
- Keep functions focused and single-purpose
- Add JSDoc comments for public APIs

## Testing

Currently, testing is done manually with Claude Desktop or custom test scripts. Contributions to add automated tests are welcome!

To test manually:
1. Build the project: `npm run build`
2. Configure in Claude Desktop (see CLAUDE_CONFIG.md)
3. Test with real conversations in Claude

## Ideas for Contributions

### Features
- Add search improvements (fuzzy search, semantic search)
- Add import/export functionality
- Add backup/restore capabilities
- Add support for tags or categories
- Add support for attachments or file references
- Add graph visualization tools

### Documentation
- More usage examples
- Video tutorials
- Translations to other languages
- Better error messages

### Infrastructure
- Automated tests
- CI/CD pipeline
- Docker image
- NPM package publication
- Performance benchmarks

### Integrations
- Support for other MCP clients
- Integration with other tools
- Plugin system for extensions

## Questions?

Not sure about something? Open an issue or discussion on GitHub. We're here to help!

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.

## Recognition

Contributors will be recognized in the project. Thank you for helping make this project better! 🎉
