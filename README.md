# Bar Assistant MCP Server

An MCP (Model Context Protocol) server for [Bar Assistant](https://barassistant.app/) - manage your home bar shelf and discover cocktails you can make.

## Features

- 📋 View ingredients on your bar shelf
- 🍸 See cocktails you can make with what you have
- ➕ Add ingredients to your shelf
- ➖ Remove ingredients from your shelf
- 🔍 Search for ingredients by name
- 🏪 Discover your available bars

## Installation

### Using uvx (Recommended)

Run directly with uvx:

```bash
uvx --from git+https://github.com/the-real-py/bar-assistant-mcp bar-assistant-mcp \
  https://bar.johnprovost.com/bar/api \
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
BAR_ASSISTANT_API_URL=https://bar.johnprovost.com/bar/api
BAR_ASSISTANT_TOKEN=your_bearer_token_here
BAR_ASSISTANT_BAR_ID=1
```

Or pass them as command-line arguments:

```bash
bar-assistant-mcp <api_url> <token> <bar_id>
```

### Getting Your Credentials

1. **API URL**: Your Bar Assistant instance URL + the API path
   - Standard setup: `http://localhost:8000/api`
   - Custom setup: Check your reverse proxy configuration (e.g., `https://bar.example.com/bar/api`)
2. **Token**: Generate a personal access token from your Bar Assistant profile settings
3. **Bar ID**: Use the `list_bars` tool to find your bar ID, or it's usually `1` for your first bar

**Important**: The `BAR_ASSISTANT_BAR_ID` is optional. If you don't set it, you can provide the `bar_id` parameter when calling tools, or use the `list_bars` tool first to discover your available bars.

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
        "https://bar.johnprovost.com/bar/api",
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
        "BAR_ASSISTANT_API_URL": "https://bar.johnprovost.com/bar/api",
        "BAR_ASSISTANT_TOKEN": "your_token_here",
        "BAR_ASSISTANT_BAR_ID": "1"
      }
    }
  }
}
```

## Available Tools

### `list_bars`
Discover all bars you have access to and get their IDs.

### `get_shelf_ingredients`
List all ingredients on your bar shelf.

**Parameters:**
- `bar_id` (optional): Bar ID to query
- `page` (optional): Page number for pagination

### `get_shelf_cocktails`
See all cocktails you can make with your current ingredients.

**Parameters:**
- `bar_id` (optional): Bar ID to query
- `page` (optional): Page number for pagination

### `add_ingredients_to_shelf`
Add ingredients to your shelf by their IDs.

**Parameters:**
- `ingredient_ids` (required): Array of ingredient IDs
- `bar_id` (optional): Bar ID to update

### `remove_ingredients_from_shelf`
Remove ingredients from your shelf.

**Parameters:**
- `ingredient_ids` (required): Array of ingredient IDs
- `bar_id` (optional): Bar ID to update

### `search_ingredients`
Search for ingredients by name to find their IDs.

**Parameters:**
- `name` (required): Ingredient name to search for
- `bar_id` (optional): Bar ID context

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

## Troubleshooting

### Finding Your API URL

The Bar Assistant API URL depends on your setup:

1. **Standard Docker setup**: `http://localhost:8000/api`
2. **Custom reverse proxy**: Check your nginx/Traefik configuration for the API route
3. **Cloud hosted**: Usually provided by your hosting service

To verify your API URL is correct, run:
```bash
curl -H "Accept: application/json" YOUR_API_URL/server/version
```

You should get a JSON response with version information.

## License

MIT

## Links

- [Bar Assistant](https://barassistant.app/)
- [Bar Assistant Documentation](https://bar-assistant.github.io/docs/)
- [MCP Documentation](https://modelcontextprotocol.io/)
