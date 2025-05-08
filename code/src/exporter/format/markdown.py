import os

from src.exporter.format.format_interface import FormatInterface


class Markdown(FormatInterface):
    """
    Concrete implementation of the FormatInterface for exporting CV data into a Markdown file.
    This class takes a structured dictionary and generates a formatted Markdown document.
    """

    EXTENSION = "md"

    def export(
        self, author_name: str, extract: str, data, filename: str = "resume"
    ) -> str:
        """
        Exports the given CV data (`data`) to a Markdown file in the output directory.

        Args:
            author_name (str): The author's name.
            extract (str): The CV extract.
            data (list[dict]): A list of dictionaries where each dictionary represents a CV section.
            filename (str): The name of the Markdown file where the content will be saved.
                            Defaults to "resume".

        Returns:
            str: The full path of the generated Markdown file.
        """
        markdown_text = self._generate_text(author_name, extract, data)
        filename = f"{filename}.{self.EXTENSION}"
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        return path

    def _generate_text(self, author_name: str, extract: str, data):
        """
        Converts the given CV data into a Markdown-formatted string.

        Args:
            author_name (str): The author's name.
            extract (str): The CV extract.
            data (list[dict]): A list of dictionaries.

        Returns:
            str: A formatted Markdown string representing the provided CV data.
        """
        lines = []
        lines.append(f"# {author_name}")
        lines.append("")
        lines.append(extract)
        lines.append("")
        for item in data:
            name = item.get("name", self._not_apply)
            position = item.get("position", self._not_apply)
            highlights = item.get("highlights", [])
            title = item.get("title", self._not_apply)
            domain = item.get("domain", self._not_apply)
            date_start = item.get("date_start", "")
            if date_start:
                date_start = self._format_date(date_start)
            date_end = item.get("date_end", "")
            if date_end:
                date_end = self._format_date(date_end)
            description = item.get("description", "")
            technologies = item.get("technologies", [])
            technologies = ", ".join(
                [f"{tech} ({weight:.2f}%)" for tech, weight in technologies.items()]
            )

            lines.append(f"## {title} ({date_start} - {date_end})")
            lines.append(f"* **{self._name}**: {name}")
            lines.append(f"* **{self._position}**: {position}")
            lines.append(f"* **{self._domain}**: {domain}")
            lines.append(f"* **{self._technologies}**: {technologies}")
            lines.append(f"* **{self._description}**: {description}")
            lines.append(f"* **{self._highlights}**:")
            for highlight in highlights:
                lines.append(f"  - {highlight}")
            lines.append("")

        return "\n".join(lines)
