from mcp.server.fastmcp import FastMCP
from abc import ABC, abstractmethod


class ExtraPrompts(ABC):
    """
    Abstract class to use extra prompts needed to guide the LLM.
    Use it as a base to create extra prompts within the `integrate_prompts(mcp: FastMCP)` function.
    """

    @abstractmethod
    def integrate_prompts(self, mcp: FastMCP):
        """
        Integrates the extra prompts into the MCP. This method must be implemented by subclasses.
        """
        pass
