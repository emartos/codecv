from typing import Any, Dict, List


class PromptBuilder:

    ASSISTANT_ROLE = (
        "You are an expert in software development with mastery of all technologies."
    )

    ASSISTANT_RESPONSE_INSTRUCTIONS = """
    You must only provide a JSON containing the CV elements.
    Your response must contain nothing but the JSON, with no delimiters (such as ```json), additional indications, or the word 'json'.
    """.strip()

    ASSISTANT_PROMPT = """
    Below, enclosed in ^^^, is a monthly chronological summary of the commits made by a developer.

    Your task is:
    - Summarize the technical achievements, tasks performed, and group information by functional areas or projects.
    - Use the technologies and their weights (field: "Technologies") provided in the input without recalculating or inferring additional ones.
    - Consolidate projects that span multiple months into a single block, ensuring that:
      - The "date_start" field corresponds to the first month of activity.
      - The "date_end" field corresponds to the last month of activity.
    - Generate a professional CV structure in JSON format strictly using the following format:
    {
      "extract": "Summarized overview or key points of the provided CV details, highlighting the most relevant skills, achievements, and experiences",
      "project_description": "Describes the project as a whole, using the information provided in the input and taking into account that the main technologies are [MAIN_TECHNOLOGIES]",
      "cv": [
          {
            "name": "Name of the project or account. This field must identify the employer, client, or specific project worked on.",
            "position": "Professional title or role. Clearly describe the candidate's position in the project (e.g. 'Backend Developer', 'Fullstack Engineer', etc.)",
            "title": "Brief name of the milestone or project",
            "description": "Detailed description of the project, milestone, or position",
            "domain": "Knowledge domain (e.g. E-Commerce, Web Development, CMS, DevOps, Cybersecurity, API, Data Integration, Data Analytics, AI, Testing, Performance...)",
            "technologies": {
                "Name of technology 1": 40,  # Relative weight or importance (in percentage)
                "Name of technology 2": 30,
                "Name of technology 3": 20
            },
            "date_start": "Start date in YYYY-MM format",
            "date_end": "End date in YYYY-MM format",
            "highlights": [
                "Specific accomplishment, task, or result achieved in this project",
                "Another highlight that demonstrates impact or success"
                ...
            ]
          },
          ...
      ]
    }

    IMPORTANT:
    - Ensure that your response content, including JSON strings, is written in "[TARGET_LANGUAGE]".
    - Ensure consistency in technology names (e.g., always use "PHP", not "Php").
    - Format dates strictly as "YYYY-MM".
    - Use the following grammatical person for the generated text: [GRAMMATICAL_PERSON].
      When the grammatical person is "first", write in active voice (e.g., "I developed a platform...") using "I"/"my" consistently to describe the work.
      When the grammatical person is "third", write in passive or impersonal voice (e.g., "They developed a platform..." or "A platform was developed...").
    - The "highlights" field should include a short list of the most relevant achievements, results, or contributions made during the project.
      These should be concise and impactful, focusing on measurable success where possible.
    - Ensure that all fields strictly adhere to the provided format and purpose.

    Note: If the input contains irrelevant or unclear information, process only the meaningful content related to the task.

    ^^^
    [BODY]
    ^^^
    """

    def build_prompt(
        self,
        monthly_summaries: List[Dict[str, Any]],
        target_language: str,
        project_context: List[str],
        grammatical_person: str,
    ) -> str:
        """
        Constructs a clear and structured prompt to send to a Large Language Model (LLM)
        using the provided monthly summaries of commits.

        Args:
            monthly_summaries (List[str]): A list containing monthly summaries of commits.

        Returns:
            str: The constructed prompt as a string.
        """
        body = "\n---\n"
        for summary in monthly_summaries:
            block = f"Month: {summary['month']}\n"
            block += f"Total commits: {summary['commit_count']}\n"
            block += f"Technologies: {summary['technologies']}\n"
            block += "Commit messages:\n"
            if isinstance(summary["descriptions"], list):
                for msg in summary["descriptions"]:
                    block += f"  - {msg.strip()}\n"
            else:
                block += summary["descriptions"]
            body += block + "\n"

        project_context_str = (", ").join(project_context)
        prompt = (
            self.ASSISTANT_PROMPT.replace("[TARGET_LANGUAGE]", target_language)
            .replace("[MAIN_TECHNOLOGIES]", project_context_str)
            .replace("[GRAMMATICAL_PERSON]", grammatical_person)
            .replace("[BODY]", body)
        )

        return self.ASSISTANT_ROLE + prompt + self.ASSISTANT_RESPONSE_INSTRUCTIONS
