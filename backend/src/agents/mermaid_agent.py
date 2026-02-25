import os
import base64
import httpx
from typing import Dict, Any
from langchain_core.tools import tool
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition


class GauchoState(MessagesState):
    pass


@tool
async def generate_mermaid_diagram(graph_dict: Dict[str, Any]) -> str:
    """
    Takes a graph dictionary, converts it to Mermaid markup,
    and returns the rendered image URL from the mermaid.ink API.
    """
    mermaid_markup = "graph TD\n"

    nodes = graph_dict.get("nodes", [])
    for node in nodes:
        node_id = node.get("id", "")
        label = node.get("label", node_id)
        mermaid_markup += f'    {node_id}["{label}"]\n'

    edges = graph_dict.get("edges", [])
    for edge in edges:
        source = edge.get("source", "")
        target = edge.get("target", "")
        label = edge.get("label", "")
        mermaid_markup += f'    {source} -- "{label}" --> {target}\n' if label else f'    {source} --> {target}\n'

    api_key = os.environ.get("MERMAID_INK_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    graph_bytes = mermaid_markup.encode("utf8")
    base64_string = base64.urlsafe_b64encode(graph_bytes).decode("ascii")
    url = f"https://mermaid.ink/img/{base64_string}"

    max_attempts = 3

    async with httpx.AsyncClient() as client:
        for attempt in range(max_attempts):
            try:
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()

                return (
                    f"Successfully generated diagram.\n"
                    f"Image URL: {url}\n\n"
                    f"Generated Markup:\n```mermaid\n{mermaid_markup}\n```"
                )
            except httpx.HTTPError as e:
                if attempt == max_attempts - 1:
                    return f"System Error: Failed to fetch the diagram from mermaid.ink after {max_attempts} attempts. Network details: {str(e)}"
