# job-cli

A command-line interface tool for managing job candidates, scheduling interviews, and leveraging AI for candidate analysis.

## Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Google Gemini](https://img.shields.io/badge/GEMINI-07405E?style=for-the-badge&logo=google&logoColor=white)
![CLI](https://img.shields.io/badge/CLI-4D4D4D?style=for-the-badge&logo=windows-terminal&logoColor=white)
![CSV](https://img.shields.io/badge/CSV-217346?style=for-the-badge&logo=microsoft-excel&logoColor=white)

## Features

- Add candidates with name, age, and resume
- Process candidates using AI analysis
- Generate dummy candidate data for testing
- Manage application settings
- Store candidate information in a CSV database

## Usage

1. To add a candidate:

```bash
python index.py add --name "John Doe" --age 30 --resume "Experienced software engineer with 5 years..."
```

1. To process the next candidate:

```bash
python index.py process
```

or

```bash
python index.py next
```

1. To change a setting:

```bash
python index.py settings --setting max_candidates --value 15
```

1. To view current settings:

```bash
python index.py settings --setting show
```

1. To generate dummy candidate data:

```bash
python index.py fill_dummy
```

or specify the number of dummy candidates:

```bash
python index.py fill_dummy --num 20
```

## AI-Powered Analysis

The tool uses Google's Gemini AI to analyze candidate information and provide:

- A summary of the candidate's key qualities
- A hireability score on a scale of 1-10
- Three other potential roles the candidate might be suitable for

## Data Storage

Candidate information is stored in a `.csv` file, allowing for easy data management and persistence between sessions.

## Configuration

The tool uses a `settings.json` file and environment variables for configuration. Ensure you have set up your Gemini API key in the settings or as an environment variable.

## Getting Started

1. Clone the repository
1. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

1. Set up your Gemini API key in `settings.json` or as an environment variable
1. Run the tool using the commands described in the Usage section
