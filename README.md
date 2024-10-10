# job-cli

A command-line interface tool for managing job candidates, scheduling interviews, and leveraging AI for candidate analysis.

## Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Google Gemini](https://img.shields.io/badge/GEMINI-07405E?style=for-the-badge&logo=google&logoColor=white)
![CLI](https://img.shields.io/badge/CLI-4D4D4D?style=for-the-badge&logo=windows-terminal&logoColor=white)
![CSV](https://img.shields.io/badge/CSV-217346?style=for-the-badge&logo=microsoft-excel&logoColor=white)
![PDF](https://img.shields.io/badge/PDF-B1040E?style=for-the-badge&logo=adobe-acrobat-reader&logoColor=white)

## Features

- Add candidates with name, age, and resume (PDF)
- Process candidates using AI analysis
- Extract text from PDF resumes
- Generate dummy candidate data for testing
- Manage application settings
- Store candidate information in a CSV database

## Usage

1. To add a candidate:

```bash
python index.py add --name "John Doe" --age 30 --resume "path/to/resume.pdf"
```

2. To process the next candidate:

```bash
python index.py process
```

3. To view current settings:

```bash
python index.py show_settings
```

4. To generate dummy candidate data:

```bash
python index.py fill_dummy
```

or specify the number of dummy candidates:

```bash
python index.py fill_dummy --num 20
```

## AI-Powered Analysis with Resume Reading

The tool uses Google's Gemini AI to analyze candidate information, including the content of their PDF resumes:

1. When a candidate is added, their PDF resume is processed and the text is extracted.
2. During the `process` action, the AI analyzes the candidate's information, including the extracted resume text.
3. The AI provides:
   - A summary of the candidate's key qualities (5 bullet points)
   - A hireability score on a scale of 1-10
   - Three other potential roles the candidate might be suitable for

This integration allows for a more comprehensive analysis of each candidate based on their actual resume content.

## Data Storage

Candidate information is stored in a `candidates.csv` file, which includes:
- Name
- Age
- Path to the resume PDF
- Hireability score (after processing)
- Other potential roles (after processing)

The actual resume text is extracted when needed but not stored in the CSV to keep the file size manageable.

## Configuration

The tool uses a `settings.json` file and environment variables for configuration. Ensure you have set up your Gemini API key in the settings or as an environment variable.

## Getting Started

1. Clone the repository
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Gemini API key in `settings.json` or as an environment variable
4. Prepare some PDF resumes for testing (or use the `fill_dummy` command to generate sample data)
5. Run the tool using the commands described in the Usage section

## Note

Make sure you have the necessary permissions to read the PDF files you're using with this tool. The resume extraction feature supports text-based PDFs; scanned documents may not work correctly.