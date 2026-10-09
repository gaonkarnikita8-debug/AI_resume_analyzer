
from pathlib import Path
import re

import pandas as pd
from pypdf import PdfReader


class ResumeAnalyzer:
    """Analyze a resume against a job description."""

    def __init__(self, resume_text, job_description, skills_data):
        """Initialize the analyzer with resume, job and skills data."""

        self.name = "AI Resume Analyzer"
        self.resume_text = resume_text or ""
        self.job_description = job_description or ""
        self.skills_data = skills_data.copy()
        self.page_count = 0

        self.skills = (
            self.skills_data["skill"]
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )

        print(self.name)

    # --------------------------------------------------
    # 1. SKILL DETECTION
    # --------------------------------------------------

    @staticmethod
    def contains_skill(text, skill):
        """Check whether a skill appears as a whole phrase."""

        pattern = r"\b" + re.escape(skill.strip()) + r"\b"
        return bool(re.search(pattern, text, re.IGNORECASE))

    def find_skills(self):
        """Find skills present in the resume."""

        skills_found = []

        for skill in self.skills:
            if self.contains_skill(self.resume_text, skill):
                skills_found.append(skill)

        return skills_found

    def find_required_skills(self):
        """Find listed skills mentioned in the job description."""

        required_skills = []

        for skill in self.skills:
            if self.contains_skill(self.job_description, skill):
                required_skills.append(skill)

        return required_skills

    @staticmethod
    def find_matching_skills(required_skills, skills_found):
        """Find required skills that are present in the resume."""

        found = {skill.strip().lower() for skill in skills_found}

        return [
            skill
            for skill in required_skills
            if skill.strip().lower() in found
        ]

    @staticmethod
    def find_missing_skills(required_skills, skills_found):
        """Find required skills that are absent from the resume."""

        found = {skill.strip().lower() for skill in skills_found}

        return [
            skill
            for skill in required_skills
            if skill.strip().lower() not in found
        ]

    # --------------------------------------------------
    # 2. CATEGORY ANALYSIS
    # --------------------------------------------------

    def get_category(self, skill):
        """Return the category associated with a skill."""

        rows = self.skills_data.loc[
            self.skills_data["skill"].astype(str).str.strip().str.lower()
            == skill.strip().lower(),
            "category",
        ]

        if rows.empty or pd.isna(rows.iloc[0]):
            return None

        return str(rows.iloc[0])

    def find_missing_by_category(self, missing_skills):
        """Group missing skills by category."""

        missing_by_category = {}

        for skill in missing_skills:
            category = self.get_category(skill)

            if category:
                missing_by_category.setdefault(category, []).append(skill)

        return missing_by_category

    def find_strong_categories(self, matching_skills):
        """Find categories containing matching job skills."""

        categories = {
            self.get_category(skill)
            for skill in matching_skills
        }

        categories.discard(None)

        return sorted(categories)

    def display_skills_by_category(self, skills_found):
        """Display detected resume skills grouped by category."""

        print("\nSkills by Category:")

        for category in sorted(
            self.skills_data["category"].dropna().astype(str).unique()
        ):
            category_skills = [
                skill
                for skill in skills_found
                if self.get_category(skill) == category
            ]

            if category_skills:
                print(f"\n{category}:")

                for skill in category_skills:
                    print("  ✓", skill)

    def display_missing_by_category(self, missing_by_category):
        """Display missing skills grouped by category."""

        print("\nMissing Skills by Category:")

        if not missing_by_category:
            print("  ✓ No missing skills found by category.")
            return

        for category in sorted(missing_by_category):
            print(f"\n{category}:")

            for skill in missing_by_category[category]:
                print("  ❌", skill)

    # --------------------------------------------------
    # 3. SCORE CALCULATION
    # --------------------------------------------------

    @staticmethod
    def calculate_match_percentage(matching_skills, required_skills):
        """Calculate the percentage of unique required skills matched."""

        required = {skill.strip().lower() for skill in required_skills}
        matching = {skill.strip().lower() for skill in matching_skills}

        if not required:
            return 0.0

        matched_count = len(required.intersection(matching))

        return matched_count / len(required) * 100

    @staticmethod
    def calculate_resume_score(result):
        """Convert the match percentage into a whole-number score."""

        return round(result)

    # --------------------------------------------------
    # 4. ROLE DETECTION
    # --------------------------------------------------

    @staticmethod
    def detect_role(job_description):
        """Identify the target role using job description keywords."""

        job_lower = job_description.lower()

        if "machine learning engineer" in job_lower:
            return "Machine Learning Engineer"

        if "data scientist" in job_lower:
            return "Data Scientist"

        if "ai engineer" in job_lower:
            return "AI Engineer"

        if "python developer" in job_lower:
            return "Python Developer"

        return "General Technical Role"

    @staticmethod
    def get_role_skills(detected_role):
        """Return important skills for the detected role."""

        role_skills = {
            "Python Developer": [
                "Python", "SQL", "FastAPI", "REST API",
                "Git", "Docker", "AWS",
            ],
            "Data Scientist": [
                "Python", "SQL", "Pandas", "NumPy",
                "Scikit-learn", "Machine Learning",
            ],
            "Machine Learning Engineer": [
                "Python", "Machine Learning", "Scikit-learn",
                "Pandas", "NumPy", "Docker", "AWS",
            ],
            "AI Engineer": [
                "Python", "Machine Learning", "Deep Learning",
                "Docker", "AWS",
            ],
        }

        return role_skills.get(detected_role, [])

    @staticmethod
    def get_role_missing_skills(role_skills, skills_found):
        """Find role-specific skills missing from the resume."""

        found = {skill.strip().lower() for skill in skills_found}

        return [
            skill
            for skill in role_skills
            if skill.strip().lower() not in found
        ]

    # --------------------------------------------------
    # 5. IMPROVEMENT SUGGESTIONS
    # --------------------------------------------------

    @staticmethod
    def get_improvement_suggestions(missing_skills):
        """Recommend learning resources or actions for missing skills."""

        suggestions = {
            "scikit-learn":
                "Learn Scikit-learn and build Machine Learning projects.",
            "pandas":
                "Improve Pandas skills for data cleaning and analysis.",
            "numpy":
                "Learn NumPy for numerical calculations and data processing.",
            "fastapi":
                "Learn FastAPI to build Python backend applications.",
            "rest api":
                "Learn REST APIs and how applications communicate.",
            "git":
                "Learn Git and GitHub for version control.",
            "docker":
                "Learn Docker basics and containerization.",
            "aws":
                "Learn AWS fundamentals such as EC2 and S3.",
        }

        return {
            skill: suggestions.get(
                skill.strip().lower(),
                "Improve your skills in this area.",
            )
            for skill in missing_skills
        }

    @staticmethod
    def get_application_readiness(resume_score):
        """Return a basic application-readiness recommendation."""

        if resume_score >= 80:
            return "You are ready to apply."

        if resume_score >= 60:
            return "You can apply, but improve the missing skills."

        return "Improve your skills before applying."

    # --------------------------------------------------
    # 6. REPORT DISPLAY METHODS
    # --------------------------------------------------

    def display_resume_review(
        self, result, matching_skills, missing_skills
    ):
        """Display an overall resume review."""

        print("\n" + "=" * 40)
        print("          AI RESUME REVIEW")
        print("=" * 40)

        print("\nOverall Assessment:")

        if result >= 80:
            print("  ✓ Your resume has a strong match for this job.")
        elif result >= 60:
            print("  → Your resume has a moderate match for this job.")
        else:
            print("  → Your resume has a low match for this job.")

        print("\nYour Strengths:")

        if matching_skills:
            for skill in matching_skills:
                print("  ✓", skill)
        else:
            print("  → No matching skills found.")

        print("\nSkills You Should Improve:")

        if missing_skills:
            for skill in missing_skills:
                print("  →", skill)
        else:
            print("  ✓ No major missing skills.")

        print("\nCareer Advice:")

        if result < 60:
            print("  → Focus on missing skills before applying.")
            print("  → Build projects using the required technologies.")
            print("  → Add relevant projects to your resume.")
        elif result < 80:
            print("  → Strengthen the missing skills.")
            print("  → Add projects demonstrating those skills.")
        else:
            print("  → Continue strengthening your projects and experience.")

    @staticmethod
    def display_resume_summary(
        result, required_skills, matching_skills, missing_skills
    ):
        """Display the numerical summary of the analysis."""

        print("\n" + "=" * 40)
        print("        RESUME ANALYSIS SUMMARY")
        print("=" * 40)

        print(f"\nMatch Score: {result:.2f}%")
        print("Required Skills:", len(required_skills))
        print("Matching Skills:", len(matching_skills))
        print("Missing Skills:", len(missing_skills))

    @staticmethod
    def display_category_analysis(
        strong_categories, improvement_categories, result
    ):
        """Display strong and improvement categories."""

        print("\nStrong Areas:")

        if strong_categories:
            for category in strong_categories:
                print("  ✓", category)
        else:
            print("  → No strong areas found.")

        print("\nAreas to Improve:")

        if improvement_categories:
            for category in improvement_categories:
                print("  →", category)
        else:
            print("  ✓ No category-level improvements identified.")

        print("\nFinal Recommendation:")

        if result >= 80:
            print("  ✓ Your resume is a strong skill match for this job.")
        elif result >= 60:
            print("  ✓ Your resume is a good match, but some skills can improve.")
        elif result >= 40:
            print("  → Your resume has a moderate match.")
        else:
            print("  → Focus on missing skills before applying.")

    def display_role_recommendation(self, detected_role):
        """Display advice based on the target role."""

        recommendations = {
            "Python Developer": [
                "Focus on Python backend development.",
                "Learn FastAPI and REST API development.",
                "Strengthen Git and GitHub skills.",
                "Learn Docker for application deployment.",
                "Learn AWS fundamentals.",
            ],
            "Data Scientist": [
                "Focus on data analysis and Machine Learning.",
                "Strengthen Pandas and NumPy.",
                "Learn Scikit-learn.",
                "Build end-to-end Data Science projects.",
            ],
            "Machine Learning Engineer": [
                "Strengthen Machine Learning and Python.",
                "Learn Scikit-learn and model deployment.",
                "Learn Docker and cloud deployment.",
                "Build end-to-end ML projects.",
            ],
            "AI Engineer": [
                "Strengthen Python and AI/ML skills.",
                "Learn Deep Learning and modern AI tools.",
                "Learn Docker and cloud deployment.",
                "Build practical AI applications.",
            ],
        }

        default_recommendations = [
            "Review the required job skills carefully.",
            "Build projects demonstrating the required technologies.",
        ]

        print("\nRole-Specific Recommendation:")

        for recommendation in recommendations.get(
            detected_role, default_recommendations
        ):
            print("  →", recommendation)

    def display_improvement_plan(
        self, detected_role, role_skills, skills_found
    ):
        """Display prioritized learning tasks and a project idea."""

        missing = {
            skill.lower()
            for skill in self.get_role_missing_skills(
                role_skills, skills_found
            )
        }

        priorities = [
            ("Priority 1 - Immediate:", ["FastAPI", "REST API"]),
            ("Priority 2 - Next:", ["Git", "Docker"]),
            ("Priority 3 - Later:", ["AWS"]),
        ]

        print("\n" + "=" * 40)
        print("       RESUME IMPROVEMENT PLAN")
        print("=" * 40)

        for title, priority_skills in priorities:
            print("\n" + title)

            tasks = [
                skill
                for skill in priority_skills
                if skill.lower() in missing
            ]

            if tasks:
                for skill in tasks:
                    print("  →", skill)
            else:
                print("  ✓ No missing skills in this priority group.")

        print("\nSuggested Project:")

        if detected_role == "Python Developer":
            print("  → Build a Python FastAPI application.")
            print("  → Add REST API endpoints.")
            print("  → Connect the application to an SQL database.")
            print("  → Use Git and GitHub for version control.")
            print("  → Containerize it using Docker.")
            print("  → Explore deployment using AWS.")
        else:
            print(
                "  → Build a project demonstrating the missing "
                "skills for your target role."
            )

    @staticmethod
    def display_learning_roadmap(detected_role):
        """Display a role-specific learning roadmap."""

        roadmaps = {
            "Python Developer": [
                ("Learn FastAPI", "Create APIs and learn GET and POST."),
                ("Learn REST APIs", "Understand endpoints and HTTP requests."),
                ("Learn Git", "Practice Git commands and GitHub."),
                ("Learn Docker", "Containerize a FastAPI application."),
                ("Learn AWS", "Understand cloud deployment basics."),
            ],
            "Data Scientist": [
                ("Learn Pandas", "Clean and analyze datasets."),
                ("Learn NumPy", "Practice numerical operations."),
                ("Learn Scikit-learn", "Build and evaluate ML models."),
                ("Build a project", "Complete an end-to-end data project."),
            ],
            "Machine Learning Engineer": [
                ("Learn Python ML tools", "Practice Pandas and NumPy."),
                ("Learn Scikit-learn", "Train and evaluate ML models."),
                ("Learn FastAPI", "Serve a model through an API."),
                ("Learn Docker and AWS", "Explore deployment."),
            ],
            "AI Engineer": [
                ("Strengthen Python", "Build reusable Python applications."),
                ("Learn AI/ML", "Practice Machine Learning and Deep Learning."),
                ("Learn APIs", "Integrate AI into applications."),
                ("Explore deployment", "Learn Docker and cloud basics."),
            ],
        }

        print("\n" + "=" * 40)
        print("          LEARNING ROADMAP")
        print("=" * 40)

        roadmap = roadmaps.get(detected_role)

        if not roadmap:
            print("  → Identify the important skills for your target role.")
            print("  → Learn the missing skills step by step.")
            return

        for number, (title, detail) in enumerate(roadmap, start=1):
            print(f"\nStep {number} - {title}")
            print("  →", detail)

    @staticmethod
    def display_project_suggestions(detected_role):
        """Display project ideas for the target role."""

        projects = {
            "Python Developer": (
                "Build a Python FastAPI REST API",
                [
                    "Create endpoints using FastAPI.",
                    "Use Python for backend development.",
                    "Connect the API to an SQL database.",
                    "Use Git and GitHub.",
                    "Create a Docker container.",
                    "Explore deployment using AWS.",
                ],
            ),
            "Data Scientist": (
                "Build an End-to-End Data Science Project",
                [
                    "Use Pandas and NumPy.",
                    "Clean and analyze data.",
                    "Build a Machine Learning model.",
                    "Use Scikit-learn.",
                    "Evaluate model performance.",
                ],
            ),
            "Machine Learning Engineer": (
                "Build an End-to-End ML Application",
                [
                    "Preprocess data using Pandas.",
                    "Train a model using Scikit-learn.",
                    "Build an API using FastAPI.",
                    "Use Docker.",
                    "Explore AWS deployment.",
                ],
            ),
            "AI Engineer": (
                "Build a Practical AI Application",
                [
                    "Create a Python backend.",
                    "Integrate an AI/ML model.",
                    "Build an API using FastAPI.",
                    "Explore Docker.",
                    "Explore AWS deployment.",
                ],
            ),
        }

        print("\n" + "=" * 40)
        print("       PROJECT SUGGESTIONS")
        print("=" * 40)

        project = projects.get(detected_role)

        if not project:
            print("  → Build a project based on the required job skills.")
            return

        title, features = project

        print("\nRecommended Project:\n  →", title)
        print("\nProject Features:")

        for feature in features:
            print("  →", feature)

    def display_application_checklist(
        self, matching_skills, missing_skills, skills_found, detected_role
    ):
        """Display a checklist of application preparation tasks."""

        checklist = {
            "Resume skills match job requirements": bool(matching_skills),
            "All listed required skills matched": not missing_skills,
            "Relevant project available": True,
            "GitHub skill detected in resume": any(
                skill.lower() == "github" for skill in skills_found
            ),
            "Target role identified": (
                detected_role != "General Technical Role"
            ),
        }

        print("\n" + "=" * 40)
        print("     JOB APPLICATION CHECKLIST")
        print("=" * 40)

        for item, status in checklist.items():
            print("  " + ("✓" if status else "❌"), item)

    @staticmethod
    def display_application_readiness(resume_score, recommendation):
        """Display the final readiness assessment."""

        print("\n" + "=" * 40)
        print("       APPLICATION READINESS")
        print("=" * 40)

        if resume_score >= 80:
            print("\n🟢 Strong Skill Match")
            print("  → Your resume matches many of the listed job skills.")
        elif resume_score >= 60:
            print("\n🟡 Moderate Skill Match")
            print("  → Consider improving the missing skills.")
        else:
            print("\n🔴 Low Skill Match")
            print("  → Focus on priority skills and relevant projects.")

        print("\nRecommendation:")
        print("  →", recommendation)
        print("\nNote: This is a skill-match estimate, not a hiring prediction.")

    # --------------------------------------------------
    # 7. MAIN ANALYSIS METHOD
    # --------------------------------------------------

    def run_analysis(self):
        """Coordinate the resume analysis and display the report."""

        # Step A: Find skills
        skills_found = self.find_skills()
        required_skills = self.find_required_skills()

        matching_skills = self.find_matching_skills(
            required_skills, skills_found
        )
        missing_skills = self.find_missing_skills(
            required_skills, skills_found
        )

        # Step B: Calculate scores
        result = self.calculate_match_percentage(
            matching_skills, required_skills
        )
        resume_score = self.calculate_resume_score(result)

        # Step C: Analyze categories
        missing_by_category = self.find_missing_by_category(
            missing_skills
        )
        strong_categories = self.find_strong_categories(
            matching_skills
        )
        improvement_categories = sorted(missing_by_category.keys())

        # Step D: Analyze the role
        detected_role = self.detect_role(self.job_description)
        role_skills = self.get_role_skills(detected_role)
        role_missing = self.get_role_missing_skills(
            role_skills, skills_found
        )

        # Step E: Prepare suggestions
        suggestions = self.get_improvement_suggestions(missing_skills)
        application_readiness = self.get_application_readiness(
            resume_score
        )

        # Step F: Display the report
        print("\nNumber of pages:", self.page_count)

        print("\nSkills Found:")
        if skills_found:
            for skill in skills_found:
                print("✅", skill)
        else:
            print("No skills from skills.csv were detected in the resume.")

        self.display_skills_by_category(skills_found)

        print("\nJob Description:")
        print(self.job_description)

        print("\nRequired Skills for the Job:")
        if required_skills:
            for skill in required_skills:
                print("✅", skill)
        else:
            print("No listed skills were detected in the job description.")

        self.display_resume_review(
            result, matching_skills, missing_skills
        )
        self.display_resume_summary(
            result, required_skills, matching_skills, missing_skills
        )
        self.display_category_analysis(
            strong_categories, improvement_categories, result
        )
        self.display_missing_by_category(missing_by_category)

        print("\n" + "=" * 40)
        print("      RESUME IMPROVEMENT SUGGESTIONS")
        print("=" * 40)

        if suggestions:
            for skill, recommendation in suggestions.items():
                print(f"  → {skill}: {recommendation}")
        else:
            print("  ✓ No improvement suggestions needed.")

        print("\nDetected Role:\n  →", detected_role)

        print("\nRole Readiness:")
        if result >= 80:
            print("  ✓ Strong skill-match score for this role.")
        elif result >= 60:
            print("  → Moderate skill-match score for this role.")
        else:
            print("  → Low skill-match score for this role.")
            print("  → Review the role-specific missing skills below.")

        print("\nRole-Specific Skills to Improve:")
        if role_missing:
            for skill in role_missing:
                print("  →", skill)
        else:
            print("  ✓ No role-specific skills missing.")

        self.display_role_recommendation(detected_role)

        print("\n" + "=" * 40)
        print("            RESUME SCORE")
        print("=" * 40)
        print("\nResume Score:", resume_score, "/ 100")

        if resume_score >= 80:
            rating = "Excellent skill match"
        elif resume_score >= 60:
            rating = "Good skill match"
        elif resume_score >= 40:
            rating = "Needs improvement"
        else:
            rating = "Low skill match"

        print("\nRating:\n  →", rating)
        print("\nMain Areas to Improve:")

        if missing_skills:
            for skill in missing_skills:
                print("  →", skill)
        else:
            print("  ✓ No listed required skills are missing.")

        self.display_improvement_plan(
            detected_role, role_skills, skills_found
        )
        self.display_learning_roadmap(detected_role)
        self.display_project_suggestions(detected_role)

        self.display_application_checklist(
            matching_skills,
            missing_skills,
            skills_found,
            detected_role,
        )

        self.display_application_readiness(
            resume_score, application_readiness
        )


# --------------------------------------------------
# 8. MAIN FUNCTION: LOAD FILES AND START THE PROGRAM
# --------------------------------------------------

def main():
    """Load input files and run the ResumeAnalyzer."""

    project_folder = Path(__file__).resolve().parent

    resume_path = project_folder / "resume.pdf"
    skills_path = project_folder / "skills.csv"
    job_description_path = project_folder / "job_description.txt"

    # Check that all required files exist.
    for file_path in (
        resume_path,
        skills_path,
        job_description_path,
    ):
        if not file_path.exists():
            raise FileNotFoundError(
                f"Required file not found: {file_path.name}. "
                "Keep it in the same folder as main.py."
            )

    # Extract text from the resume PDF.
    reader = PdfReader(str(resume_path))
    resume_parts = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        resume_parts.append(page_text)

    resume_text = "\n".join(resume_parts)

    if not resume_text.strip():
        raise ValueError(
            "No readable text found in resume.pdf. "
            "The PDF may be scanned and require OCR."
        )

    # Load the skills database.
    skills_data = pd.read_csv(skills_path)

    required_columns = {"skill", "category"}
    if not required_columns.issubset(skills_data.columns):
        raise ValueError(
            "skills.csv must contain 'skill' and 'category' columns."
        )

    # Load the job description.
    job_description = job_description_path.read_text(
        encoding="utf-8"
    )

    if not job_description.strip():
        raise ValueError("job_description.txt is empty.")

    # Create the analyzer object.
    analyzer = ResumeAnalyzer(
        resume_text,
        job_description,
        skills_data,
    )

    analyzer.page_count = len(reader.pages)

    # Run the complete analysis.
    analyzer.run_analysis()


if __name__ == "__main__":
    main()