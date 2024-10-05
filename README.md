# job-cli

A command-line interface tool for managing job candidates and scheduling interviews.

## Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![google](https://img.shields.io/badge/GEMINI-07405E?style=for-the-badge&logo=google&logoColor=white)
![CLI](https://img.shields.io/badge/CLI-4D4D4D?style=for-the-badge&logo=windows-terminal&logoColor=white)

## Usage

1. To add a candidate:

```bash
python index.py add --name "John Doe"
```

1. To process the next candidate:

```bash
python index.py process
```

1. To change a setting:

```bash
python index.py settings --setting max_candidates --value 15
```

1. To view current settings:

```bash
python index.py settings --setting show
```
