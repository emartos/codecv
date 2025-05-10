import json
import logging
import time
from typing import Any, Dict, Generator, List

from src.cache.file_cache import FileCache
from src.config.configuration_manager import ConfigurationManager
from src.detector.technology_detector import TechnologyDetector
from src.exporter.exporter_provider import ExporterProvider
from src.git_parser.commit_extractor import CommitExtractor
from src.llm.model_provider import ModelProvider
from src.llm.prompt_builder import PromptBuilder
from src.logger.logger import Logger
from src.summarizer.daily_summarizer import DailySummarizer
from src.summarizer.monthly_summarizer import MonthlySummarizer
from src.summarizer.weekly_summarizer import WeeklySummarizer


class CVGenerator:
    """
    Class to encapsulate the CV generation workflow.
    This class handles configuration, commit extraction, data summarization,
    LLM processing, and exporting the final CV.
    """

    def __init__(self) -> None:
        """
        Initializes the CVGenerator class and sets up the ConfigurationManager and hash.
        """
        Logger.setup()
        self.configuration_manager = ConfigurationManager()
        self.commit_extractor = CommitExtractor()
        self.hash = ""

    def run(self) -> None:
        """
        Orchestrates the entire CV generation workflow.
        Collects inputs, extracts commits, summarizes data, processes LLM, and exports the CV.

        Returns:
            None
        """
        start_time = time.time()
        try:
            # Stage 1: Input data collection
            self._collect_inputs()

            # Stage 2: Commits extraction and project context retrieval
            commits_generator = self._extract_commits()
            project_context = self._get_project_context()

            # Stage 3: Summarization
            monthly_summaries = self._summarize(commits_generator, project_context)

            # Stage 4: LLM processing
            cv_data = self._llm_processing(monthly_summaries, project_context)

            # Stage 5: Data export
            self._export(cv_data)
        except ValueError as err:
            logging.error(f"Error during CV generation process: {err}")
        except Exception as err:
            logging.exception(f"Unexpected error during execution: {err}")
        finally:
            total_time = time.time() - start_time
            logging.info(f"Total execution time: {total_time:.2f} seconds.")

    def _collect_inputs(self) -> None:
        """
        Collects inputs such as repository path, author email, and other configuration details
        from ConfigurationManager.
        Generates a unique hash for this workflow.

        Returns:
            None
        """
        self.configuration_manager.collect_inputs()
        repo_path = self.configuration_manager.get_repo_path()
        # Adding the last commit date, the hash reflects the current status of the repository
        last_commit_date = self.commit_extractor.get_last_commit_date(repo_path)
        self.hash = self.configuration_manager.generate_hash(last_commit_date)

    def _extract_commits(self) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Extracts Git commits authored by the specified email from the repository as a generator.

        Yields:
            Generator[List[Dict[str, Any]]]: Batches of commits produced by the generator.
        """
        logging.info("Extracting author's commits...")

        repo_path = self.configuration_manager.get_repo_path()
        author_email = self.configuration_manager.get_author_email()
        start_date = self.configuration_manager.get_start_date()
        end_date = self.configuration_manager.get_end_date()
        repo_branches = self.configuration_manager.get_repo_branches()
        ignore_commit_keywords = self.configuration_manager.get_ignore_commit_keywords()

        for batch in self.commit_extractor.extract_commits_by_author(
            repo_path=repo_path,
            repo_branches=repo_branches,
            author_email=author_email,
            start_date=start_date,
            end_date=end_date,
            ignore_commit_keywords=ignore_commit_keywords,
        ):
            if not batch:
                logging.warning("Empty batch received during commit extraction.")
                continue
            yield batch

    def _get_project_context(self) -> List[str]:
        """
        Retrieves the project's context by analyzing README files and the project structure.

        Extracts and analyzes README files and the project structure to gather relevant
        contextual information about the project. Utilizes a `TechnologyDetector` to infer
        the project's context based on the content of README files and the overall structure.

        Returns:
           List[str]: A list of strings representing the project's context.
        """
        logging.info("Extracting README files to get the project's context...")
        repo_path = self.configuration_manager.get_repo_path()
        readme_files = self.commit_extractor.get_root_readme_files(repo_path)
        project_structure = self.commit_extractor.get_project_structure(repo_path)
        technology_detector = TechnologyDetector()
        project_context = technology_detector.get_project_context(
            readme_files, project_structure
        )

        return project_context

    def _summarize(
        self,
        commits_generator: Generator[List[Dict[str, Any]], None, None],
        project_context: List[str],
    ) -> List[Dict]:
        """
        Summarizes the given commit data into daily, weekly, and monthly summaries.
        Saves each summary stage using FileCache.

        Args:
            commits_generator (Generator): A generator yielding batches of commits.
            project_context (List[str]): Context of the project for better summarization.

        Returns:
            List[Dict]: A list of summarized data grouped by month.
        """
        daily_data = {
            "commits_generator": commits_generator,
            "project_context": project_context,
        }

        logging.info("Summarizing by day...")
        daily_summarizer = DailySummarizer()
        daily_summaries = FileCache.process_and_save(
            object_instance=daily_summarizer,
            process_function="summarize",
            process_args=(daily_data,),
            file_path=f"data/daily-summaries-{self.hash}.json",
        )

        logging.info("Summarizing by week...")
        weekly_summarizer = WeeklySummarizer()
        weekly_summaries = FileCache.process_and_save(
            object_instance=weekly_summarizer,
            process_function="summarize",
            process_args=(daily_summaries,),
            file_path=f"data/weekly-summaries-{self.hash}.json",
        )

        logging.info("Summarizing by month...")
        monthly_summarizer = MonthlySummarizer()
        monthly_summaries = FileCache.process_and_save(
            object_instance=monthly_summarizer,
            process_function="summarize",
            process_args=(weekly_summaries,),
            file_path=f"data/monthly-summaries-{self.hash}.json",
        )

        return monthly_summaries

    def _llm_processing(
        self, monthly_summaries: List[Dict[str, Any]], project_context: List[str]
    ) -> Dict[str, Any]:
        """
        Processes the monthly summaries through a Large Language Model (LLM).
        Builds a prompt and calls the LLM to generate a structured CV.

        Args:
            monthly_summaries (list): A list of summarized commit data grouped by month.

        Returns:
            dict: A dictionary containing the structured CV data.

        Raises:
            Exception: If the LLM response is not valid JSON.
        """
        logging.info("Building the prompt...")
        target_language = self.configuration_manager.get_target_language()
        grammatical_person = self.configuration_manager.get_grammatical_person()
        prompt_builder = PromptBuilder()
        prompt = prompt_builder.build_prompt(
            monthly_summaries, target_language, project_context, grammatical_person
        )

        logging.info("Calling the LLM...")
        llm_provider = self.configuration_manager.get_llm_provider()
        model_provider = ModelProvider()
        model = model_provider.get(llm_provider)
        llm_response = model.generate(prompt=prompt)
        cleaned_response = llm_response.strip("```json").strip("```").strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError as err:
            raise Exception(
                f"❌ Error: the model's response is not valid JSON: {err}\n\n{cleaned_response}"
            )

    def _export(self, cv_data: Dict[str, Any]) -> None:
        """
        Exports the generated CV to the desired format using the appropriate exporter.

        Args:
            cv_data (dict): The structured CV data to be exported.

        Returns:
            None
        """
        logging.info("Exporting CV...")
        author_name = self.configuration_manager.get_author_name()
        export_format = self.configuration_manager.get_export_format()
        exporter_provider = ExporterProvider()
        exporter = exporter_provider.get(export_format)
        export_path = exporter.export(
            author_name=author_name,
            extract=cv_data["extract"],
            data=cv_data["cv"],
            filename=f"resume-{self.hash}",
        )
        logging.info(f"✅ CV successfully generated at {export_path}")


if __name__ == "__main__":
    """
    Entry point of the script. Creates an instance of CVGenerator and runs the workflow.
    """
    cv_generator = CVGenerator()
    cv_generator.run()
