import base64
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from src.datetime.custom_datetime import CustomDatetime


class ConfigurationManager:
    """
    Handles the configuration setup for the application, including
    input collection, validation, and setting up environmental variables.
    This class is implemented as a Singleton, meaning only one
    instance will exist during execution.
    """

    VALID_EXPORT_FORMATS = ["markdown", "pdf", "linkedin", "jsonresume", "europass"]
    VALID_LLM_PROVIDERS = ["openai", "grok"]
    VALID_GRAMMATICAL_PERSONS = ["first", "third"]

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Override the __new__ method to ensure only one instance of the class can be created.
        """
        if cls._instance is None:
            cls._instance = super(ConfigurationManager, cls).__new__(
                cls, *args, **kwargs
            )
        return cls._instance

    def __init__(self):
        """
        Initialize the ConfigurationManager. Ensure initialization
        only occurs once, even for multiple calls to the class.
        """
        if not hasattr(self, "_initialized"):
            self.repo_path = None
            self.branch = None
            self.start_date = None
            self.end_date = None
            self.date_format = None
            self.author_name = None
            self.author_email = None
            self.export_format = None
            self.llm_provider = None
            self.target_language = None
            self.grammatical_person = None
            self.ignore_commit_keywords = None
            self._initialized = True
            self.custom_datetime = CustomDatetime()

    def collect_inputs(self) -> None:
        """
        Collects inputs required for running the application and validates them.

        Prompts the user to input configuration details such as the repository path,
        branches, date filters, author, export format, LLM provider, target language,
        grammatical person, and commit keywords to ignore. Includes validation for correct formats.

        Raises:
            ValueError: If any mandatory input is missing or invalid.

        Returns:
            None
        """
        self.repo_path = self._input("REPO_PATH", "Git repository path")
        self.repo_branches = self._input_list(
            "BRANCHES",
            "Git repository branches (separate multiple branches with commas and leave it empty to ignore this filter)",
        )

        start_date = self._input(
            "START_DATE",
            "Start Date (YYYY-MM-DD). Leave empty to avoid filtering by date",
        )
        end_date = self._input(
            "END_DATE", "End Date (YYYY-MM-DD). Leave empty to avoid filtering by date"
        )
        if start_date and end_date:
            dates = self.custom_datetime.process_input_dates(start_date, end_date)
            self.start_date = dates["start_date"]
            self.end_date = dates["end_date"]

        self.date_format = self._input(
            "DATE_FORMAT",
            "Date format. Use only year and month (i.e. %m/%Y). Leave empty to use %Y-%m",
        )
        self.custom_datetime.validate_date_format(self.date_format)

        self.author_name = self._input("AUTHOR_NAME", "Author's full name").strip('"')
        self.author_email = self._input_list(
            "AUTHOR_EMAIL",
            "Author's email address (separate multiple emails with commas)",
        )

        self.export_format = self._input_with_options(
            self.VALID_EXPORT_FORMATS, "EXPORT_FORMAT", "Export format", "markdown"
        )

        self.llm_provider = self._input_with_options(
            self.VALID_LLM_PROVIDERS, "LLM_PROVIDER", "LLM provider", "openai"
        )

        self.target_language = (os.getenv("TARGET_LANGUAGE") or "").strip() or prompt(
            "Target language: "
        ).strip().lower()

        self.grammatical_person = self._input_with_options(
            self.VALID_GRAMMATICAL_PERSONS,
            "GRAMMATICAL_PERSON",
            "Grammatical person",
            "third",
        )

        self.ignore_commit_keywords = self._input_list(
            "IGNORE_COMMIT_KEYWORDS",
            "Keywords that make a commit irrelevant (i.e. typo, minor, etc.)",
        )

    def get_repo_path(self) -> str:
        """
        Retrieves the configured Git repository path.

        Returns:
            str: The path to the Git repository.

        Raises:
            ValueError: If the repository path is not yet configured.
        """
        if not self.repo_path:
            raise ValueError("❌ The git repository path has not been configured.")
        return self.repo_path

    def get_repo_branches(self) -> Optional[List[str]]:
        """
        Retrieves the configured Git repository branches.

        Returns:
            Optional[List[str]]: A list of branches, or None if no branches are configured.
        """
        return self.repo_branches

    def get_start_date(self) -> Optional[datetime]:
        """
        Retrieves the start date for filtering repository commits.

        Returns:
            Optional[datetime]: The start date for filtering, or None if not configured.
        """
        return self.start_date

    def get_end_date(self) -> Optional[datetime]:
        """
        Retrieves the start date for filtering repository commits.

        Returns:
            Optional[datetime]: The start date for filtering, or None if not configured.
        """
        return self.end_date

    def get_date_format(self) -> str:
        """
        Retrieves the date formatting string.

        Returns:
            str: The configured date format. Defaults to '%Y-%m' if not explicitly set.
        """
        return self.date_format or "%Y-%m"

    def get_author_name(self) -> str:
        """
        Retrieves the configured author's name.

        Returns:
            str: The author's full name.

        Raises:
            ValueError: If the author's name is not yet configured.
        """
        if not hasattr(self, "author_name") or not self.author_name:
            raise ValueError("❌ The author's name has not been configured.")
        return self.author_name

    def get_author_email(self) -> List[str]:
        """
        Retrieves the email address(es) of the configured author.

        Returns:
            List[str]: A list of email addresses associated with the author.

        Raises:
            ValueError: If no email address has been configured.
        """
        if not self.author_email:
            raise ValueError("❌ The email address has not been configured.")
        return self.author_email

    def get_export_format(self) -> str:
        """
        Retrieves the selected export format.

        Returns:
            str: The configured export format, e.g., `markdown`, `pdf`.

        Raises:
            ValueError: If the export format is not yet configured.
        """
        if not self.export_format:
            raise ValueError("❌ The export method has not been configured.")
        return self.export_format

    def get_llm_provider(self) -> str:
        """
        Returns the configured Large Language Model (LLM) provider.

        Returns:
            str: The selected LLM provider, e.g., `openai`.

        Raises:
            ValueError: If the LLM provider is not yet configured.
        """
        if not self.llm_provider:
            raise ValueError("❌ The LLM provider has not been configured.")
        return self.llm_provider

    def get_target_language(self) -> str:
        """
        Retrieves the target language setting for text generation.

        Returns:
            str: The configured target language.

        Raises:
            ValueError: If the target language is not yet configured.
        """
        if not self.target_language:
            raise ValueError("❌ The target language has not been configured.")
        return self.target_language

    def get_grammatical_person(self) -> str:
        """
        Retrieves the configured grammatical person for generated text.

        Returns:
            str: The grammatical person, e.g., `first` or `third`.

        Raises:
            ValueError: If the grammatical person is not yet configured.
        """
        if not self.grammatical_person:
            raise ValueError("❌ The grammatical person has not been configured.")
        return self.grammatical_person

    def get_ignore_commit_keywords(self) -> List[str]:
        """
        Retrieves the list of keywords for commit messages to ignore during filtering.

        These keywords allow exclusion of commits based on their messages.

        Returns:
            List[str]: A list of keywords to ignore in commit messages.
        """
        return self.ignore_commit_keywords

    def get_configuration(self) -> Dict[str, str]:
        """
        Retrieves the collected and validated configuration.

        Returns:
            Dict[str, Any]: A dictionary containing the configuration values.
        """
        return {
            "repo_path": self.repo_path,
            "author_name": self.author_name,
            "author_email": self.author_email,
            "export_format": self.export_format,
            "llm_provider": self.llm_provider,
            "target_language": self.target_language,
            "grammatical_person": self.grammatical_person,
        }

    def generate_hash(self, date: Optional[datetime] = None) -> str:
        """
        Calculates a unique short hash based on various configuration attributes.

        This method incorporates mandatory attributes such as 'repo_path', 'author_email', and 'llm_provider'.
        Optional attributes like 'start_date', 'end_date', and a specific datetime ('date') are included if provided.

        Args:
            date (Optional[datetime]): An additional datetime object to include in the hash calculation.

        Returns:
            str: A short hash string uniquely identifying the configuration.
        """
        # Start with core fields
        combined_string = f"{self.repo_path}:{self.author_email}:{self.llm_provider}"

        # Add start_date and end_date to the hash if they are set
        if self.start_date:
            combined_string += f":{self.start_date.strftime('%Y-%m-%d')}"
        if self.end_date:
            combined_string += f":{self.end_date.strftime('%Y-%m-%d')}"

        # Add the additional date if provided
        if date:
            combined_string += f":{date.strftime('%Y-%m-%d %H:%M:%S')}"

        # Generate hash
        hash_object = hashlib.sha256(combined_string.encode())
        short_hash = (
            base64.urlsafe_b64encode(hash_object.digest()).decode("utf-8").rstrip("=")
        )

        return short_hash

    def _input(self, env_key: str, label: str) -> str:
        """
        Prompts the user for input, with optional support for environment variable defaults.

        Args:
            env_key (str): The name of the environment variable to check for a default input value.
            label (str): The label or message displayed to the user in the input prompt.

        Returns:
            str: The user's input as a string.
        """
        user_input = (os.getenv(env_key) or "").strip() or prompt(f"{label}: ").strip()

        return user_input

    def _input_list(self, env_key: str, label: str) -> List[str]:
        """
        Prompts the user for input, with optional support for environment variable defaults
        and formatting the input as a list.

        Args:
            env_key (str): The name of the environment variable to check for a default input value.
            label (str): The label or message displayed to the user in the input prompt.

        Returns:
            List[str]: The user's input as list of strings.
        """
        user_input = self._input(env_key, label)
        list = [part.strip() for part in user_input.split(",") if part.strip()]

        return list

    def _input_with_options(
        self,
        options: List[str],
        env_key: str,
        label: str,
        default_option: Optional[str] = None,
    ) -> str:
        """
        Prompts the user for input from a predefined list of valid options,
        with support for autocompletion and fallback to environment variables.

        Args:
            options (List[str]): A list of valid options the user can choose from.
            env_key (str): The name of the environment variable to check for a default input value.
            label (str): The label or message displayed to the user in the input prompt.
            default_option (str, optional): The default option to use if the user provides no input. Defaults to None.

        Returns:
            str: The user's selected option.

        Raises:
            ValueError: If the user's input is not in the list of valid options.
        """
        completer = WordCompleter(options, ignore_case=True)
        default_option_str = ""
        if default_option:
            default_option_str = f"; default is '{default_option}'"

        user_input = (os.getenv(env_key) or "").strip() or prompt(
            f"{label} (valid options: {', '.join(options)}{default_option_str}): ",
            completer=completer,
        ).strip().lower()

        if default_option and not user_input:
            user_input = default_option

        if user_input not in options:
            raise ValueError(f"❌ Invalid {label.lower()}: '{user_input}'.")

        return user_input
