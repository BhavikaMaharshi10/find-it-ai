# FindItAI — Entity Relationship Diagram

## ER Diagram (Mermaid)

```mermaid
erDiagram
    users ||--o| profiles : has
    users ||--o{ resumes : uploads
    users ||--o{ saved_jobs : bookmarks
    users ||--o{ applications : tracks
    users ||--o{ recommendations : receives
    users ||--o{ ai_logs : generates

    resumes ||--o| resume_embeddings : has
    jobs ||--o| job_embeddings : has
    jobs ||--o{ saved_jobs : saved_in
    jobs ||--o{ applications : applied_to
    jobs ||--o{ recommendations : recommended_in

    recommendations ||--o{ skill_gaps : identifies

    users {
        uuid id PK
        string email UK
        string password
        string first_name
        string last_name
        boolean is_active
        boolean is_staff
        datetime created_at
        datetime updated_at
    }

    profiles {
        uuid id PK
        uuid user_id FK
        string headline
        string location
        string phone
        string linkedin_url
        string github_url
        string avatar
        json preferences
        datetime created_at
        datetime updated_at
    }

    resumes {
        uuid id PK
        uuid user_id FK
        file file
        string original_filename
        text raw_text
        json structured_data
        json skills
        json education
        json work_experience
        json projects
        json certifications
        text ai_summary
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    resume_embeddings {
        uuid id PK
        uuid resume_id FK
        vector embedding "1536 dimensions"
        string model
        datetime created_at
    }

    jobs {
        uuid id PK
        string title
        string company
        text description
        string location
        boolean is_remote
        string experience_level
        json required_skills
        json preferred_skills
        string salary_range
        string employment_type
        string source_url
        boolean is_active
        datetime posted_at
        datetime created_at
        datetime updated_at
    }

    job_embeddings {
        uuid id PK
        uuid job_id FK
        vector embedding "1536 dimensions"
        string model
        datetime created_at
    }

    saved_jobs {
        uuid id PK
        uuid user_id FK
        uuid job_id FK
        text notes
        datetime saved_at
    }

    applications {
        uuid id PK
        uuid user_id FK
        uuid job_id FK
        string status
        text notes
        date applied_date
        date interview_date
        datetime created_at
        datetime updated_at
    }

    recommendations {
        uuid id PK
        uuid user_id FK
        uuid job_id FK
        float match_score
        text reasoning
        json missing_skills
        json strengths
        boolean is_viewed
        datetime created_at
    }

    skill_gaps {
        uuid id PK
        uuid recommendation_id FK
        string skill_name
        string severity
        text learning_suggestion
        datetime created_at
    }

    ai_logs {
        uuid id PK
        uuid user_id FK
        string service
        string action
        json request_data
        json response_data
        int tokens_used
        float cost_usd
        float duration_ms
        datetime created_at
    }
```

## Application Status Enum

```
applied → interview_scheduled → interview_completed → rejected
                                                   → offer_received → accepted
```

## Indexes (Planned)

| Table | Index | Purpose |
|-------|-------|---------|
| `resume_embeddings` | HNSW on `embedding` | Fast cosine similarity search |
| `job_embeddings` | HNSW on `embedding` | Fast cosine similarity search |
| `jobs` | GIN on `required_skills` | Skill-based filtering |
| `applications` | `(user_id, status)` | Dashboard queries |
| `recommendations` | `(user_id, match_score DESC)` | Top recommendations |

## pgvector Setup

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- Example index for cosine similarity
CREATE INDEX ON resume_embeddings
  USING hnsw (embedding vector_cosine_ops);

CREATE INDEX ON job_embeddings
  USING hnsw (embedding vector_cosine_ops);
```
