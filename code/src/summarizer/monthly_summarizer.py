import math
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import DefaultDict, Dict, List

from src.summarizer.summarizer_interface import SummarizerInterface


class MonthlySummarizer(SummarizerInterface):
    """
    A class for processing and summarizing commit data by month, identifying technologies,
    and generating monthly summaries using a language model (LLM).
    """

    PROMPT = """
    The following is a collection of commit messages corresponding to a specific month.
    Your task is to summarize the information in clear, concise language, highlighting the key technical and functional milestones.
    Avoid excessive detail or mentions related to individual files.
    Do not exceed 450 characters.
    [MESSAGES]
    Provide your response in plain text.
    Start your summary directly without any headers such as 'During this month' or 'The developer...'.
    """

    def summarize(self, data: List[Dict]) -> List[Dict]:
        """
        Groups commit data by month (based on the "start_date") and creates monthly summaries.

        Args:
            data (List[Dict[str, Any]]): A list of dictionaries containing weekly commit data with the following keys:
                - "start_date" (str): The start date of the week in ISO format.
                - "end_date" (str): The end date of the week in ISO format.
                - "commit_count" (int): The total number of commits for the week.
                - "descriptions" (str): A unified weekly summary description.
                - "technologies" (Optional[List[str]]): A list of detected technologies.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries with monthly commit summaries. Each dictionary contains:
                - "month" (str): The corresponding month in the "YYYY-MM" format.
                - "start_date" (str): The first day of the month in ISO format.
                - "end_date" (str): The last day of the month in ISO format.
                - "commit_count" (int): The total number of commits for the month.
                - "technologies" (List[str]): A list of unique detected technologies.
                - "descriptions" (str): The summarized description for the month.
        """
        # 1. Group by month (based on start_date).
        summaries = defaultdict(list)
        for item in data:
            start_dt = datetime.fromisoformat(item["start_date"]).date()
            # Month key is the first day of the month.
            month_key = start_dt.replace(day=1)
            summaries[month_key].append(item)

        # 2. Process each month to generate summaries.
        results = []
        for month_start, group in summaries.items():
            technologies = self._consolidate_technologies(group)
            month_end = self._last_day_of_month(month_start)

            total_commits = sum(g["commit_count"] for g in group)
            monthly_summary_text = self._unify_and_summarize(
                commits=group, prompt=self.PROMPT
            )

            results.append(
                {
                    "month": month_start.strftime("%Y-%m"),
                    "start_date": month_start.isoformat(),
                    "end_date": month_end.isoformat(),
                    "commit_count": total_commits,
                    "descriptions": monthly_summary_text,
                    "technologies": technologies,
                }
            )

        return results

    def _last_day_of_month(self, d: date) -> date:
        """
        Returns the last day of the month for a given date.

        Args:
            d (date): A Python `date` object representing the input date.

        Returns:
            date: A `date` object representing the last day of the month.
        """
        next_month = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
        return next_month - timedelta(days=1)

    def _consolidate_technologies(self, group: List[Dict]):
        """
        Consolidates and calculates the weighted percentage distribution of technologies in a given group.

        This method aggregates the technology weights from multiple weekly records, computes their
        percentages relative to the total weight, and adjusts the percentages to ensure the sum is
        exactly 100%. It also rounds the percentages to two decimal places for precision.

        Args:
            group (list): A list of dictionaries where each dictionary represents a weekly record.
                Each record is expected to contain a "technologies" key, with a dictionary value
                mapping technology names (str) to their weights (float).

        Returns:
            dict: A sorted dictionary where keys are technology names (str) and values are their
                respective percentages (float), rounded to two decimal places.
        """
        # Collect technology weights
        technology_totals: DefaultDict[str, float] = defaultdict(float)
        for week in group:
            weekly_technologies = week["technologies"]
            for tech, weight in weekly_technologies.items():
                technology_totals[tech] += weight

        # Compute the total weight
        total_monthly_weight = sum(technology_totals.values())

        # Handle case where total weight is 0
        if total_monthly_weight == 0:
            return {}

        # Compute initial percentages
        percentages = {
            tech: (weight / total_monthly_weight) * 100
            for tech, weight in technology_totals.items()
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

        # Return sorted dictionary
        result = dict(sorted(rounded_percentages.items()))
        return result
