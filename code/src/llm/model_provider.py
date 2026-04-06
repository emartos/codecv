import importlib

from src.llm.provider.model_interface import ModelInterface


class ModelProvider:
    """
    A factory-like class that manages and provides instances of registered models.
    """

    VALID_PROVIDERS = ["openai", "grok", "ollama", "googlegenai", "smart"]

    def get(self, name: str, max_tokens: int = 4000) -> ModelInterface:
        """
        Retrieves a model by its name.

        Args:
            name (str): The name of the class to retrieve.
            max_tokens (int): The maximum number of tokens allowed in the response.

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

            return model_class(max_tokens=max_tokens)
        except AttributeError as err:
            raise AttributeError(str(err))
