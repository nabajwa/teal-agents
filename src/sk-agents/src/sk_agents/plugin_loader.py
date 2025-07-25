import logging
from typing import Any

from ska_utils import ModuleLoader


class PluginLoader:
    def __init__(self, plugin_module: str | None = None):
        self.plugin_module = None
        self.custom_module = None

        self.set_plugin_module(plugin_module)

    @staticmethod
    def _parse_module_name(types_module: str) -> str:
        return types_module.split("/")[-1].split(".")[0]

    def set_plugin_module(self, plugin_module: str | None):
        self.plugin_module = plugin_module
        if self.plugin_module:
            try:
                self.custom_module = ModuleLoader.load_module(plugin_module)
            except (FileNotFoundError, ImportError, AttributeError, SyntaxError) as e:
                logging.exception(f"Failed to load module '{plugin_module}': {e}")
                raise ImportError(f"Cannot load plugin module '{plugin_module}': {e}") from e
        else:
            self.custom_module = None

    def get_plugins(self, plugin_names: list[str]) -> dict[str, Any]:
        if not self.custom_module:
            raise RuntimeError("Custom module not loaded; cannot retrieve plugins.")
        plugins = {}
        for plugin_name in plugin_names:
            if hasattr(self.custom_module, plugin_name):
                plugins[plugin_name] = getattr(self.custom_module, plugin_name)
            else:
                raise ValueError(f"Plugin {plugin_name} not found")
        return plugins


_plugin_loader: PluginLoader | None = None


def get_plugin_loader(plugin_module: str | None = None) -> PluginLoader:
    global _plugin_loader
    if not _plugin_loader:
        _plugin_loader = PluginLoader(plugin_module)
    return _plugin_loader
