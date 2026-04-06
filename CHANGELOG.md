## [1.0.0] - 2025-05-08

### Added
- In `.env.template`:
  - Created a new configuration template with sections for Application Settings, Parameters, OpenAI Settings, xAI Settings, and Redis Settings to streamline environment variable setup.
- In `.flake8`:
  - Added Flake8 configuration with a maximum line length of 210 to enforce consistent code style.
- In `.gitignore`:
  - Added comprehensive ignore patterns for Node, Java, Python, Maven, JetBrains IDE, macOS, Windows, and other common artifacts to prevent unnecessary files from being tracked.
- In `.pre-commit-config.yaml`:
  - Added pre-commit hooks for checking case conflicts, docstrings, symlinks, VCS permalinks, trailing whitespace, and requirements.txt formatting, along with hooks for `isort`, `black`, `flake8`, and `mypy` to enforce code quality.
- In `Makefile`:
  - Added a comprehensive Makefile with targets for environment setup (`create-venv`, `install-requirements`, `delete-venv`), code analysis (`lint`, `pre-commit`), application execution (`run`, `app-version`), and cache management (`cache-list`, `cache-clear`), with color-coded output for better usability.
- In `README.md`:
  - Added detailed documentation covering project overview, features, installation, usage, Makefile commands, export formats, example workflow, limitations, support, contributing guidelines, license, and acknowledgments.
- In `code/`:
  - Added `app.py` as the main entry point for the CV generator application, orchestrating commit extraction, summarization, LLM processing, and CV export.
  - Added `requirements.txt` with dependencies for the project, including `GitPython`, `openai`, `redis`, and others.
  - Added `scripts/cache.py` for managing Redis cache operations (list and invalidate).
  - Added `src/cache/file_cache.py` for caching processed data to JSON files.
  - Added `src/config/configuration_manager.py` for handling configuration setup and validation as a Singleton.
  - Added `src/detector/technology_detector.py` for detecting technologies from project files and context.
  - Added `src/exporter/exporter_provider.py` and related exporter classes for generating CVs in multiple formats (Markdown, PDF, LinkedIn, JSON Resume, Europass).
  - Added `src/git_parser/commit_extractor.py` for extracting and filtering Git commits.
  - Added `src/llm/` with `cache_manager.py`, `model_provider.py`, `prompt_builder.py`, and provider implementations (`grok.py`, `openai.py`) for LLM integration with caching.
  - Added `src/logger/` with `formatter.py` and `logger.py` for colored logging output.
  - Added `src/summarizer/` with `daily_summarizer.py`, `weekly_summarizer.py`, `monthly_summarizer.py`, and `summarizer_interface.py` for summarizing commit data at different granularities.
  - Added `version.py` to define the project version (`1.0.0`).
- In `code/src/`:
  - Added `__init__.py` files in relevant directories to structure the Python package.

## [1.1.0] - 2025-05-14

### Added
- In `code/src/llm/provider/googlegenai.py`:
  - Added support for Google Gemini API integration, enabling text generation with the `gemini-1.5-flash` model by default, configurable via `GOOGLE_TEXT_MODEL` environment variable.
  - Implemented caching with `CacheManager` and retry logic for handling rate limit errors (`ResourceExhausted`) and specific handling for `NotFound` (404) errors.
  - Explicitly configured the Google AI Studio API key using `genai.configure()`.
- In `code/src/llm/provider/ollama.py`:
  - Added support for Ollama integration with Llama models, defaulting to `llama3.1`, configurable via `LLAMA_TEXT_MODEL` and `LLAMA_BASE_URL` environment variables.
  - Included caching with `CacheManager` and retry logic for handling `ResponseError` and `RequestException`.
- In `code/src/llm/provider/openai.py` and `code/src/llm/provider/grok.py`:
  - Updated default models to `gpt-4o` and `grok-2-latest` respectively for improved performance and stability.

## [1.1.1] - 2026-03-19

### Fixed
- In `code/src/llm/provider/googlegenai.py`:
  - Updated default model from `gemini-1.5-flash` to `gemini-2.5-flash` to fix 404 errors with v1beta API.
  - Improved retry strategy with proper exponential backoff (10s, 20s, 40s, 80s, 160s) for rate limit handling.
  - Reduced max retries from 15 to 5 with better delay intervals.
- In `code/src/llm/provider/openai.py`:
  - Updated default model from `gpt-5.4-nano` to `gpt-4o-mini` (valid model name).
  - Added retry logic for empty or None responses with exponential backoff.
  - Improved error handling to distinguish between empty content and other errors.
- In `code/src/summarizer/weekly_summarizer.py`:
  - Fixed IndexError when consolidating technologies with empty technology list.
  - Added validation to return empty dict when total_weight is 0.
  - Added safety check before accessing `sorted_techs[0]` to prevent index out of range errors.
- In `code/app.py`:
  - Added validation for empty LLM responses before JSON parsing.
  - Enhanced error logging with response previews for debugging JSON decode errors.
  - Added debug logging for raw LLM responses.

## [1.1.2] - 2026-04-06

### Optimized
- In `code/src/summarizer/daily_summarizer.py`:
  - Implemented parallel processing using `ThreadPoolExecutor` (10 workers) for daily summaries and technology detection, significantly reducing execution time.
- In `code/src/summarizer/weekly_summarizer.py`:
  - Added parallelization with `ThreadPoolExecutor` (5 workers) for processing weekly summaries concurrently.
- In `code/src/summarizer/monthly_summarizer.py`:
  - Added parallelization with `ThreadPoolExecutor` (3 workers) for processing monthly summaries concurrently.
- General:
  - Ensured chronological order is preserved after parallel execution by sorting data keys before mapping tasks.