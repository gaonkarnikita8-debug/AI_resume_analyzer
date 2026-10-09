
from pathlib import Path

import pandas as pd
import streamlit as st
from pypdf import PdfReader

from main import ResumeAnalyzer


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
)

# --------------------------------------------------
# 2. CUSTOM STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
    .main-title {
        font-size: 38px;
        font-weight: bold;
        color: #6C63FF;
    }
    .subtitle {
        font-size: 17px;
        color: #777777;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">📄 AI Resume Analyzer</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Analyze your resume, identify skill gaps, and prepare for your target role.'
    '</div>',
    unsafe_allow_html=True,
)

st.divider()


# --------------------------------------------------
# 3. LOAD SKILLS DATABASE
# --------------------------------------------------

PROJECT_FOLDER = Path(__file__).resolve().parent
SKILLS_PATH = PROJECT_FOLDER / "skills.csv"

try:
    skills_data = pd.read_csv(SKILLS_PATH)

    required_columns = {"skill", "category"}

    if not required_columns.issubset(skills_data.columns):
        st.error(
            "skills.csv must contain 'skill' and 'category' columns."
        )
        st.stop()

except FileNotFoundError:
    st.error("Could not find skills.csv in the project folder.")
    st.stop()

except Exception as error:
    st.error(f"Could not load skills.csv: {error}")
    st.stop()


def analyzer_category(skills_data, skill):
    rows = skills_data.loc[
        skills_data["skill"].astype(str).str.strip().str.lower()
        == skill.strip().lower(),
        "category",
    ]

    if rows.empty or pd.isna(rows.iloc[0]):
        return None

    return str(rows.iloc[0])

# --------------------------------------------------
# 4. USER INPUTS
# --------------------------------------------------

st.subheader("Step 1: Upload Your Resume")

uploaded_resume = st.file_uploader(
    "Upload your resume in PDF format",
    type=["pdf"],
    help="Choose a PDF resume that contains selectable text.",
)

st.subheader("Step 2: Enter the Job Description")

job_description = st.text_area(
    "Paste the job description here",
    height=220,
    placeholder=(
        "Example: We are looking for a Python Developer "
        "with Python, SQL, FastAPI, REST API, Git and Docker skills."
    ),
)

analyze_button = st.button(
    "🔍 Analyze Resume",
    type="primary",
    use_container_width=True,
)


# --------------------------------------------------
# 5. ANALYZE THE RESUME
# --------------------------------------------------


if analyze_button:

    if uploaded_resume is None:
        st.warning("Please upload your resume PDF first.")

    elif not job_description.strip():
        st.warning("Please enter a job description.")

    else:
        try:
            # Extract text from the uploaded PDF.
            try:
                reader = PdfReader(uploaded_resume)

                if reader.is_encrypted:
                    st.error(
                        "This PDF is password-protected. "
                        "Please upload an unlocked PDF."
                    )
                    st.stop()

                resume_parts = [
                    page.extract_text() or ""
                    for page in reader.pages
                ]

                resume_text = "\n".join(resume_parts)
                page_count = len(reader.pages)

            except Exception:
                st.error(
                    "Unable to read this PDF. "
                    "Please upload a valid, readable PDF file."
                )
                st.stop()

            # Check whether readable text was extracted.
            if not resume_text.strip():
                st.error(
                    "No readable text was found in this PDF. "
                    "It may be a scanned document requiring OCR."
                )
                st.stop()

            # Create an instance of your existing class.
            analyzer = ResumeAnalyzer(
                resume_text,
                job_description,
                skills_data,
            )

            analyzer.page_count = page_count

            # Run the existing analysis methods.
            skills_found = analyzer.find_skills()
            required_skills = analyzer.find_required_skills()

            matching_skills = analyzer.find_matching_skills(
                required_skills,
                skills_found,
            )

            missing_skills = analyzer.find_missing_skills(
                required_skills,
                skills_found,
            )

            match_percentage = analyzer.calculate_match_percentage(
                matching_skills,
                required_skills,
            )

            resume_score = analyzer.calculate_resume_score(
                match_percentage
            )

            detected_role = analyzer.detect_role(job_description)

            role_skills = analyzer.get_role_skills(detected_role)

            role_missing = analyzer.get_role_missing_skills(
                role_skills,
                skills_found,
            )

            missing_by_category = analyzer.find_missing_by_category(
                missing_skills
            )

            strong_categories = analyzer.find_strong_categories(
                matching_skills
            )

            suggestions = analyzer.get_improvement_suggestions(
                missing_skills
            )

            readiness = analyzer.get_application_readiness(
                resume_score
            )

            # Save results for display.
            st.session_state["analysis_results"] = {
                "page_count": page_count,
                "skills_found": skills_found,
                "required_skills": required_skills,
                "matching_skills": matching_skills,
                "missing_skills": missing_skills,
                "match_percentage": match_percentage,
                "resume_score": resume_score,
                "detected_role": detected_role,
                "role_missing": role_missing,
                "missing_by_category": missing_by_category,
                "strong_categories": strong_categories,
                "suggestions": suggestions,
                "readiness": readiness,
            }

        except Exception as error:
            st.error(
                f"An error occurred during analysis: {error}"
            )
# --------------------------------------------------
# 6. DISPLAY THE RESULTS
# --------------------------------------------------

if "analysis_results" in st.session_state:

    results = st.session_state["analysis_results"]

    st.divider()
    st.header("📊 Resume Analysis Dashboard")

    st.caption(
        f"Pages analyzed: {results['page_count']} | "
        f"Target role: {results['detected_role']}"
    )

    # Summary metrics.
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Resume Score",
        f"{results['resume_score']}/100",
    )

    col2.metric(
        "Job Match",
        f"{results['match_percentage']:.1f}%",
    )

    col3.metric(
        "Matching Skills",
        len(results["matching_skills"]),
    )

    col4.metric(
        "Missing Skills",
        len(results["missing_skills"]),
    )

    # Score interpretation.
    if results["resume_score"] >= 80:
        st.success("Strong skill match for this job.")

    elif results["resume_score"] >= 60:
        st.warning("Moderate skill match. Some improvements may help.")

    else:
        st.error("Low skill match. Focus on the missing skills.")

    st.progress(
        min(results["match_percentage"] / 100, 1.0)
    )

    st.caption(
        "This score measures overlap between the listed skills "
        "and the job description. It is not a hiring prediction."
    )

    # Detected skills.
    st.subheader("✅ Skills Found in Your Resume")

    if results["skills_found"]:
        st.write(", ".join(results["skills_found"]))
    else:
        st.info("No skills from skills.csv were detected.")

    # Matching skills.
    st.subheader("🎯 Skills Matching the Job")

    if results["matching_skills"]:
        st.write(", ".join(results["matching_skills"]))
    else:
        st.info("No matching required skills were found.")

    # Missing skills.
    st.subheader("📚 Missing Skills to Improve")

    if results["missing_skills"]:
        for skill in results["missing_skills"]:
            st.write(f"• {skill}")
    else:
        st.success("All detected required skills are present.")

    # Skills grouped by category.
    st.subheader("🗂️ Skills by Category")

    category_rows = []

    for category in sorted(
        skills_data["category"].dropna().astype(str).unique()
    ):
        category_skills = [
            skill
            for skill in results["skills_found"]
            if analyzer_category(
                skills_data, skill
            ) == category
        ] if "analyzer" in locals() else []

        category_rows.append(
            {
                "Category": category,
                "Skills Found": (
                    ", ".join(category_skills)
                    if category_skills
                    else "—"
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(category_rows),
        use_container_width=True,
        hide_index=True,
    )

    # Role-specific skill gaps.
    st.subheader("💼 Role-Specific Skills to Improve")

    if results["role_missing"]:
        st.write(", ".join(results["role_missing"]))
    else:
        st.success("No role-specific skill gaps were identified.")

    # Improvement suggestions.
    st.subheader("🚀 Improvement Suggestions")

    if results["suggestions"]:
        for skill, suggestion in results["suggestions"].items():
            st.markdown(f"**{skill}**")
            st.write(suggestion)
    else:
        st.success("No additional suggestions based on missing skills.")

    # Readiness recommendation.
    st.subheader("📝 Application Readiness")

    st.info(results["readiness"])

    st.caption(
        "A skill-match score alone cannot determine whether you "
        "are qualified for a job. Consider your experience, projects, "
        "education, and the employer's full requirements."
    )