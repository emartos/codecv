import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from src.config.configuration_manager import ConfigurationManager
from src.llm.model_provider import ModelProvider


class SummarizerInterface(ABC):
    """
    An abstract interface defining the contract for a summarizer
    that processes a list of commit data and generates summarized results.

    Classes inheriting from this interface must implement the `summarize` method.
    """

    def __init__(self):
        configuration_manager = ConfigurationManager()
        llm_provider = configuration_manager.get_llm_provider()
        model_provider = ModelProvider()
        self.model = model_provider.get(llm_provider)

    @abstractmethod
    def summarize(self, data: List[Dict]) -> List[Dict]:
        """
        Processes and summarizes a list of commit dictionaries.

        Args:
            data (List[Dict]): The data to process, that relies on the implementation.

        Returns:
            List[Dict]: A list of summarized commit data. The exact structure of the
                        output depends on the implementation.
        """
        pass

    def _combine_descriptions(self, commits) -> str:
        """
        Combines the descriptions of a list of commits into a single formatted string.

        This method extracts the "descriptions" field from each commit in the provided list,
        joins all descriptions into a single string separated by periods, and removes any
        extra newline characters. The resulting string is then wrapped in a code block
        using triple backticks.

        Args:
            commits (list): A list of dictionaries where each dictionary represents a commit.
                Each dictionary is expected to contain a "descriptions" key with the commit description.

        Returns:
            str: A formatted string containing all combined commit descriptions.
        """
        descriptions = [commit.get("descriptions", "") for commit in commits]
        combined_descriptions = ". ".join(descriptions)
        combined_descriptions = re.sub(r"\n+", ". ", combined_descriptions)
        combined_descriptions = f"```{combined_descriptions}```"

        return combined_descriptions

    def _unify_and_summarize(
        self,
        commits: List[Dict],
        prompt: str,
        max_token_threshold: Optional[int] = None,
    ) -> str:
        """
        Merges commit descriptions into a single text block and generates a summarized version.

        Args:
           commits (List[Dict]): A list of dictionaries containing commit details.
           prompt (str): The specific prompt used for querying the LLM.
           max_token_threshold (Optional[int]): The maximum number of tokens allowed in the summary.
                                                Defaults to None (no threshold).

        Returns:
           str: A summarized string containing the commit information.
        """
        # 1. Combine all descriptions into a unified text
        combined_descriptions = self._combine_descriptions(commits)

        # 2. Check the token count for the prompt
        token_estimate = self.model.estimate_tokens(combined_descriptions)
        if max_token_threshold is not None and token_estimate > max_token_threshold:
            raise ValueError(
                f"The unified text ({token_estimate} tokens) exceeds the token threshold of {max_token_threshold}. "
                "Consider splitting the input and summarizing in chunks."
            )

        # 3. Construct the LLM prompt
        prompt = prompt.replace("[MESSAGES]", combined_descriptions)

        # 4. Query the LLM for a summary
        summary = self.model.generate(
            prompt=prompt, temperature=0.7, max_tokens=300
        ).strip()

        return summary.strip()
