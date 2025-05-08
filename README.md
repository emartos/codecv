# CV Generator: Automated résumé creation tool

This project is an innovative **CV generator** leveraging **Large Language Models (LLM)** to analyze a Git repository and produce professional résumés in multiple formats, including **Markdown**, **PDF**, and **LinkedIn-ready content**. Its primary goal is to automate résumé creation by utilizing a developer's contributions and commit history to highlight their skills and achievements.

---

## 🚀 Features

1. **Git Commit Analysis**:
    - Extracts commit history and information from a Git repository.
    - Filters commits by the author's email to ensure precision.

2. **Data Summarization**:
    - Automatically generates daily, weekly, and monthly summaries of Git activity.
    - Identifies key contributions and projects to showcase in the CV.

3. **LLM-Powered CV Building**:
    - Uses an LLM to analyze summarized data and generate polished résumé content.
    - Seamlessly works with the best AI providers for precise résumé generation and analysis.

4. **Flexible Export Options**:
   - Supports a variety of popular formats:
      - **Markdown**: Lightweight and editable format, great for version control and plain text sharing.
      - **PDF**: Print-ready résumé for formal job applications.
      - **LinkedIn**: Professionally structured profiles for LinkedIn.
      - **Europass (XML)**: Ideal for EU job applications following the standard Europass CV format.
      - **JSON Resume**: Compliant with the JSON Resume schema for easy integration with automated systems.

5. **Multi-language Support**:
   - Generate résumés in **any known language**, thanks to the integration with advanced Large Language Models (LLMs). Adapt easily to diverse job markets and regional requirements.

6. **Highly Configurable**:
   - Customize the process easily using environment variables.

7. **Makefile for Simplified Workflow**:
    - Easy-to-use make commands for setting up the environment, running the app, and maintaining the codebase.

---

## 📦 Installation

### Step 1: Clone the repository
```bash
git clone https://github.com/yourusername/cv-generator.git
cd cv-generator
```

### Step 2: Create and activate the virtual environment
```bash
make create-venv
```

### Step 3: Install dependencies
```bash
make install-requirements
```

### Step 4: Prepare configuration
```bash
make env
```
This will create an `.env` file if it does not exist. Update the file with the necessary configuration.

---

## ▶️ Usage

To run the application, use:

```bash
make run
```

---

## 🛠️ Available Makefile commands

Here is a list of **Makefile** commands to streamline various tasks within the project:

### 📂 Environment setup
- **`make create-venv`**: Creates the virtual environment if it does not exist.
- **`make install-requirements`**: Installs all dependencies from `requirements.txt`.
- **`make freeze-requirements`**: Updates the `requirements.txt` file with the current environment.
- **`make env`**: Creates the `.env` file from a template, if it doesn't exist.
- **`make delete-venv`**: Deletes the virtual environment.

### 🛠 Code quality and pre-commit
- **`make lint`**: Runs `flake8` for linting the code.
- **`make pre-commit`**: Runs all pre-commit hooks on the codebase.
- **`make check-format`**: Validates the code format with `isort` and `black`.

### ▶️ Application execution
- **`make run`**: Runs the main application.

### 🧹 Cleanup and maintenance
- **`make clean`**: Removes temporary files (`__pycache__`, `.pyc`, etc.).
- **`make delete-venv`**: Deletes the virtual environment.

### ℹ️ Utilities
- **`make help`**: Displays all available commands along with a brief description.

> **Tip**: Use `make help` to quickly list all make commands.

---

## 🌐 Export formats

The application supports multiple résumé formats:
1. **Markdown**:
    - Lightweight and editable format.
    - Suitable for version control and plain text sharing.
2. **PDF**:
    - Print-ready résumé for formal applications.
3. **LinkedIn**:
    - Professionally structured content for LinkedIn profiles.
4. **Europass (XML)**:
   - Compatible with the standard Europass CV format.
   - Ideal for EU job applications.
5. **JSON Resume**:
   - Adheres to the JSON Resume schema.
   - Easy to integrate into other systems and applications.

---

## 📑 Example workflow

To generate a résumé, follow these steps:

1. **Initialize the environment**:
   ```bash
   make create-venv
   make install-requirements
   make env
   ```

2. **Run pre-commit for code validation**:
   ```bash
   make pre-commit
   ```

3. **Run the application**:
   ```bash
   make run
   ```

4. **Output**:
   - The résumé will be generated in the desired format (Markdown, PDF, or LinkedIn) and saved in the output directory.

---

## ⚙️ Running the application without or with `.env` Configuration

You can run the program both with and without initializing the `.env` configuration file. Here's how:

### Without using the `.env` file

If you choose not to set up a `.env` file, the program will ask you for required inputs during runtime. Follow these steps:

1. Ensure your project and virtual environment are set up:
   ```bash
   make create-venv
   make install-requirements
   ```

2. Run the application:
   ```bash
   make run
   ```
   - The application will interactively prompt you for the required inputs such as repository path, author name, email, etc.

3. Output:
   - The résumé will be generated in the desired format and saved in the `output/` directory.

### Using the `.env` file

The `.env` file allows you to predefine input configurations to run the program smoothly without prompts.

1. Generate the `.env` file template:
   ```bash
   make env
   ```

2. Open the `.env` file in a text editor and fill in the necessary values. Example:
   ```dotenv
   REPO_PATH=/path/to/your/repository
   AUTHOR_NAME=John Doe
   AUTHOR_EMAIL=john.doe@example.com
   EXPORT_FORMAT=pdf
   ```

3. Save and close the `.env` file.

4. Run the application:
   ```bash
   make run
   ```

5. Output:
   - The résumé will be automatically generated in the pre-configured format and saved in the `output/` directory.

---

## 🚧 Limitations

1. **Dependency on commit message quality**:  
   The system relies on the quality of commit messages to generate summaries and insights. Sending all code changes to
   the LLM would be an alternative, but this could exceed processing limits due to the large volume of data.

2. **Limited technology coverage**:  
   The detected technologies are exclusively based on the project's code. Technologies related to infrastructure
   (e.g., CI/CD, operating systems, etc.) are not included in the detection scope.

---

## 📧 Support

If you encounter any issues or have questions, feel free to open an issue in the repository or contact the project maintainer at `info@natiboo.es`.

---

## 🤝 Contributing

We welcome contributions to this project! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-branch-name`).
3. Ensure all `make pre-commit` hooks pass.
4. Submit a pull request.

---

## 📜 License

This project is licensed under the GNU Affero General Public License v3.0.
You may redistribute and/or modify it under the terms of the AGPL-3.0.

See the [LICENSE](./LICENSE) file for full license details.

Copyright (C) 2025 Eduardo Martos Gómez <emartos@natiboo.es>

---

## 🎉 Acknowledgements

- [OpenAI](https://openai.com/) and [Grok](https://grok.com/) for their LLM capabilities.
- The open-source community for their incredible tools and resources.
