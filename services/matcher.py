from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Generic words to ignore
GENERIC_WORDS = {
    "data", "analysis", "experience", "learning",
    "looking", "strong", "machine"
}


from services.skill_map import SKILL_SYNONYMS

def normalize_skills(keywords):
    normalized = set()

    for kw in keywords:
        kw_lower = kw.lower()
        matched = False

        for canonical, variants in SKILL_SYNONYMS.items():
            if kw_lower == canonical or kw_lower in variants:
                normalized.add(canonical)
                matched = True
                break

        if not matched:
            normalized.add(kw_lower)

    return list(normalized)






def compute_similarity(text1, text2):
    if not text1.strip() or not text2.strip():
        return 0.0

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=2000
    )

    tfidf = vectorizer.fit_transform([text1, text2])
    return cosine_similarity(tfidf[0], tfidf[1])[0][0]


def extract_keywords(text):
    """
    Extract meaningful keywords from text using TF-IDF
    """
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=50
    )

    tfidf = vectorizer.fit_transform([text])
    keywords = vectorizer.get_feature_names_out()

    cleaned = []
    for kw in keywords:
        if len(kw.split()) == 1 and kw in GENERIC_WORDS:
            continue
        cleaned.append(kw)

    return set(cleaned)


def analyze_resumes(resume_sections, jd_text):
    results = []

    jd_skills = extract_keywords(jd_text)

    for sections in resume_sections:
        # Section-wise similarity
        skills_score = compute_similarity(sections["skills"], jd_text)
        experience_score = compute_similarity(sections["experience"], jd_text)
        projects_score = compute_similarity(sections["projects"], jd_text)

        final_score = (
            0.5 * skills_score +
            0.3 * experience_score +
            0.2 * projects_score
        )

        # Skill coverage
        resume_skills = extract_keywords(sections["skills"])

        raw_matched = resume_skills & jd_skills
        raw_missing = jd_skills - resume_skills

        matched_skills = normalize_skills(list(raw_matched))
        missing_skills = normalize_skills(list(raw_missing))

        coverage = (
            len(matched_skills) / len(jd_skills)
            if jd_skills else 0
        )

        results.append({
            "score": final_score,
            "skills_score": skills_score,
            "experience_score": experience_score,
            "projects_score": projects_score,
            "skill_coverage": coverage,
            "matched_skills": matched_skills[:10],
            "missing_skills": missing_skills[:10]
        })

    return results
