# Resume Screening AI

## Project Description

This is a Resume Screening AI application built using Python and Streamlit as part of the WeIntern Week 2 assignment.

The application compares multiple resumes with a job description, identifies matching and missing skills, calculates match scores, and ranks candidates based on their relevance to the job requirements.

## Technologies Used

- Python
- Streamlit
- Pandas
- pdfplumber
- Scikit-learn

## Features

- Upload multiple resumes in PDF and TXT formats
- Enter a job role and job description
- Extract candidate names, education, and experience
- Identify matching and missing skills using predefined keywords
- Calculate TF-IDF text similarity using cosine similarity
- Calculate a final match score using skill matching and text similarity
- Rank candidates by match score
- View individual candidate reports
- Download candidate rankings as a CSV file

## Scoring Method

The final match score is calculated using:

- 70% weight for required skill matching
- 30% weight for TF-IDF text similarity

Final Score = (0.7 × Skill Score) + (0.3 × Similarity Score)

## How to Run

1. Install Python.
2. Open the project folder in the terminal.
3. Install the required libraries:

   ```
   py -m pip install -r requirements.txt
   ```

4. Run the application:

   ```
   py -m streamlit run app.py
   ```

5. Open the local URL displayed in the terminal.

## Project Files

- `app.py` — Resume Screening AI source code
- `README.md` — Project documentation
- `requirements.txt` — Required Python libraries
- `sample_input_output.md` — Sample inputs and outputs

## Limitations

- Skills are identified using a predefined keyword list.
- Education and experience extraction depends on resume formatting and section headings.
- Match scores are estimates of relevance and should not be treated as the sole basis for hiring decisions.