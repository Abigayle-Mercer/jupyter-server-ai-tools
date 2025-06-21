import re
from typing import Callable

from pydantic import BaseModel, ConfigDict, Field, model_validator

def get_doc_description(func: Callable) -> str:
    """
    Extract the first paragraph from a function's docstring using regex.
    
    Args:
        func (callable): The function to extract the description from
    
    Returns:
        str: The first paragraph of the docstring, or an empty string if no docstring exists
    """
    if not func.__doc__:
        return ""
    
    # Use regex to match the first paragraph (text before the first double newline or end of string)
    match = re.match(r'^(.*?)(?:\n\n|$)', func.__doc__.strip(), re.DOTALL)
    
    return match.group(1).strip() if match else ""


class Tool(BaseModel):
    callable: Callable = Field(exclude=True)
    name: str | None = None
    description: str | None = None
    read: bool = False
    write: bool = False
    execute: bool = False
    delete: bool = False

    @model_validator(mode="after")
    def set_name_description(self):
        if not self.name:
            if hasattr(self.callable, "__name__") and self.callable.__name__:
                self.name = self.callable.__name__
            else:
                raise ValueError("Unable to extract name from callable")
        
        if not self.description:
            self.description = get_doc_description(self.callable)

        return self

    def __eq__(self, other):
        if not isinstance(other, Tool):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class ToolSet(set):
    def add(self, item):
        if item in self:
            raise ValueError(f"Tool with name '{item.name}' already exists in the set")
        super().add(item)


class Toolkit(BaseModel):
    name: str
    description: str | None = None
    tools: ToolSet = Field(default_factory=ToolSet)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def add_tool(self, tool: Tool):
        self.tools.add(tool)

    def find_tools(
        self, read: bool = False, write: bool = False, execute: bool = False, delete: bool = False
    ) -> ToolSet[Tool]:
        toolset = ToolSet()
        for tool in self.tools:
            if (
                tool.read == read
                and tool.write == write
                and tool.execute == execute
                and tool.delete == delete
            ):
                toolset.add(tool)

        return toolset

    def __eq__(self, other):
        if not isinstance(other, Toolkit):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class ToolkitSet(set):
    def add(self, item):
        if item in self:
            raise ValueError(f"Toolkit with name '{item.name}' already exists.")
        super().add(item)

    def model_dump_json(self):
        items = []
        for item in self:
            items.append(item.model_dump_json())

        return "[" + ",".join(items) + "]"

class ToolkitRegistry(BaseModel):
    toolkits: ToolkitSet[Toolkit] = Field(default_factory=ToolkitSet)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def register_toolkit(self, toolkit: Toolkit):
        self.toolkits.add(toolkit)

    def list_toolkits(self):
        toolkits = ToolkitSet()
        for toolkit in self.toolkits:
            toolkits.add(toolkit)
        
        return toolkits

    def get_toolkit(
        self,
        name: str,
        read: bool = False,
        write: bool = False,
        execute: bool = False,
        delete: bool = False,
    ) -> Toolkit:
        toolkit_in_registry = self._find_toolkit(name)
        if toolkit_in_registry:
            tools = toolkit_in_registry.find_tools(
                read=read, write=write, execute=execute, delete=delete
            )
            return Toolkit(name=toolkit_in_registry.name, tools=tools)
        else:
            raise LookupError(f"Tookit with {name=} not found in registry.")
    
    def _find_toolkit(self, name: str) -> Toolkit | None:
        for toolkit in self.toolkits:
            if toolkit.name == name:
                return toolkit
