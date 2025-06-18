from typing import Callable, Optional

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator


class Tool(BaseModel):
    callable: Callable
    read: bool = False
    write: bool = False
    execute: bool = False
    delete: bool = False
    _callable_name: str = PrivateAttr()

    @model_validator(mode="after")  # Use model_validator for Pydantic V2+
    def populate_callable_name(self):
        if hasattr(self.callable, "__name__") and self.callable.__name__:
            self._callable_name = self.callable.__name__
        else:
            raise ValueError("Unable to extract name from callable")
        return self

    def __eq__(self, other):
        if not isinstance(other, Tool):
            return False
        return self._callable_name == other._callable_name

    def __hash__(self):
        return hash(self._callable_name)


class ToolSet(set):
    def add(self, item):
        if item in self:
            raise ValueError(f"Tool with name '{item._callable_name}' already exists in the set")
        super().add(item)


class Toolkit(BaseModel):
    name: str
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


class ToolkitRegistry(BaseModel):
    toolkits: ToolkitSet[Toolkit]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def register_toolkit(self, toolkit: Toolkit):
        self.toolkits.add(toolkit)

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
