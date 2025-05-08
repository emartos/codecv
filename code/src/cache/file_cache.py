import json
import logging
from pathlib import Path
from typing import Any


class FileCache:

    @staticmethod
    def process_and_save(
        object_instance: Any,
        process_function: str,
        process_args: tuple,
        file_path: str,
    ) -> None:
        """
        Verifies whether a file exists and loads its content. If the file does not exist,
        processes data using a specified function and saves the result to a file in JSON format.

        Args:
            object_instance (object): The instance of the class that provides the processing function.
            process_function (str): The name of the function (method) to call on the object_instance.
            process_args (tuple): A tuple of arguments to pass to the processing function.
            file_path (str): The path of the file where the result will be saved.

        Returns:
            any: The loaded content from the file or the result of the processing function.
        """
        # Get the absolute path relative to the current working directory
        base_path = Path.cwd() / file_path

        # Ensure the parent directory exists
        if not base_path.parent.exists():
            logging.info(f"📂 Directory '{base_path.parent}' not found. Creating it...")
            base_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if the file exists
        if base_path.exists():
            logging.info(f"🔄 File '{base_path}' exists. Loading its content...")
            with base_path.open(encoding="utf-8") as file:
                return json.load(file)
        else:
            # If the file does not exist, process and save the result
            logging.warning(f"⚙️  File '{base_path}' not found. Processing data...")
            process_method = getattr(object_instance, process_function)
            result = process_method(*process_args)

            # Save the result to the specified file in JSON format
            base_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
            logging.info(f"✅ File '{base_path}' created and data saved.")
            return result
