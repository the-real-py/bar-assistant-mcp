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


def get_headers():
    """Get HTTP headers with authentication."""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    if CONFIG["token"]:
        headers["Authorization"] = f"Bearer {CONFIG['token']}"
    if CONFIG["bar_id"]:
        headers["Bar-Assistant-Bar-Id"] = CONFIG["bar_id"]
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
                f"{CONFIG['api_url']}/bars/{CONFIG['bar_id']}/ingredients",
                headers=get_headers()
            )
            response.raise_for_status()
            data = response.json()
            
            ingredients = data.get("data", [])
            result = f"# Bar Shelf Ingredients ({len(ingredients)} total)\n\n"
            for ing in ingredients:
                result += f"- **{ing['name']}** (ID: {ing['id']})\n"
            
            return result
            
        elif uri == "bar://shelf/cocktails":
            response = await client.get(
                f"{CONFIG['api_url']}/bars/{CONFIG['bar_id']}/cocktails",
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
            name="get_shelf_ingredients",
            description="Get all ingredients currently on your bar shelf with detailed information",
            inputSchema={
                "type": "object",
                "properties": {
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
                    }
                },
                "required": ["name"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    async with httpx.AsyncClient() as client:
        
        if name == "get_shelf_ingredients":
            params = {}
            if arguments.get("page"):
                params["page"] = arguments["page"]
            
            response = await client.get(
                f"{CONFIG['api_url']}/bars/{CONFIG['bar_id']}/ingredients",
                headers=get_headers(),
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
            params = {}
            if arguments.get("page"):
                params["page"] = arguments["page"]
            
            response = await client.get(
                f"{CONFIG['api_url']}/bars/{CONFIG['bar_id']}/cocktails",
                headers=get_headers(),
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
            response = await client.post(
                f"{CONFIG['api_url']}/bars/{CONFIG['bar_id']}/ingredients/batch-store",
                headers=get_headers(),
                json={"ingredients": arguments["ingredient_ids"]}
            )
            response.raise_for_status()
            
            return [TextContent(
                type="text",
                text=f"Successfully added {len(arguments['ingredient_ids'])} ingredients to your bar shelf!"
            )]
        
        elif name == "remove_ingredients_from_shelf":
            response = await client.post(
                f"{CONFIG['api_url']}/bars/{CONFIG['bar_id']}/ingredients/batch-delete",
                headers=get_headers(),
                json={"ingredients": arguments["ingredient_ids"]}
            )
            response.raise_for_status()
            
            return [TextContent(
                type="text",
                text=f"Successfully removed {len(arguments['ingredient_ids'])} ingredients from your bar shelf!"
            )]
        
        elif name == "search_ingredients":
            response = await client.get(
                f"{CONFIG['api_url']}/ingredients",
                headers=get_headers(),
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