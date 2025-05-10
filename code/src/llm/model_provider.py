import importlib

from src.llm.provider.model_interface import ModelInterface


class ModelProvider:
    """
    A factory-like class that manages and provides instances of registered models.
    """

    def get(self, name: str) -> ModelInterface:
        """
        Retrieves a model by its name.

        Args:
            name (str): The name of the class to retrieve.

        Returns:
            ModelInterface: An instance of the requested model.

        Raises:
            Exception: If the specified model provider is not found.
        """
        module_name = f"src.llm.provider.{name}"

        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            raise ImportError(f"The module '{module_name}' does not exist.")

        try:
            class_name = name.capitalize()
            model_class = getattr(module, class_name)
            if not issubclass(model_class, ModelInterface):
                raise TypeError(
                    f"The class {class_name} is not a subclass of ModelInterface."
                )

            return model_class()
        except AttributeError:
            raise AttributeError(
                f"The class '{class_name}' could not be found in the module '{module_name}'."
            )
