"""Keyword-based skill extraction (no API cost)."""

SKILL_KEYWORDS = [
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "ruby", "php",
    "react", "vue", "angular", "next.js", "nextjs", "django", "flask", "fastapi", "spring",
    "node.js", "nodejs", "express", "rest api", "graphql",
    "sql", "postgresql", "postgres", "mysql", "mongodb", "redis", "dynamodb",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd",
    "machine learning", "deep learning", "nlp", "llm", "rag", "generative ai",
    "prompt engineering", "agentic ai", "microservices", "git", "linux", "agile", "scrum",
    "pandas", "numpy", "tensorflow", "pytorch", "spark", "kafka", "selenium",
    "swift", "kotlin", "scala", "elasticsearch", "figma", "tailwind",
]


def extract_skills_from_text(text: str, limit: int = 12) -> list[str]:
    if not text:
        return []
    text_lower = text.lower()
    found: list[str] = []
    for skill in SKILL_KEYWORDS:
        if skill in text_lower:
            label = skill.upper() if len(skill) <= 3 else skill.title()
            if label not in found:
                found.append(label)
        if len(found) >= limit:
            break
    return found
