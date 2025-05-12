from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from src.detector.technology_detector import TechnologyDetector
from src.summarizer.summarizer_interface import SummarizerInterface


class DailySummarizer(SummarizerInterface):
    """
    A class for processing and summarizing commit data, identifying technologies,
    and generating summaries using a language model (LLM).
    """

    PROMPT = """
    The following is a collection of commit messages from a single day of work.
    Your task is to summarize the information in clear, concise language, highlighting the main tasks, changes, or accomplishments:
    [MESSAGES]
    Provide your response in plain text.
    """

    def summarize(self, data: Dict) -> List[Dict]:
        """
        Groups commit data by day and creates daily summaries.

        Args:
           data (Dict): A dictionary with the commits generator and the project context.

        Returns:
           List[Dict[str, Any]]: A list of dictionaries containing daily commit summaries, where each dictionary includes:
               - "date" (str): The date in ISO format (YYYY-MM-DD).
               - "commit_count" (int): The total number of commits for that day.
               - "technologies" (List[str]): A list of technologies inferred from the modified files.
               - "descriptions" (str): A summary of the daily commit messages.
        """
        technology_detector = TechnologyDetector()
        summaries = defaultdict(list)
        commits_generator = data["commits_generator"]
        project_context = data["project_context"]

        for batch in commits_generator:
            for commit in batch:
                commit_date = datetime.fromisoformat(commit["date"]).date()
                summaries[commit_date].append(commit)

        commits_by_day = []
        for commit_date, group in summaries.items():
            files = [file for group_item in group for file in group_item["files"]]
            technologies = technology_detector.detect(files, project_context)
            daily_summary = self._unify_and_summarize(commits=group, prompt=self.PROMPT)

            commits_by_day.append(
                {
                    "date": commit_date.isoformat(),
                    "commit_count": len(group),
                    "technologies": technologies,
                    "descriptions": daily_summary,
                }
            )

        return commits_by_day

    def _combine_descriptions(self, commits: List[Dict]) -> str:
        """
        Combines commit descriptions into a single formatted string.

        Args:
            commits (list[dict]): List of commits containing "message" fields.

        Returns:
            str: Combined commit descriptions, wrapped in triple backticks for formatting.
        """
        combined_descriptions = ". ".join(
            summary["message"].strip() for summary in commits
        )
        combined_descriptions = f"```{combined_descriptions}```"

        return combined_descriptions
