# Bar Assistant MCP Server

An MCP (Model Context Protocol) server for [Bar Assistant](https://barassistant.app/) - manage your home bar shelf and discover cocktails you can make.

## Features

- 📋 View ingredients on your bar shelf
- 🍸 See cocktails you can make with what you have
- ➕ Add ingredients to your shelf
- ➖ Remove ingredients from your shelf
- 🔍 Search for ingredients by name
- 🏪 Discover your available bars
- 🧪 Create new ingredients
- 🍹 Create new cocktail recipes
- ✏️ Update existing cocktail recipes

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

### `create_ingredient`
Create a new ingredient in the bar database. Use this when an ingredient doesn't exist and needs to be created before adding to a cocktail.

**Parameters:**
- `name` (required): Name of the ingredient
- `strength` (optional): Alcohol strength/percentage (e.g., 40 for 40% ABV)
- `description` (optional): Description of the ingredient
- `origin` (optional): Origin/country of the ingredient
- `color` (optional): Hex color code (e.g., '#ffffff')
- `parent_ingredient_id` (optional): Parent ingredient ID for categorization
- `units` (optional): Default units for this ingredient (e.g., 'ml', 'oz', 'dash')
- `bar_id` (optional): Bar ID context

### `create_cocktail`
Create a new cocktail recipe. First use `search_ingredients` to find ingredient IDs, then use `create_ingredient` for any missing ingredients.

**Parameters:**
- `name` (required): Name of the cocktail
- `instructions` (required): Step-by-step instructions for making the cocktail
- `ingredients` (required): Array of ingredients with:
  - `ingredient_id` (required): ID of the ingredient
  - `amount` (required): Amount of the ingredient
  - `units` (optional): Units for the amount (e.g., 'ml', 'oz', 'dash')
  - `optional` (optional): Whether this ingredient is optional
  - `note` (optional): Additional note for this ingredient
  - `sort` (optional): Sort order for the ingredient
- `description` (optional): Description of the cocktail
- `garnish` (optional): Garnish for the cocktail
- `source` (optional): Source/origin of the recipe
- `glass_id` (optional): ID of the glass type to use
- `method_id` (optional): ID of the mixing method (shaken, stirred, etc.)
- `tags` (optional): Array of tags for the cocktail
- `bar_id` (optional): Bar ID context

**Example - Creating a Margarita:**
```
1. search_ingredients(name="tequila") → ID: 45
2. search_ingredients(name="lime juice") → ID: 89  
3. search_ingredients(name="triple sec") → ID: 23
4. create_cocktail(
     name="Margarita",
     instructions="1. Add all ingredients to shaker with ice\n2. Shake well\n3. Strain into salt-rimmed glass",
     ingredients=[
       {"ingredient_id": 45, "amount": 60, "units": "ml"},
       {"ingredient_id": 89, "amount": 30, "units": "ml"},
       {"ingredient_id": 23, "amount": 30, "units": "ml"}
     ],
     garnish="Lime wheel, salt rim"
   )
```

### `update_cocktail`
Update an existing cocktail recipe. Use this to modify the name, instructions, ingredients, or other details of a cocktail.

**Parameters:**
- `id` (required): ID of the cocktail to update
- `name` (required): Name of the cocktail
- `instructions` (required): Step-by-step instructions for making the cocktail
- `ingredients` (required): Array of ingredients with:
  - `ingredient_id` (required): ID of the ingredient
  - `amount` (required): Amount of the ingredient
  - `units` (optional): Units for the amount (e.g., 'ml', 'oz', 'dash')
  - `optional` (optional): Whether this ingredient is optional
  - `note` (optional): Additional note for this ingredient
  - `sort` (optional): Sort order for the ingredient
- `description` (optional): Description of the cocktail
- `garnish` (optional): Garnish for the cocktail
- `source` (optional): Source/origin of the recipe
- `glass_id` (optional): ID of the glass type to use
- `method_id` (optional): ID of the mixing method (shaken, stirred, etc.)
- `tags` (optional): Array of tags for the cocktail
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
