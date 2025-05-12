import logging
import os
import tempfile
from datetime import datetime
from typing import Dict, Generator, List, Optional

from git import Repo


class CommitExtractor:
    """
    A utility class to extract commit information from a Git repository for a specific author.
    """

    def extract_commits_by_author(
        self,
        repo_path: str,
        author_email: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page_size: int = 100,
        repo_branches: Optional[List[str]] = None,
        ignore_commit_keywords: Optional[List[str]] = None,
    ) -> Generator[List[Dict], None, None]:
        """
        Extracts all commits from a Git repository for a specified author in a paginated manner.

        This method employs a generator to yield commits in batches (pages).

        Args:
           repo_path (str): The file path to the Git repository.
           author_email (List[str]): A list of email addresses to filter commits by author.
           start_date (Optional[datetime]): The start date for filtering commits.
           end_date (Optional[datetime]): The end date for filtering commits.
           page_size (int): The number of commits to include in each batch (page).
           repo_branches (Optional[List[str]]): A list of branch names to filter the commits.

        Yields:
           List[Dict[str, Any]]: A batch (page) of dictionaries containing commit details. Each dictionary includes:
               - "hash" (str): The commit SHA hash.
               - "author" (str): The name of the author.
               - "email" (str): The email address of the author.
               - "date" (str): The date of the commit in ISO 8601 format.
               - "message" (str): The commit message.
               - "files" (List[str]): A list of modified files.
        """
        # Clone repo if needed and get Repo instance
        repo_path = self._get_or_clone_repo(repo_path)
        repo = Repo(repo_path)

        # Validate repository state
        if repo.bare or not repo.heads:
            raise ValueError(
                f"❌ The repository at '{repo_path}' has no commits or is invalid."
            )

        # Validates the repository
        if repo.bare or not repo.heads:
            raise ValueError(f"❌ The repository at '{repo_path}' has no commits.")

        # Define branches to iterate over (all if no filter is specified)
        branches_to_iterate = repo_branches or [branch.name for branch in repo.branches]
        if not branches_to_iterate:
            raise ValueError(f"❌ No branches found in the repository '{repo_path}'.")

        # Iterate over all commits and filter by author
        batch = []
        for branch in branches_to_iterate:
            logging.info(f"Extracting commits for branch: {branch}")

            # Check if branch exists in the repository
            if branch not in [b.name for b in repo.branches]:
                logging.warning(
                    f"⚠️ Branch '{branch}' not found in the repository. Skipping..."
                )
                continue

            # Iterate commits in the current branch
            for commit in repo.iter_commits(branch, reverse=True):
                # Skip merge commits
                if len(commit.parents) > 1:
                    continue

                # Filter by date range
                commit_date = datetime.fromtimestamp(commit.committed_date)
                # Ignoring the hour
                commit_date = datetime.fromtimestamp(commit.committed_date).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                if start_date and commit_date < start_date:
                    continue
                if end_date and commit_date > end_date:
                    continue

                # Filter by author email
                if commit.author.email not in author_email:
                    continue

                commit_message = commit.message.strip()
                if not self._is_relevant_commit(commit_message, ignore_commit_keywords):
                    continue

                # Build commit information
                commit_data = {
                    "hash": commit.hexsha,
                    "author": commit.author.name,
                    "email": commit.author.email,
                    "date": commit_date.isoformat(),
                    "message": commit_message,
                    "files": list(commit.stats.files.keys()),
                }
                batch.append(commit_data)

                # Yield batch if full
                if len(batch) >= page_size:
                    yield batch
                    batch = []

        # Yield remaining commits (if any)
        if batch:
            yield batch

    def get_last_commit_date(self, repo_path: str) -> datetime:
        """
        Retrieves the date of the most recent commit in the Git repository.

        Args:
           repo_path (str): The file path to the Git repository.

        Returns:
           datetime: A `datetime` object representing the date of the most recent commit.

        Raises:
           ValueError: If the repository is empty or not accessible.
        """
        repo_path = self._get_or_clone_repo(repo_path)
        repo = Repo(repo_path)

        # Ensure the repository has at least one commit
        if repo.bare or not repo.heads:
            raise ValueError(f"❌ The repository at '{repo_path}' has no commits.")

        # Get the most recent commit (head of the default branch)
        most_recent_commit = next(repo.iter_commits(repo.head, max_count=1))

        # Convert the commit date to a datetime object
        return datetime.fromtimestamp(most_recent_commit.committed_date)

    def get_project_structure(self, repo_path: str) -> str:
        """
        Generates a textual representation of the project's structure at the first level.

        Args:
           repo_path (str): The file path to the Git repository.

        Returns:
           str: A string representation of the project's structure, showing only first-level files and directories.

        Raises:
           Exception: If the repository cannot be accessed or the provided path is invalid.
        """
        try:
            # Initialize the Git repository
            repo_path = self._get_or_clone_repo(repo_path)
            repo = Repo(repo_path)

            # Ensure the repository is valid
            if repo.bare:
                raise ValueError(
                    f"❌ The repository at {repo_path} is bare or invalid."
                )

            # Get the root tree (latest commit)
            root_tree = repo.tree()

            # Collect names of files and directories in the root
            items = []
            for item in root_tree:
                if item.type == "blob":  # File
                    items.append(f"[FILE] {item.name}")
                elif item.type == "tree":  # Directory
                    items.append(f"[DIR] {item.name}")

            # Generate the textual representation of the structure
            structure = "\n".join(items)
            return f"🌳 Project Structure (First Level):\n{structure}"

        except Exception as e:
            raise ValueError(f"❌ Failed to generate project structure: {e}")

    def get_root_readme_files(self, repo_path: str) -> Dict[str, str]:
        """
        Identifies README files with known extensions in the root directory of a Git repository
        and retrieves their contents.

        Args:
           repo_path (str): The file path to the local Git repository.

        Returns:
           Dict[str, str]: A dictionary where keys are file paths (relative to the repository root)
           and values are the contents of the respective files.
        """
        # Define known README extensions
        readme_extensions = {".md", ".txt", ".rst", ".markdown", ""}
        readme_contents = {}

        # Initialize the Git repository
        repo_path = self._get_or_clone_repo(repo_path)
        repo = Repo(repo_path)

        # Traverse all files in the working tree or latest commit
        for blob in repo.tree().traverse():
            if blob.type == "blob":
                file_path = blob.path
                file_name = blob.name
                file_extension = os.path.splitext(file_name)[1].lower()

                # Check if the file is a README with a known extension (or empty extension)
                if (
                    (
                        file_name.upper().startswith(
                            "README"
                        )  # Name starts with README
                        or file_name.upper().startswith(
                            "CHANGELOG"
                        )  # Name starts with CHANGELOG
                    )
                    and file_extension
                    in readme_extensions  # Extension matches known types
                    and "/" not in file_path  # Exclude files in subdirectories
                ):
                    # Read the content of the file
                    content = blob.data_stream.read().decode("utf-8")
                    readme_contents[file_path] = content

        return readme_contents

    def _is_url(self, path: str) -> bool:
        """
        Determines whether a given path is a URL or a remote resource.

        This method checks if the provided path starts with typical URL or remote
        resource prefixes such as "http://", "https://", or "git@".

        Args:
            path (str): The path string to be evaluated.

        Returns:
            bool: True if the path is a URL or remote resource, False otherwise.
        """
        return path.startswith(("http://", "https://", "git@"))

    def _get_or_clone_repo(self, repo_path: str) -> str:
        """
        Determines whether the provided `repo_path` is a local directory or a Git URL.
        If it is a URL, the repository is cloned to a temporary directory.

        Args:
           repo_path (str): The local file path or the Git repository URL.

        Returns:
           str: The path to the local repository (original or cloned).
        """
        if self._is_url(repo_path):
            temp_dir = tempfile.mkdtemp()
            Repo.clone_from(repo_path, temp_dir)
            return temp_dir
        elif os.path.isdir(repo_path):
            return repo_path
        else:
            raise ValueError(f"Invalid repository path: {repo_path}")

    def _is_relevant_commit(
        self, commit_message: str, irrelevant_keywords: Optional[List[str]]
    ) -> bool:
        """
        Evaluates the relevance of a commit based on its message length and the presence of specific keywords.

        Args:
           commit_message (str): The message of the commit.

        Returns:
           bool: `True` if the commit is considered relevant, otherwise `False`.
        """
        if irrelevant_keywords:
            message_lower = commit_message.lower()
            if any(keyword in message_lower for keyword in irrelevant_keywords):
                return False

        if len(commit_message.strip()) < 10:
            return False

        return True
