import abc
import asyncio
import importlib
import os
import sys
import asyncio
from pathlib import Path

from fastapi import Request


class BasePlugin(abc.ABC):
    """Abstract class for all plugins"""
    auto_exec = True

    @abc.abstractmethod
    async def exec(self, request: Request, _: any) -> any:
        """Executes the plugin with given data"""
        raise Exception("not implemented")

class PluginManager:
    def __init__(self, plugin_folder="src/plugins/webplugs/extended_plugs"):
        self.plugin_folder = Path(plugin_folder)
        self.plugins = {}

    def load_plugins(self):
        sys.path.insert(0, str(self.plugin_folder.parent))  
        for file in self.plugin_folder.glob("*.py"):
            if file.stem == "__init__":
                continue  # Skip __init__.py
            
            module_name = f"src.plugins.webplugs.extended_plugs.{file.stem}"  
            module = importlib.import_module(module_name)

            # Find all plugin classes
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr is not BasePlugin:
                    self.plugins[file.stem] = attr() 

    async def run(self, name, data):
        """Execute a single plugin asynchronously"""
        if name in self.plugins:
            return await self.plugins[name].exec(data)
        else:
            raise ValueError(f"Plugin '{name}' not found. in {self.plugins}")

    async def execute(self, request: Request, data=None):
        """Execute only plugins where `auto_exec=True`"""
        tasks = [plugin.exec(request, data) for plugin in self.plugins.values() if plugin.auto_exec]
        return await asyncio.gather(*tasks) if tasks else []
    

PLUGIN_MANAGER = PluginManager()
