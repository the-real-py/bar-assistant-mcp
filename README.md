# Bar Assistant MCP Server

An MCP (Model Context Protocol) server for [Bar Assistant](https://barassistant.app/) - manage your home bar shelf and discover cocktails you can make.

## Features

- 📋 View ingredients on your bar shelf
- 🍸 See cocktails you can make with what you have
- ➕ Add ingredients to your shelf
- ➖ Remove ingredients from your shelf
- 🔍 Search for ingredients by name

## Installation

### Using uvx (Recommended)

Run directly with uvx:

```bash
uvx --from git+https://github.com/the-real-py/bar-assistant-mcp bar-assistant-mcp \
  http://localhost:8000/api \
  your_token_here \
  1
```

Or set environment variables in `.env` and run:

```bash
uvx --from git+https://github.com/the-real-py/bar-assistant-mcp bar-assistant-mcp
```

### Using pip

```bash
pip install git+https://github.com/the-real-py/bar-assistant-mcp
bar-assistant-mcp
```

## Configuration

Create a `.env` file in your project directory:

```bash
BAR_ASSISTANT_API_URL=http://localhost:8000/api
BAR_ASSISTANT_TOKEN=your_bearer_token_here
BAR_ASSISTANT_BAR_ID=1
```

Or pass them as command-line arguments:

```bash
bar-assistant-mcp <api_url> <token> <bar_id>
```

### Getting Your Credentials

1. **API URL**: Your Bar Assistant instance URL + `/api`
2. **Token**: Generate a personal access token from your Bar Assistant profile
3. **Bar ID**: Find your bar ID in the Bar Assistant UI (usually 1 for your first bar)

## Usage with Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "bar-assistant": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/the-real-py/bar-assistant-mcp",
        "bar-assistant-mcp",
        "http://localhost:8000/api",
        "your_token_here",
        "1"
      ]
    }
  }
}
```

Or using environment variables:

```json
{
  "mcpServers": {
    "bar-assistant": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/the-real-py/bar-assistant-mcp",
        "bar-assistant-mcp"
      ],
      "env": {
        "BAR_ASSISTANT_API_URL": "http://localhost:8000/api",
        "BAR_ASSISTANT_TOKEN": "your_token_here",
        "BAR_ASSISTANT_BAR_ID": "1"
      }
    }
  }
}
```

## Available Tools

### `get_shelf_ingredients`
List all ingredients on your bar shelf.

### `get_shelf_cocktails`
See all cocktails you can make with your current ingredients.

### `add_ingredients_to_shelf`
Add ingredients to your shelf by their IDs.

### `remove_ingredients_from_shelf`
Remove ingredients from your shelf.

### `search_ingredients`
Search for ingredients by name to find their IDs.

## Resources

- `bar://shelf/ingredients` - Your bar shelf ingredients
- `bar://shelf/cocktails` - Cocktails you can make

## Development

Clone and install in development mode:

```bash
git clone https://github.com/the-real-py/bar-assistant-mcp
cd bar-assistant-mcp
pip install -e .
```

## License

MIT

## Links

- [Bar Assistant](https://barassistant.app/)
- [Bar Assistant Documentation](https://bar-assistant.github.io/docs/)
- [MCP Documentation](https://modelcontextprotocol.io/)