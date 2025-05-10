import json
import os

from src.exporter.format.format_interface import FormatInterface


class Jsonresume(FormatInterface):
    """
    Implementation of the FormatInterface for exporting CV data into JSON Resume Schema.
    See: https://jsonresume.org/
    """

    EXTENSION = "json"

    def export(
        self, author_name: str, extract: str, data, filename: str = "resume"
    ) -> str:
        """
        Exports the given CV data to a JSON Resume file in the output directory.

        Args:
            author_name (str): The author's name.
            extract (str): The CV extract.
            data (list[dict]): A list of dictionaries representing a CV's structured sections.
            filename (str): The name of the JSON file where the content will be saved.
                            Defaults to "resume".

        Returns:
            str: The full path of the generated JSON Resume file.
        """
        json_resume = self._generate_json(author_name, extract, data)
        filename = f"{filename}.{self.EXTENSION}"
        path = os.path.join(self.output_dir, filename)

        # Save to file
        with open(path, "w", encoding="utf-8") as file:
            json.dump(json_resume, file, indent=4)
        return path

    def _generate_json(self, author_name: str, extract: str, data):
        """
        Converts internal CV data into a JSON Resume Schema-compliant dictionary.

        Args:
            author_name (str): The author's name.
            extract (str): The CV extract (professional summary).
            data (list[dict]): Structured CV data.

        Returns:
            dict: A structured representation of the resume in JSON Resume format.
        """
        basics = {
            "name": author_name,
            "summary": extract,
        }

        work = [
            {
                "name": item.get("name"),
                "position": item.get("position"),
                "startDate": (
                    self._format_date(item.get("date_start", ""))
                    if item.get("date_start", "")
                    else ""
                ),
                "endDate": (
                    self._format_date(item.get("date_end", ""))
                    if item.get("date_end", "")
                    else ""
                ),
                "summary": item.get("description", ""),
                "highlights": item.get("highlights", []),
            }
            for item in data
        ]

        # Generate skills section by aggregating technologies across all jobs
        # Aggregated technologies
        all_techs = {}
        for item in data:
            technologies = item.get("technologies", {})
            for tech, weight in technologies.items():
                if tech not in all_techs:
                    all_techs[tech] = weight
                else:
                    all_techs[tech] += weight  # Summing up scores for repeated techs

        # Sort aggregated technologies by weight
        sorted_technologies = sorted(
            all_techs.items(), key=lambda x: x[1], reverse=True
        )

        # Create detailed skills section
        skills = [
            {
                "name": tech,
                "level": f"{weight:.2f}%",  # Represent weight as a percentage level
            }
            for tech, weight in sorted_technologies
        ]

        return {"basics": basics, "work": work, "skills": skills}
