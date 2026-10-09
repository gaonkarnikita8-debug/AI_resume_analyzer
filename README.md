# AI Resume Analyzer

## Project Overview

AI Resume Analyzer is a Python-based application that analyzes a resume against a job description. It identifies skills in the resume, calculates a skill-match percentage, highlights missing skills, and provides suggestions to help users prepare for their target roles.

The application includes a web interface built using Streamlit.

## Features

* Upload a resume in PDF format.
* Enter a job description.
* Extract text and detect skills from the resume.
* Identify required skills mentioned in the job description.
* Calculate a resume skill-match score.
* Display matching and missing skills.
* Detect the target job role.
* Identify role-specific skill gaps.
* Provide personalized improvement suggestions.
* Display an application-readiness recommendation.

## Technologies Used

* Python
* Pandas
* Streamlit
* pypdf
* Regular Expressions
* Object-Oriented Programming (OOP)

## Project Structure

```text
AI_resume_analyzer/
├── main.py
├── app.py
├── skills.csv
├── resume.pdf
├── job_description.txt
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd AI_resume_analyzer
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual repository URL.

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Run the application

```bash
python -m streamlit run app.py
```

Open the local URL displayed in your terminal.

## How to Use

1. Open the Streamlit application.
2. Upload your resume as a PDF.
3. Paste the target job description.
4. Click **Analyze Resume**.
5. Review the score, matching skills, missing skills, and improvement suggestions.

## Future Improvements

* Improve skill detection using synonyms and NLP.
* Add downloadable analysis reports.
* Support additional resume formats.
* Improve ATS-oriented resume feedback.
* Add more detailed resume-quality checks.

## Important Note

The match score measures the overlap between skills listed in the application's skills database and skills found in the job description. It is not an official ATS score or a prediction of hiring success.

## Author

Developed as a Python portfolio project to demonstrate Python programming, data processing, PDF text extraction, object-oriented programming, and Streamlit application development.
