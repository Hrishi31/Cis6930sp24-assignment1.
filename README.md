# CIS 6930, Spring 2024 Assignment 1: The Censoror

## Name:

HRISHIKESH BALAJI

## UFID:

3299-8859

## Assignment Description

This project is an automated solution designed for censoring sensitive information from text documents. It leverages Python and the Google Cloud Natural Language API to identify and censor personal names, dates, phone numbers, and addresses within text files. This tool is particularly useful for ensuring privacy and compliance with data protection standards by redacting sensitive information before sharing documents.

## How to Install

Ensure you have Python 3.11.0 or later installed on your machine. This project also requires setting up Google Cloud credentials for using the Natural Language API. Follow these steps to set up the project environment:

1. **Environment Setup**: Clone the repository and navigate to the project directory.

2. **Dependency Installation**: Install the necessary Python dependencies using pipenv:

    ```bash
    pipenv install
    ```

3. **Google Cloud Setup**: Follow the Google Cloud documentation to create a project, enable the Natural Language API, and generate a service account key. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of your JSON key file:

    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="path/to/your-service-account-file.json"
    ```

## How to Run

To run the censoring script, use the following command, providing flags for the specific types of information you wish to censor:

```bash
pipenv run python censor.py --input "path/to/input/files/*.txt" --names --dates --phones --address --output "path/to/output" --stats "path/to/stats.txt"
```

### Flags

- `--input`: Glob pattern for input text files.
- `--names`: Enable censoring of personal names.
- `--dates`: Enable censoring of dates.
- `--phones`: Enable censoring of phone numbers.
- `--address`: Enable censoring of addresses.
- `--output`: Directory to store censored files.
- `--stats`: File or location to write statistics of censored information.

## Functions

### `censoror.py`

- Core functionalities to censor sensitive information as specified by the user flags.
- Utility functions for processing text content, including `_censor_dates`, `_censor_phones`, `_censor_names`, and `_censor_addresses`.
- Integration with Google Cloud Natural Language API for identifying names and addresses in the text.

### Additional Scripts

- **Database and Statistical Analysis**: Functions to generate and output statistics on the censored information, helping in understanding the extent of censoring performed.

## Bugs and Assumptions

- **Bugs**: Cannot censor information that Google NLP can't detect.
- **Assumptions**: Assumes consistent text formatting within input documents and accurate detection by the Google Cloud Natural Language API. Variations in text formatting or API inaccuracies may affect censoring accuracy. 

