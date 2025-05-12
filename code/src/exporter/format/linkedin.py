import os
from typing import Any, Dict, List

from src.exporter.format.format_interface import FormatInterface


class Linkedin(FormatInterface):
    """
    Concrete implementation of the `FormatInterface` for exporting LinkedIn profile text.
    This class writes the provided LinkedIn text to a file in the specified output directory.
    """

    EXTENSION = "txt"

    def export(
        self, author_name: str, extract: str, data, filename: str = "linkedin_resume"
    ) -> str:
        """
        Exports the given LinkedIn profile data to a file in the output directory.

        Args:
            author_name (str): The author's name.
            extract (str): The CV extract.
            data (str | list[dict]): The data extracted from a LinkedIn profile, either as a string or a
                                              list of dictionaries representing structured data.
            filename (str): The name of the file where the content will be saved.
                            Defaults to "linkedin_resume".

        Returns:
            str: The full path of the file where the content was saved.
        """
        # Decide the format: process if a list, otherwise use it as raw text
        if isinstance(data, list):
            linkedin_text = self._generate_text(author_name, extract, data)
        else:
            linkedin_text = data

        # Write the content to the file
        filename = f"{filename}.{self.EXTENSION}"
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(linkedin_text)
        return path

    def _generate_text(
        self, author_name: str, extract: str, data: List[Dict[str, Any]]
    ) -> str:
        """
        Converts the given LinkedIn data into a formatted text string.

        Args:
            author_name (str): The name of the CV owner (if provided).
            extract (str): A brief summary of the CV details (if provided).
            data (list[dict]): A list of dictionaries.

        Returns:
            str: A formatted string representing the provided LinkedIn data.
        """
        lines = []
        lines.append(f"{self._author}: {author_name}")
        lines.append("")
        lines.append(f"{self._extract}: {extract}")
        lines.append("")
        for item in data:
            name = item.get("name", self._not_apply)
            position = item.get("position", self._not_apply)
            highlights = item.get("highlights", [])
            title = item.get("title", self._not_apply)
            company = item.get("company", self._not_apply)
            date_start = item.get("date_start", "")
            if date_start:
                date_start = self._format_date(date_start)
            date_end = item.get("date_end", "")
            if date_end:
                date_end = self._format_date(date_end)
            description = item.get("description", self._not_apply)
            technologies = item.get("technologies", [])
            technologies = ", ".join(
                [f"{tech} ({weight:.2f}%)" for tech, weight in technologies.items()]
            )
            domain = item.get("domain", self._not_apply)

            lines.append(f"{self._job_title}: {title}")
            lines.append(f"{self._name}: {name}")
            lines.append(f"{self._position}: {position}")
            lines.append(f"{self._company}: {company}")
            if date_start and date_end:
                lines.append(f"{self._time_period}: {date_start} - {date_end}")
            lines.append(f"{self._description}: {description}")
            lines.append(f"{self._technologies}: {technologies}")
            lines.append(f"{self._domain}: {domain}")
            lines.append(f"{self._highlights}:")
            for highlight in highlights:
                lines.append(f"  - {highlight}")
            lines.append("")

        return "\n".join(lines)
