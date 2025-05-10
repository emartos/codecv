from abc import ABC, abstractmethod
from datetime import datetime

from src.config.configuration_manager import ConfigurationManager
from src.llm.model_provider import ModelProvider


class FormatInterface(ABC):
    """
    Abstract base class (interface) for defining a contract for exporter classes.
    All concrete classes implementing this interface must provide their own implementation
    for the `export` method.

    Attributes:
        output_dir (str): The directory in which the exported files will be saved.
    """

    def __init__(self, output_dir: str = "./output"):
        """
        Initializes the ExporterInterface with an optional output directory.

        Args:
            output_dir (str): The directory where exported files will be saved.
                              Defaults to "./output".
        """
        self.output_dir = output_dir
        self.configuration_manager = ConfigurationManager()
        llm_provider = self.configuration_manager.get_llm_provider()
        model_provider = ModelProvider()
        self.model = model_provider.get(llm_provider)

        # Translate sections
        self._untitled = self._translate_term("Untitled")
        self._not_apply = self._translate_term("N/A")
        self._author = self._translate_term("Author")
        self._extract = self._translate_term("Professional abstract")
        self._job_title = self._translate_term("Job Title")
        self._company = self._translate_term("Company")
        self._time_period = self._translate_term("Time Period")
        self._description = self._translate_term("Description")
        self._domain = self._translate_term("Domain")
        self._technologies = self._translate_term("Main technologies")
        self._name = self._translate_term("Project/Employer name")
        self._position = self._translate_term("Position")
        self._highlights = self._translate_term("Highlights")

    @abstractmethod
    def export(self, author_name: str, extract: str, data: str, filename: str) -> str:
        """
        Abstract method to export a given LinkedIn profile text to a specified file.

        Args:
            author_name (str): The author's name.
            extract (str): The CV extract.
            data (str): The profile data to be exported.
            filename (str): The name of the file where the content will be saved.

        Returns:
            str: The full path of the file where the content was exported.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        pass

    def _translate_term(self, term: str) -> str:
        """
        Translates a given term into the target language specified in the configuration.

        This method uses the configured language model to generate a translation
        of the provided term into the target language. The target language is retrieved
        from the configuration manager.

        Args:
            term (str): The term to be translated.

        Returns:
            str: The translated term in the target language.
        """
        target_language = self.configuration_manager.get_target_language()
        prompt = f"Translate '{term}' into '{target_language}'. Respond only with the translation."
        return self.model.generate(prompt=prompt)

    def _format_date(self, date: str) -> str:
        """
        Formats a date into the application's configured format.

        Args:
            date (str): The date object to be formatted.

        Returns:
            str: The formatted date as a string.
        """
        # We assume that the input date format is %Y-%m
        input_date_format = "%Y-%m"
        configuration_manager = ConfigurationManager()
        date_format = configuration_manager.get_date_format()
        try:
            date_obj = datetime.strptime(date, input_date_format)
            return date_obj.strftime(date_format)
        except ValueError:
            raise ValueError(
                f"Invalid date format: '{date}'. Expected format: {input_date_format}"
            )
