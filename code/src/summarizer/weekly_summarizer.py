import math
from collections import defaultdict
from datetime import datetime, timedelta
from typing import DefaultDict, Dict, List

from src.summarizer.summarizer_interface import SummarizerInterface


class WeeklySummarizer(SummarizerInterface):
    """
    A class for processing and summarizing commit data by week, identifying technologies,
    and generating weekly summaries using a language model (LLM).
    """

    PROMPT = """
    The following is a collection of commit messages corresponding to a specific week.
    Your task is to summarize the information in clear, concise language, highlighting the main functional achievements
    and technical improvements, excluding intricate details about individual files.
    Do not exceed 450 characters.
    [MESSAGES]
    Provide your response in plain text.
    Start your summary directly without any headers such as 'During this week' or 'The developer...'.
    """

    def summarize(self, data: List[Dict]) -> List[Dict]:
        """
        Groups commit data by week (starting on Monday) and creates weekly summaries.

        Args:
           data (List[Dict[str, Any]]): A list of dictionaries representing commits, with the following fields:
               - "date" (str): The commit date in ISO format (YYYY-MM-DD).
               - "commit_count" (int): The number of commits on that date.
               - "descriptions" (str): Commit messages or summaries associated with the date.
               - "technologies" (Optional[List[str]]): A list of detected technologies, if available.

        Returns:
           List[Dict[str, Any]]: A list of weekly commit summaries, where each dictionary includes:
               - "start_date" (str): The start date of the week in ISO format.
               - "end_date" (str): The end date of the week in ISO format.
               - "commit_count" (int): The total number of commits for the week.
               - "technologies" (List[str]): A unique list of detected technologies for the week.
               - "descriptions" (str): A summary of the weekly commit messages.
        """
        # 1. Group commits by week (starting on Monday)
        summaries = defaultdict(list)
        for commit in data:
            commit_date = datetime.fromisoformat(commit["date"]).date()
            week_start = commit_date - timedelta(days=commit_date.weekday())
            summaries[week_start].append(commit)

        # 2. Process each week to generate summaries
        results = []
        for week_start, group in summaries.items():
            technologies = self._consolidate_technologies(group)
            week_end = week_start + timedelta(days=6)
            weekly_summary = self._unify_and_summarize(
                commits=group, prompt=self.PROMPT
            )
            total_commits = sum(item["commit_count"] for item in group)

            results.append(
                {
                    "start_date": week_start.isoformat(),
                    "end_date": week_end.isoformat(),
                    "commit_count": total_commits,
                    "technologies": technologies,
                    "descriptions": weekly_summary,
                }
            )

        return results

    def _consolidate_technologies(self, group: List[Dict]) -> Dict[str, float]:
        """
        Consolidates and calculates the overall weights of technologies from the weekly summaries.

        Args:
            group (list[dict]): A list of weekly summaries, each containing a "technologies" field.

        Returns:
            dict[str, float]: A dictionary where keys are technology names and values are their accumulated weights.
        """
        # Collect technology weights
        tech_weights: DefaultDict[str, float] = defaultdict(float)
        for entry in group:
            for tech, weight in entry["technologies"].items():
                tech_weights[tech] += weight

        # Compute the total weight
        total_weight = sum(tech_weights.values())

        # Compute initial percentages
        percentages = {
            tech: (weight / total_weight) * 100 for tech, weight in tech_weights.items()
        }

        # Round percentages to 2 decimals
        rounded_percentages = {tech: round(p, 2) for tech, p in percentages.items()}

        # Adjust so that the summation is exactly 100
        current_sum = sum(rounded_percentages.values())
        if current_sum != 100:
            # Calculate the difference
            diff = 100 - current_sum
            # Find the technology with the greatest decimal to adjust
            decimal_diffs = {
                tech: percentages[tech] - math.floor(percentages[tech] * 100) / 100
                for tech in percentages
            }
            sorted_techs = sorted(
                decimal_diffs, key=lambda x: decimal_diffs[x], reverse=True
            )
            # Adjust the first technology in the list
            rounded_percentages[sorted_techs[0]] += diff

        result = dict(sorted(rounded_percentages.items()))

        return result
