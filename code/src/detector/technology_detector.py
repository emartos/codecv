import json
import logging
import os
from collections import defaultdict
from typing import DefaultDict, Dict, List

from src.config.configuration_manager import ConfigurationManager
from src.llm.model_provider import ModelProvider


class TechnologyDetector:
    """
    A class that analyzes a list of modified files and attempts to identify the technologies,
    programming languages, or frameworks that may be involved, based on file extensions.

    This class leverages a language model to generate a summary of related technologies
    based on the file extensions detected in a given list of modified files.
    """

    def __init__(self):
        """
        Initializes a new instance of the TechnologyDetector class.

        It retrieves the configured language model provider from the environment and
        initializes the model provider instance to communicate with the LLM (Language Model).
        """
        configuration_manager = ConfigurationManager()
        llm_provider = configuration_manager.get_llm_provider()
        model_provider = ModelProvider()
        self.model = model_provider.get(llm_provider)

    def get_project_context(
        self, readme_files: Dict[str, str], project_structure: str
    ) -> List[str]:
        """
        Analyzes the project context using README files and the project structure to infer the main technology stack.

        Args:
           readme_files (Dict[str, str]): A dictionary where keys are filenames and values are the content of the README files.
           project_structure (str): A string representation of the project's structure (first-level files and directories).

        Returns:
           List[str]: A list of detected technologies or tools used in the project.
        """
        # Combine all README contents into a single string separated by a delimiter (e.g., '---')
        combined_readme_content = "\n---\n".join(readme_files.values())

        # Determine the input prompt based on the availability of README content
        if combined_readme_content.strip():
            # Use the full prompt with README content and project structure
            prompt = f"""
                You are an AI tasked with analyzing a project's README files and its structure to identify the main technology stack or primary tools used in the project.
                Focus on programming languages, frameworks, libraries, tools, or any notable technologies explicitly mentioned in the README or implied by the project structure.
                The combined README content is enclosed between ^^^ tokens, and the project's structure is enclosed between <STRUCTURE> tags.
                If the technologies are not explicitly mentioned in the README, make your best guess based on the project structure and general software development practices.
                Return only the detected technologies or tools as a list (e.g., 'Python, Django, Postgres').
                ^^^
                {combined_readme_content}
                ^^^
                Project Structure:
                <STRUCTURE>
                {project_structure}
                </STRUCTURE>
            """.strip()
        else:
            # Use a reduced prompt using only the project structure
            prompt = f"""
                You are an AI tasked with analyzing a project's structure to identify the main technology stack or primary tools used in the project.
                Focus on programming languages, frameworks, libraries, tools, or any notable technologies implied by the project structure.
                The project's structure is enclosed between <STRUCTURE> tags.
                Return only the detected technologies or tools as a list (e.g., 'Python, Django, Postgres').
                <STRUCTURE>
                {project_structure}
                </STRUCTURE>
            """.strip()

        # Query the LLM for technologies based on the context
        response = self.model.generate(prompt=prompt)
        technology_list = [tech.strip() for tech in response.split(",")]

        return technology_list

    def detect(self, files: List, project_context: List[str]) -> List[str]:
        """
        Generates a summary of potential technologies, programming languages, or frameworks
        based on the extensions of a provided list of modified file names.

        Constructs a prompt using the unique file extensions from the given list, queries the language model to
        identify relevant technologies, and processes the response to produce a refined list of unique technologies.

        Args:
           files (List[str]): A list of file names to analyze, each potentially including a file extension.

        Returns:
           List[str]: A list of unique technologies, programming languages, or frameworks.
        """
        # Get the unique extensions with their frequency
        unique_extensions = self._get_unique_file_extensions(files)

        # Prepare the input as formatted strings
        formatted_extensions = "\n".join(
            f"{ext}: {count}" for ext, count in unique_extensions.items()
        )
        if project_context:
            main_technologies = f"The project is primarily based on the following technologies: {', '.join(project_context)}."
        else:
            main_technologies = "Not defined"

        prompt = """
            You are an AI assistant tasked with identifying technologies in a software project based on file extensions and their frequencies, contextualized with the primary technologies of the project.

            Your task is:
            - Analyze the unique file extensions and their frequencies provided below alongside the main technologies (if available).
            - Derive the relevant programming languages, frameworks, and tools implied by these extensions.
            - Explicitly identify programming languages (e.g., **Python**, **JavaScript**) alongside frameworks and tools if they are implied by the file extensions.
            - Assign relative weights (%) to each technology, reflecting their importance based on the frequencies of related file extensions and any provided context.

            Instructions:
            1. Use the input data to determine technologies and their weights (total weights must sum to exactly 100%).
            2. Produce a JSON object that contains a dictionary where the key is a technology name and the value is its weight in percentage.
            3. **Do not include any additional text, comments, arrays, or delimiters outside the JSON object.**
            4. The JSON object must follow this structure:
            {
                "TechnologyA": 50,
                "TechnologyB": 30,
                "TechnologyC": 10,
                "TechnologyD": 10
            }
            5. Do not include delimiters such as ```json.
            6. If you cannot ensure a complete and valid JSON object, ALWAYS return an empty JSON object (`{}`), and nothing else.
            7. Before returning, validate the JSON format to ensure it is well-formed and closed. If not, return `{}` instead.

            Input:
            - Main technologies: [main_technologies]
            - Unique file extensions (with count):
            ^^^
            [unique_extensions]
            ^^^
        """.strip()
        prompt = prompt.replace("[main_technologies]", main_technologies).replace(
            "[unique_extensions]", formatted_extensions
        )

        # Query the LLM.
        response = self.model.generate(prompt=prompt, temperature=0.0, max_tokens=200)
        cleaned_response = response.strip("```json").strip("```").strip()

        try:
            return json.loads(cleaned_response.strip())
        except json.JSONDecodeError as err:
            # We try to auto repair the corrupt JSON by adding a closing brace
            if response.strip().endswith(","):
                response = response.strip().rstrip(",")
            if not response.strip().endswith("}"):
                response += "}"
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {}

            logging.error(
                f"Error detecting the technologies: {str(err)}\nRaw response: {response}"
            )
            return {}

    def _get_unique_file_extensions(self, files: List[str]) -> Dict[str, int]:
        """
        Extracts unique file extensions from a list of file paths and counts their occurrences.

        Args:
           files (List[str]): A list of file paths or file names.

        Returns:
           Dict[str, int]: A dictionary where file extensions are keys and their frequencies are values.
        """
        extension_count: DefaultDict[str, int] = defaultdict(int)

        for file in files:
            _, ext = os.path.splitext(file)
            if ext:
                extension_count[ext] += 1
        return dict(extension_count)
