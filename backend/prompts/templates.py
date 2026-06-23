"""Gemini prompt templates for RAG and analysis."""

RESUME_ANALYSIS_PROMPT = """You are an expert career advisor and resume analyst.

Analyze the following resume data and return a JSON object with:
- summary: A 2-3 sentence professional summary
- strengths: List of top 5 candidate strengths
- skills: List of all identified skills
- missing_skills: Skills commonly expected but not found
- experience_level: junior | mid | senior | lead
- recommended_roles: List of 3-5 suitable job titles

Resume Data:
{resume_data}
"""

JOB_MATCH_PROMPT = """You are an AI job matching expert.

Given a candidate profile and job description, provide:
- match_score: 0-100 integer
- reasoning: 2-3 sentence explanation
- missing_skills: Skills the candidate lacks for this role
- strengths: How the candidate aligns with requirements

Candidate:
{candidate_data}

Job:
{job_data}
"""

LEARNING_ROADMAP_PROMPT = """You are a career development coach.

Create a personalized learning roadmap for the following skill gaps:
{skill_gaps}

Candidate background:
{profile_data}

Return JSON with:
- roadmap: Ordered list of learning steps
- courses: Recommended courses with platform and URL
- certifications: Recommended certifications
- timeline: Estimated weeks to close gaps
"""

SKILL_GAP_PROMPT = """Compare the candidate skills against job requirements.

Candidate Skills: {candidate_skills}
Job Requirements: {job_requirements}

Return JSON with:
- missing_skills: List of skills to develop
- matching_skills: List of aligned skills
- gap_severity: low | medium | high
"""
