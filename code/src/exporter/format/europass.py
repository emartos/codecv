import os
import xml.etree.ElementTree as ET

from src.exporter.format.format_interface import FormatInterface


class Europass(FormatInterface):
    """
    Implementation of the FormatInterface for exporting CV data into Europass format (XML).
    See: https://europa.eu/europass/en
    """

    EXTENSION = "xml"

    def export(
        self, author_name: str, extract: str, data, filename: str = "resume"
    ) -> str:
        """
        Exports the given CV data to a Europass XML file in the output directory.

        Args:
            author_name (str): The author's name.
            extract (str): The CV extract.
            data (list[dict]): A list of dictionaries representing a CV's structured sections.
            filename (str): The name of the XML file where the content will be saved.
                            Defaults to "resume".

        Returns:
            str: The full path of the generated Europass XML file.
        """
        europass_xml = self._generate_xml(author_name, extract, data)
        filename = f"{filename}.{self.EXTENSION}"
        path = os.path.join(self.output_dir, filename)

        # Save XML to file
        tree = ET.ElementTree(europass_xml)
        tree.write(path, encoding="unicode", xml_declaration=True)
        return path

    def _generate_xml(self, author_name: str, extract: str, data):
        """
        Converts internal CV data into a Europass XML-compliant structure.

        Args:
            author_name (str): The author's name.
            extract (str): The CV extract (professional summary).
            data (list[dict]): Structured CV data.

        Returns:
            xml.etree.ElementTree.Element: Root XML element for the Europass structure.
        """
        root = ET.Element("Europass")
        personal_info = ET.SubElement(root, "PersonalInformation")
        ET.SubElement(personal_info, "Name").text = author_name
        ET.SubElement(personal_info, "Summary").text = extract

        experiences = ET.SubElement(root, "WorkExperience")
        for item in data:
            date_start = item.get("date_start", "")
            if date_start:
                date_start = self._format_date(date_start)
            date_end = item.get("date_end", "")
            if date_end:
                date_end = self._format_date(date_end)
            description = item.get("title", "") + ". " + item.get("description", "")

            job = ET.SubElement(experiences, "Job")
            ET.SubElement(job, "Position").text = item.get("position", "")
            ET.SubElement(job, "Domain").text = item.get("domain", "")
            ET.SubElement(job, "StartDate").text = date_start
            ET.SubElement(job, "EndDate").text = date_end
            ET.SubElement(job, "Description").text = description
            # Sort technologies by weight in descending order
            tech_list = sorted(
                item.get("technologies", {}).items(),
                key=lambda x: x[1],  # Sort by the weight (second element in tuple)
                reverse=True,  # Descending order
            )
            # Generate a formatted string
            technologies = ", ".join(
                [f"{tech} ({weight:.2f}%)" for tech, weight in tech_list]
            )
            ET.SubElement(job, "Technologies").text = technologies

        return root
