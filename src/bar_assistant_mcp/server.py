import asyncio
import os
import sys
from typing import Any
from pathlib import Path

from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
import mcp.server.stdio
import httpx
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Configuration with command-line argument support
def get_config():
    """Get configuration from environment or command-line args."""
    config = {
        "api_url": os.getenv("BAR_ASSISTANT_API_URL", "http://localhost:8000/api"),
        "token": os.getenv("BAR_ASSISTANT_TOKEN"),
        "bar_id": os.getenv("BAR_ASSISTANT_BAR_ID"),
    }
    
    # Override with command-line arguments if provided
    if len(sys.argv) > 1:
        config["api_url"] = sys.argv[1]
    if len(sys.argv) > 2:
        config["token"] = sys.argv[2]
    if len(sys.argv) > 3:
        config["bar_id"] = sys.argv[3]
    
    return config


CONFIG = get_config()
app = Server("bar-assistant-mcp")


def get_headers(bar_id=None):
    """Get HTTP headers with authentication."""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    if CONFIG["token"]:
        headers["Authorization"] = f"Bearer {CONFIG['token']}"
    
    # Use provided bar_id or fall back to config
    active_bar_id = bar_id or CONFIG["bar_id"]
    if active_bar_id:
        headers["Bar-Assistant-Bar-Id"] = str(int(active_bar_id))
    
    return headers


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available bar shelf resources."""
    return [
        Resource(
            uri="bar://shelf/ingredients",
            name="Bar Shelf Ingredients",
            mimeType="application/json",
            description="List of all ingredients currently on your bar shelf"
        ),
        Resource(
            uri="bar://shelf/cocktails",
            name="Bar Shelf Cocktails",
            mimeType="application/json",
            description="Cocktails you can make with ingredients on your bar shelf"
        )
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read bar shelf resources."""
    async with httpx.AsyncClient() as client:
        if uri == "bar://shelf/ingredients":
            response = await client.get(
                f"{CONFIG['api_url']}/ingredients",
                headers=get_headers(),
                params={"filter[bar_shelf]": "true"}
            )
            response.raise_for_status()
            data = response.json()
            
            ingredients = data.get("data", [])
            result = f"# Bar Shelf Ingredients ({len(ingredients)} total)\n\n"
            for ing in ingredients:
                result += f"- **{ing['name']}** (ID: {ing['id']})\n"
            
            return result
            
        elif uri == "bar://shelf/cocktails":
            bar_id = CONFIG.get("bar_id")
            if not bar_id:
                return "# Error: No bar ID configured\n\nPlease set BAR_ASSISTANT_BAR_ID or use list_bars to find your bar ID."
            
            response = await client.get(
                f"{CONFIG['api_url']}/bars/{int(bar_id)}/cocktails",
                headers=get_headers()
            )
            response.raise_for_status()
            data = response.json()
            
            cocktails = data.get("data", [])
            result = f"# Cocktails You Can Make ({len(cocktails)} total)\n\n"
            for cocktail in cocktails:
                result += f"- **{cocktail['name']}**\n"
                if cocktail.get('short_ingredients'):
                    result += f"  Ingredients: {', '.join(cocktail['short_ingredients'])}\n"
            
            return result
    
    raise ValueError(f"Unknown resource: {uri}")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available bar tools."""
    return [
        Tool(
            name="list_bars",
            description="List all bars you have access to and get their IDs",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_shelf_ingredients",
            description="Get all ingredients currently on your bar shelf with detailed information",
            inputSchema={
                "type": "object",
                "properties": {
                    "bar_id": {
                        "type": "number",
                        "description": "Bar ID (optional if BAR_ASSISTANT_BAR_ID is set)"
                    },
                    "page": {
                        "type": "number",
                        "description": "Page number for pagination (optional)"
                    }
                }
            }
        ),
        Tool(
            name="get_shelf_cocktails",
            description="Get all cocktails you can make with ingredients on your bar shelf",
            inputSchema={
                "type": "object",
                "properties": {
                    "bar_id": {
                        "type": "number",
                        "description": "Bar ID (optional if BAR_ASSISTANT_BAR_ID is set)"
                    },
                    "page": {
                        "type": "number",
                        "description": "Page number for pagination (optional)"
                    }
                }
            }
        ),
        Tool(
            name="add_ingredients_to_shelf",
            description="Add ingredients to your bar shelf by their IDs",
            inputSchema={
                "type": "object",
                "properties": {
                    "ingredient_ids": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Array of ingredient IDs to add to shelf"
                    },
                    "bar_id": {
                        "type": "number",
                        "description": "Bar ID (optional if BAR_ASSISTANT_BAR_ID is set)"
                    }
                },
                "required": ["ingredient_ids"]
            }
        ),
        Tool(
            name="remove_ingredients_from_shelf",
            description="Remove ingredients from your bar shelf by their IDs",
            inputSchema={
                "type": "object",
                "properties": {
                    "ingredient_ids": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Array of ingredient IDs to remove from shelf"
                    },
                    "bar_id": {
                        "type": "number",
                        "description": "Bar ID (optional if BAR_ASSISTANT_BAR_ID is set)"
                    }
                },
                "required": ["ingredient_ids"]
            }
        ),
        Tool(
            name="search_ingredients",
            description="Search for ingredients by name to find their IDs",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Ingredient name to search for"
                    },
                    "bar_id": {
                        "type": "number",
                        "description": "Bar ID (optional if BAR_ASSISTANT_BAR_ID is set)"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="create_ingredient",
            description="Create a new ingredient in the bar database. Use this when an ingredient doesn't exist and needs to be created before adding to a cocktail.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the ingredient (required)"
                    },
                    "strength": {
                        "type": "number",
                        "description": "Alcohol strength/percentage (optional, e.g., 40 for 40% ABV)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the ingredient (optional)"
                    },
                    "origin": {
                        "type": "string",
                        "description": "Origin/country of the ingredient (optional)"
                    },
                    "color": {
                        "type": "string",
                        "description": "Hex color code (optional, e.g., '#ffffff')"
                    },
                    "parent_ingredient_id": {
                        "type": "number",
                        "description": "Parent ingredient ID for categorization (optional)"
                    },
                    "units": {
                        "type": "string",
                        "description": "Default units for this ingredient (optional, e.g., 'ml', 'oz', 'dash')"
                    },
                    "bar_id": {
                        "type": "number",
                        "description": "Bar ID (optional if BAR_ASSISTANT_BAR_ID is set)"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="create_cocktail",
            description="Create a new cocktail recipe. First use search_ingredients to find ingredient IDs, then use create_ingredient for any missing ingredients.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the cocktail (required)"
                    },
                    "instructions": {
                        "type": "string",
                        "description": "Step-by-step instructions for making the cocktail (required)"
                    },
                    "ingredients": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "ingredient_id": {
                                    "type": "number",
                                    "description": "ID of the ingredient (required)"
                                },
                                "amount": {
                                    "type": "number",
                                    "description": "Amount of the ingredient (required)"
                                },
                                "units": {
                                    "type": "string",
                                    "description": "Units for the amount (optional, e.g., 'ml', 'oz', 'dash')"
                                },
                                "optional": {
                                    "type": "boolean",
                                    "description": "Whether this ingredient is optional (optional)"
                                },
                                "note": {
                                    "type": "string",
                                    "description": "Additional note for this ingredient (optional)"
                                },
                                "sort": {
                                    "type": "number",
                                    "description": "Sort order for the ingredient (optional)"
                                }
                            },
                            "required": ["ingredient_id", "amount"]
                        },
                        "description": "Array of ingredients with their IDs and amounts (required)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the cocktail (optional)"
                    },
                    "garnish": {
                        "type": "string",
                        "description": "Garnish for the cocktail (optional)"
                    },
                    "source": {
                        "type": "string",
                        "description": "Source/origin of the recipe (optional)"
                    },
                    "glass_id": {
                        "type": "number",
                        "description": "ID of the glass type to use (optional)"
                    },
                    "method_id": {
                        "type": "number",
                        "description": "ID of the mixing method - shaken, stirred, etc. (optional)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of tags for the cocktail (optional)"
                    },
                    "bar_id": {
                        "type": "number",
                        "description": "Bar ID (optional if BAR_ASSISTANT_BAR_ID is set)"
                    }
                },
                "required": ["name", "instructions", "ingredients"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    async with httpx.AsyncClient() as client:
        
        if name == "list_bars":
            response = await client.get(
                f"{CONFIG['api_url']}/bars",
                headers=get_headers()
            )
            response.raise_for_status()
            data = response.json()
            
            result = "Available bars:\n\n"
            for bar in data.get('data', []):
                result += f"**{bar['name']}** (ID: {bar['id']})\n"
                result += f"  Slug: {bar['slug']}\n\n"
            
            return [TextContent(type="text", text=result)]
        
        if name == "get_shelf_ingredients":
            bar_id = arguments.get("bar_id") or CONFIG["bar_id"]
            if not bar_id:
                return [TextContent(
                    type="text",
                    text="Error: No bar ID provided. Use list_bars to find your bar ID or set BAR_ASSISTANT_BAR_ID."
                )]
            
            params = {"filter[bar_shelf]": "true"}
            if arguments.get("page"):
                params["page"] = arguments["page"]
            
            response = await client.get(
                f"{CONFIG['api_url']}/ingredients",
                headers=get_headers(bar_id),
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            return [TextContent(
                type="text",
                text=f"Found {len(data.get('data', []))} ingredients on your bar shelf:\n\n" + 
                     "\n".join([f"- {ing['name']} (ID: {ing['id']})" for ing in data.get('data', [])])
            )]
        
        elif name == "get_shelf_cocktails":
            bar_id = arguments.get("bar_id") or CONFIG["bar_id"]
            if not bar_id:
                return [TextContent(
                    type="text",
                    text="Error: No bar ID provided. Use list_bars to find your bar ID or set BAR_ASSISTANT_BAR_ID."
                )]
            
            params = {}
            if arguments.get("page"):
                params["page"] = arguments["page"]
            
            response = await client.get(
                f"{CONFIG['api_url']}/bars/{int(bar_id)}/cocktails",
                headers=get_headers(bar_id),
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            result = f"You can make {len(data.get('data', []))} cocktails:\n\n"
            for cocktail in data.get('data', []):
                result += f"**{cocktail['name']}** (ID: {cocktail['id']})\n"
                if cocktail.get('short_ingredients'):
                    result += f"  • {', '.join(cocktail['short_ingredients'])}\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "add_ingredients_to_shelf":
            bar_id = arguments.get("bar_id") or CONFIG["bar_id"]
            if not bar_id:
                return [TextContent(
                    type="text",
                    text="Error: No bar ID provided. Use list_bars to find your bar ID or set BAR_ASSISTANT_BAR_ID."
                )]
            
            ingredient_ids = [int(id) for id in arguments["ingredient_ids"]]
            
            response = await client.post(
                f"{CONFIG['api_url']}/bars/{int(bar_id)}/ingredients/batch-store",
                headers=get_headers(bar_id),
                json={"ingredients": ingredient_ids}
            )
            response.raise_for_status()
            
            return [TextContent(
                type="text",
                text=f"Successfully added {len(ingredient_ids)} ingredients to your bar shelf!"
            )]
        
        elif name == "remove_ingredients_from_shelf":
            bar_id = arguments.get("bar_id") or CONFIG["bar_id"]
            if not bar_id:
                return [TextContent(
                    type="text",
                    text="Error: No bar ID provided. Use list_bars to find your bar ID or set BAR_ASSISTANT_BAR_ID."
                )]
            
            ingredient_ids = [int(id) for id in arguments["ingredient_ids"]]
            
            response = await client.post(
                f"{CONFIG['api_url']}/bars/{int(bar_id)}/ingredients/batch-delete",
                headers=get_headers(bar_id),
                json={"ingredients": ingredient_ids}
            )
            response.raise_for_status()
            
            return [TextContent(
                type="text",
                text=f"Successfully removed {len(ingredient_ids)} ingredients from your bar shelf!"
            )]
        
        elif name == "search_ingredients":
            bar_id = arguments.get("bar_id") or CONFIG["bar_id"]
            
            response = await client.get(
                f"{CONFIG['api_url']}/ingredients",
                headers=get_headers(bar_id),
                params={"filter[name]": arguments["name"]}
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get('data'):
                return [TextContent(type="text", text="No ingredients found matching your search.")]
            
            result = "Found ingredients:\n\n"
            for ing in data.get('data', []):
                result += f"- **{ing['name']}** (ID: {ing['id']})\n"
                if ing.get('description'):
                    result += f"  {ing['description'][:100]}...\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "create_ingredient":
            bar_id = arguments.get("bar_id") or CONFIG["bar_id"]
            
            # Build the ingredient payload
            payload = {
                "name": arguments["name"]
            }
            
            # Add optional fields if provided
            if arguments.get("strength") is not None:
                payload["strength"] = float(arguments["strength"])
            if arguments.get("description"):
                payload["description"] = arguments["description"]
            if arguments.get("origin"):
                payload["origin"] = arguments["origin"]
            if arguments.get("color"):
                payload["color"] = arguments["color"]
            if arguments.get("parent_ingredient_id") is not None:
                payload["parent_ingredient_id"] = int(arguments["parent_ingredient_id"])
            if arguments.get("units"):
                payload["units"] = arguments["units"]
            
            response = await client.post(
                f"{CONFIG['api_url']}/ingredients",
                headers=get_headers(bar_id),
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            ingredient = data.get("data", {})
            result = f"Successfully created ingredient!\n\n"
            result += f"**{ingredient.get('name')}** (ID: {ingredient.get('id')})\n"
            if ingredient.get('strength'):
                result += f"  Strength: {ingredient.get('strength')}%\n"
            if ingredient.get('description'):
                result += f"  Description: {ingredient.get('description')}\n"
            if ingredient.get('origin'):
                result += f"  Origin: {ingredient.get('origin')}\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "create_cocktail":
            bar_id = arguments.get("bar_id") or CONFIG["bar_id"]
            
            # Build the cocktail payload
            payload = {
                "name": arguments["name"],
                "instructions": arguments["instructions"],
                "ingredients": []
            }
            
            # Process ingredients array
            for ing in arguments["ingredients"]:
                ingredient_entry = {
                    "ingredient_id": int(ing["ingredient_id"]),
                    "amount": float(ing["amount"])
                }
                if ing.get("units"):
                    ingredient_entry["units"] = ing["units"]
                if ing.get("optional") is not None:
                    ingredient_entry["optional"] = ing["optional"]
                if ing.get("note"):
                    ingredient_entry["note"] = ing["note"]
                if ing.get("sort") is not None:
                    ingredient_entry["sort"] = int(ing["sort"])
                payload["ingredients"].append(ingredient_entry)
            
            # Add optional fields if provided
            if arguments.get("description"):
                payload["description"] = arguments["description"]
            if arguments.get("garnish"):
                payload["garnish"] = arguments["garnish"]
            if arguments.get("source"):
                payload["source"] = arguments["source"]
            if arguments.get("glass_id") is not None:
                payload["glass_id"] = int(arguments["glass_id"])
            if arguments.get("method_id") is not None:
                payload["method_id"] = int(arguments["method_id"])
            if arguments.get("tags"):
                payload["tags"] = arguments["tags"]
            
            response = await client.post(
                f"{CONFIG['api_url']}/cocktails",
                headers=get_headers(bar_id),
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            cocktail = data.get("data", {})
            result = f"Successfully created cocktail!\n\n"
            result += f"**{cocktail.get('name')}** (ID: {cocktail.get('id')})\n"
            if cocktail.get('description'):
                result += f"  Description: {cocktail.get('description')}\n"
            if cocktail.get('garnish'):
                result += f"  Garnish: {cocktail.get('garnish')}\n"
            if cocktail.get('instructions'):
                result += f"\n**Instructions:**\n{cocktail.get('instructions')}\n"
            
            return [TextContent(type="text", text=result)]
    
    raise ValueError(f"Unknown tool: {name}")


async def run_server():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Main entry point."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
