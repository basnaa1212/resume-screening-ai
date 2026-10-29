import streamlit as st
import pdfplumber
import pandas as pd
import re
from io import BytesIO
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Resume Screening AI",page_icon="📄",layout="wide")

st.title("📄Resume Screening AI")
st.write("Upload multiple resume and rank candidates based on a job description")

SKILLS = [
    "python", "java", "c", "c++", "javascript", "php",
    "artificial intelligence", "machine learning", "deep learning",
    "data science", "data analysis", "natural language processing",
    "computer vision", "scikit-learn", "tensorflow", "pytorch",
    "pandas", "numpy", "matplotlib", "html", "css", "react",
    "bootstrap", "django", "flask", "node.js", "express.js",
    "rest api", "full stack development", "web development",
    "mysql", "postgresql", "mongodb", "git", "github", "docker",
    "streamlit", "excel", "power bi", "tableau", "communication",
    "problem-solving", "teamwork"
]

def extract_text(uploaded_file):
    try:
        if uploaded_file.name.lower().endswith(".pdf"):
            with pdfplumber.open(BytesIO(uploaded_file.getvalue())) as pdf:
                return "\n".join(
                    page.extract_text() or "" for page in pdf.pages
                )
        return uploaded_file.getvalue().decode("utf-8",errors="ignore")
    except Exception:
        return""

def find_skills(text):
    text_lower=text.lower()
    found=[]
    for skill in SKILLS:
        pattern=r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern,text_lower):
            found.append(skill)
    return found

def extract_name(text,filename):
    lines=[line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:8]:
        words=line.split()
        if 2 <= len(words) <=4:
            if not any(word.lower() in [
                "resume", "curriculum", "vitae", "profile",
                "education", "experience", "skills",
                "intern", "engineer", "developer", "analyst",
                "machine", "learning", "data", "science",
                "summary", "objective", "qualification",
                "contact", "projects", "certifications"
            ] for word in words):
                return line
    return filename.rsplit(".",1)[0]

def extract_education(text):
    lines=text.splitlines()
    education_lines=[]
    in_education=False

    for line in lines:
        line=line.strip()
        if line.lower() in ["education","educational qualification"]:
            in_education=True
            continue
        if in_education:
            if line.lower() in [
                "skills", "projects", "experience",
                "professional summary", "certifications"
            ]:
                break
            if line:
                education_lines.append(line)
    return "; ".join(education_lines) if education_lines else "Not found"

def extract_experience(text):
    lines=text.splitlines()
    experience_lines=[]
    in_experience=False

    for line in lines:
        line=line.strip()
        if line.lower() in[
            "experience",
            "work experience",
            "professional experience",
            "internship",
            "employment history"
        ]:
            in_experience=True
            continue
        if in_experience:
            if line.lower() in [
                "education", "skills", "projects",
                "certifications", "technical skills",
                "professional summary"  
            ]:
                break
            if line:
                experience_lines.append(line)
    return "; ".join(experience_lines) if experience_lines else "Not found"

job_role=st.text_input("Job Role",placeholder="eg: AIML Intern")
job_description=st.text_area(
    "Job Description",
    placeholder="Enter the job requirements"
)

uploaded_resumes=st.file_uploader(
    "Upload Resumes (PDF or txt)",
    type=["pdf","txt"],
    accept_multiple_files=True
)

if st.button("Screen and Rank Candidates",type="primary"):
    if not job_role.strip():
        st.warning("Please enter the job role.")
    elif not job_description.strip():
        st.warning("Please enter job description.")
    elif not uploaded_resumes:
        st.warning("Please upload resume.")
    else:
        candidates=[]

        for file in uploaded_resumes:
            text=extract_text(file)
            if not text.strip():
                st.warning(f"Could not extract readable text from {file.name}.")
                continue

            resume_skills=find_skills(text)
            required_skills=find_skills(job_description)
            matched=[s for s in required_skills if s in resume_skills]
            missing=[s for s in required_skills if s not in resume_skills]

            try:
                vectorizer=TfidfVectorizer(
                    stop_words="english",
                    ngram_range=(1,2)
                )
                vectors=vectorizer.fit_transform([job_description,text])
                similarity=cosine_similarity(
                    vectors[0:1],vectors[1:2]
                )[0][0]*100
            except ValueError:
                similarity=0.0

            skill_score=(
                len(matched)/len(required_skills)*100
                if required_skills else 0.0
            )

            score=0.3 * similarity + 0.7 * skill_score

            candidates.append({
                "Candidate Name": extract_name(text, file.name),
                "Resume File": file.name,
                "Matching Skills": ", ".join(matched) or "Not found",
                "Missing Skills": ", ".join(missing) or "Not found",
                "Match Score (%)": round(score, 2),
                "Education": extract_education(text),
                "Experience": extract_experience(text),
                "Summary": (
                    f"{extract_name(text, file.name)} has "
                    f"{len(matched)} of {len(required_skills)} recognized required skills. "
                    f"Similarity: {similarity:.2f}%."
                ),
                "Resume Text": text
            })

        if not candidates:
            st.error("No readable resumes were found. Please check the files.")
        else:
            results=pd.DataFrame(candidates)
            results=results.sort_values(
                "Match Score (%)",ascending=False
            ).reset_index(drop=True)
            results.insert(0,"Rank",range(1,len(results) + 1))

            st.success("Resume screening completed!")

            st.subheader(f"Candidate Rankings: {job_role.strip()}")

            st.table(
                results[
                    ["Rank", "Candidate Name", "Matching Skills", "Missing Skills", "Match Score (%)"]
                ].style.format({"Match Score (%)": "{:.2f}%"})
            )

            st.subheader("Individual Candidate Reports")
            for _, candidate in results.iterrows():
                with st.expander(candidate["Candidate Name"]):
                    st.write("**Resume File:**", candidate["Resume File"])
                    st.write("**Matching Skills:**", candidate["Matching Skills"])
                    st.write("**Missing Skills:**", candidate["Missing Skills"])
                    st.write("**Match Score:**", f'{candidate["Match Score (%)"]:.2f}%')
                    st.write("**Education:**", candidate["Education"])
                    st.write("**Experience:**", candidate["Experience"])
                    st.write("**Summary:**", candidate["Summary"])

            st.download_button(
                "Download Ranking Report(csv)",
                data=results.drop(columns=["Resume Text"]).to_csv(index=False).encode("utf-8-sig"),
                file_name="candidate_ranking_report.csv"
            )