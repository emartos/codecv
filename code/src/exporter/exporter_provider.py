import importlib
from typing import Any

from src.exporter.format.format_interface import FormatInterface


class ExporterProvider:
    """
    A factory-like class that manages and provides instances of registered exporters.
    """

    def get(self, name: str) -> Any:
        """
        Retrieves an exporter by its name.

        Args:
            name (str): The name of the class to retrieve.

        Returns:
            ModelInterface: An instance of the requested exporter.

        Raises:
            Exception: If the specified exporter is not found.
        """
        module_name = f"src.exporter.format.{name}"

        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            raise ImportError(f"The module '{module_name}' does not exist.")

        try:
            class_name = name.capitalize()
            model_class = getattr(module, class_name)
            if not issubclass(model_class, FormatInterface):
                raise TypeError(
                    f"The class {class_name} is not a subclass of FormatInterface."
                )

            return model_class()
        except AttributeError:
            raise AttributeError(
                f"The class '{class_name}' could not be found in the module '{module_name}'."
            )
