# Job Pairing System (Skill Gap Report) - MVP Design Specification

## 1\. System Description & Requirements Analysis

### 1.1 Overview

The Job Pairing System is a web application that quantifies the "fit" between a candidate's resume and a job description. Unlike standard keyword matchers, this system utilizes a Large Language Model (LLM) to extract structured skill data and a **Canonical Skill Registry** (sourced from Stack Overflow tags) to normalize synonyms (e.g., mapping "ReactJS" to "react").

### 1.2 Functional Requirements (FR)

**FR1: Resume Ingestion & Parsing**

  * The system shall accept PDF/DOCX uploads.
  * The system shall immediately extract raw text and store it in the database (`content_text`) to minimize S3 reads.
  * The system shall process resumes asynchronously:
    1.  LLM extracts skills as a list of strings.
    2.  System normalizes strings against the `RefSkill` and `SkillAlias` tables.
    3.  System saves normalized IDs to `resume_skills`.

**FR2: Job Ingestion**

  * The system shall parse Job Descriptions (JDs) to extract Required and Preferred skills.
  * The system shall normalize JD skills using the same ontology as resumes to ensure comparable data.

**FR3: Skill Management (The Ontology)**

  * The system shall maintain a `RefSkill` table seeded with top Stack Overflow tags.
  * The system shall maintain a `SkillAlias` table to resolve variations (e.g., "RoR" $\rightarrow$ "ruby-on-rails").

**FR4: Gap Analysis Engine**

  * The system shall generate a `SkillGapReport` comparing a specific Resume UUID against a Job UUID.
  * The analysis shall calculate:
      * **Match Score:** Percentage based on weighted skill importance.
      * **Missing Skills:** Required skills present in Job but absent in Resume.
      * **Matching Skills:** Skills present in both.

### 1.3 Non-Functional Requirements (NFR)

  * **Performance:** Skill matching queries must run on Integer IDs (not UUIDs) for index efficiency.
  * **Security:** Public-facing entities (Users, Resumes, Reports) must use UUIDv7/v4 to prevent enumeration attacks.
  * **Accuracy:** The system must default to "Exact Match" or "Alias Match." It should not "guess" relationships without data.

-----

## 2\. Use Case Descriptions

### UC-01: Upload and Parse Resume

  * **Actor:** User
  * **Trigger:** User uploads a PDF file.
  * **Pre-conditions:** User is authenticated.

**Flow:**

1.  Frontend uploads file to Backend.
2.  Backend saves file to S3 and creates `Resume` record (Status: `PENDING`).
3.  Backend creates a Background Task and returns `202 Accepted` to Client.
4.  **Background Task:**
      * Extracts text from PDF.
      * Sends text to LLM (structured output mode) to get list of skill strings.
      * **Loop:** For each string:
          * Check `RefSkill` (Exact Match).
          * If no match, check `SkillAlias` (Alias Match).
          * If match found: Insert into `ResumeSkill`.
          * If no match: Log for review (or ignore).
      * Update `Resume` status to `COMPLETED`.

### UC-02: Analyze Job Fit

  * **Actor:** User
  * **Trigger:** User clicks "Analyze" on a specific Job.

**Flow:**

1.  User selects a target Job and one of their parsed Resumes.
2.  Backend fetches:
      * Set A: `job_skills` (Required IDs)
      * Set B: `resume_skills` (User IDs)
3.  Backend calculates `Missing = Set A - Set B`.
4.  Backend calculates `Match Score`.
5.  Backend saves results to `SkillGapReport` and `SkillGapItem`.
6.  Frontend displays the "Missing Skills" list to the user.

-----

## 3\. UML Diagrams

### 3.1 Class Diagram (Database Schema)

This diagram reflects the **Hybrid ID Strategy**: UUIDs for user data, Integers for the high-volume skill ontology.

```mermaid
classDiagram
    direction TB

    %% --- PUBLIC ENTITIES (UUID) ---
    class User {
        +UUID id [PK]
        +String email
        +String password_hash
    }

    class Resume {
        +UUID id [PK]
        +UUID user_id [FK]
        +String file_url
        +Text content_text
        +String status
        +DateTime created_at
    }

    class JobListing {
        +UUID id [PK]
        +String title
        +String company
        +Text content_text
    }

    class SkillGapReport {
        +UUID id [PK]
        +UUID resume_id [FK]
        +UUID job_listing_id [FK]
        +Float score
        +DateTime created_at
    }

    %% --- INTERNAL ONTOLOGY (INTEGER) ---
    class RefSkill {
        +Int id [PK]
        +String name [Unique]
        +Bool is_so_tag
        +Int so_usage_count
    }

    class SkillAlias {
        +Int id [PK]
        +String alias_name [Unique]
        +Int canonical_skill_id [FK]
    }

    %% --- JUNCTION TABLES ---
    class ResumeSkill {
        +Int id [PK]
        +UUID resume_id [FK]
        +Int skill_id [FK]
        +Int years_experience
    }

    class JobSkill {
        +Int id [PK]
        +UUID job_listing_id [FK]
        +Int skill_id [FK]
        +Enum importance
    }

    class SkillGapItem {
        +Int id [PK]
        +UUID report_id [FK]
        +Int skill_id [FK]
        +String status
    }

    %% Relationships
    User "1" --> "*" Resume : owns
    Resume "1" --> "*" ResumeSkill : contains
    ResumeSkill "*" --> "1" RefSkill : maps_to
    
    RefSkill "1" --> "*" SkillAlias : has_variations
    
    JobListing "1" --> "*" JobSkill : requires
    JobSkill "*" --> "1" RefSkill : maps_to

    Resume "1" -- "*" SkillGapReport : compared_in
    JobListing "1" -- "*" SkillGapReport : target_of
    SkillGapReport "1" -- "*" SkillGapItem : details
    SkillGapItem "*" -- "1" RefSkill : references
```

### 3.2 Sequence Diagram: The "Normalize" Logic

This details exactly how the **Stack Overflow Alias** system works during ingestion.

```mermaid
sequenceDiagram
    autonumber
    participant Worker as Background Worker
    participant LLM as AI Model
    participant DB as Database
    
    Worker->>LLM: Send Resume Text
    LLM-->>Worker: Return JSON ["ReactJS", "Go-lang", "Leadership"]
    
    loop For each Skill String
        Worker->>Worker: Normalize String (lowercase, kebab-case)
        note right of Worker: "ReactJS" -> "reactjs"
        
        Worker->>DB: SELECT id FROM ref_skills WHERE name="reactjs"
        alt Direct Match Found
            DB-->>Worker: Return ID (e.g., 101)
        else No Direct Match
            Worker->>DB: SELECT canonical_id FROM skill_aliases WHERE alias_name="reactjs"
            alt Alias Match Found
                DB-->>Worker: Return Canonical ID (e.g., 101)
            else No Match
                Worker->>DB: (Optional) Insert as raw string / Flag for review
            end
        end
        
        Worker->>DB: INSERT INTO resume_skills (resume_id, skill_id=101)
    end
    
    Worker->>DB: UPDATE resumes SET status="COMPLETED"
```

### 3.3 Flowchart


```mermaid
flowchart TD
    StartProc([Start: LLM returns Skill String]) --> Clean[Normalize String\nlowercase, kebab-case]
    Clean --> CheckMaster{Exists in\nRefSkill Table?}
    
    CheckMaster -- Yes --> GetID[Get Master ID]
    
    CheckMaster -- No --> CheckAlias{Exists in\nSkillAlias Table?}
    
    CheckAlias -- Yes --> GetCanonical[Get Canonical ID\nfrom Alias]
    GetCanonical --> GetID
    
    CheckAlias -- No --> Review["Flag for Manual Review\n(Potential New Tech)"]
    
    GetID --> Save[Insert into resume_skills]
    Review --> Log[Log to Warning File]
    
    Save --> Next{More Skills?}
    Log --> Next
    
    Next -- Yes --> StartProc
    Next -- No --> EndProc([End Process])
```

-----

### Recommended Implementation Order

1.  **Database Migration:** Create the tables defined in the Class Diagram.
2.  **Seeding Script:** Write the Python script to import Stack Overflow CSV tags into `RefSkill` and `SkillAlias`.
3.  **FastAPI Backend:**
      * Implement `POST /resumes` (Upload).
      * Implement the `normalize_skill` function (The logic in the Sequence Diagram).
      * Implement `POST /analysis` (The Set Math logic).
4.  **Frontend:** Connect the upload button and the dashboard view.