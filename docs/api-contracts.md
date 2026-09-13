# EduNavika — REST API Contracts & Endpoint Specifications

## 1. Global Conventions

- **Base URL**: `/api/v1`
- **Format**: JSON (`Content-Type: application/json`)
- **Date-Time Format**: ISO 8601 UTC (e.g. `2026-09-13T12:00:00Z`)
- **Identifier Format**: UUIDv4 string (36 characters)
- **Standardized Error Format**:
  All API errors return a structured JSON response:
  ```json
  {
    "success": false,
    "error": {
      "code": "HTTP_404",
      "message": "Resource not found",
      "field": null
    }
  }
  ```
- **Standardized Pagination**:
  List endpoints support `page` (default `1`) and `page_size` (default `50`, max `200`):
  ```json
  {
    "items": [...],
    "metadata": {
      "total_count": 142,
      "page": 1,
      "page_size": 50,
      "total_pages": 3
    }
  }
  ```

---

## 2. Curriculum Endpoints

### `GET /api/v1/standards`
Returns all active grade standards.
- **Response**: `200 OK`
  ```json
  [
    {
      "id": "std-uuid",
      "grade_number": 10,
      "name": "Standard 10",
      "description": "GSEB Class 10",
      "is_active": true,
      "created_at": "2026-09-13T12:00:00Z",
      "updated_at": "2026-09-13T12:00:00Z"
    }
  ]
  ```

### `GET /api/v1/standards/{id}/subjects`
Returns subjects belonging to a given standard.
- **Path Param**: `id` (Standard UUID)
- **Response**: `200 OK`
  ```json
  [
    {
      "id": "subj-uuid",
      "standard_id": "std-uuid",
      "name": "Science",
      "code": "SCI-10",
      "description": "Class 10 Science",
      "is_active": true,
      "created_at": "...",
      "updated_at": "..."
    }
  ]
  ```

### `GET /api/v1/subjects/{id}/chapters`
Returns ordered chapters under a subject.
- **Path Param**: `id` (Subject UUID)
- **Response**: `200 OK`

### `GET /api/v1/chapters/{id}/topics`
Returns ordered topics under a chapter.
- **Path Param**: `id` (Chapter UUID)
- **Response**: `200 OK`

### `GET /api/v1/topics/{id}`
Returns details of a specific topic.
- **Path Param**: `id` (Topic UUID)
- **Response**: `200 OK`

---

## 3. Learning Content Endpoints

### `GET /api/v1/topics/{id}/content`
Returns all grounded curriculum chunks associated with a topic.
- **Path Param**: `id` (Topic UUID)
- **Response**: `200 OK`
  ```json
  [
    {
      "id": "content-uuid",
      "topic_id": "topic-uuid",
      "content_type": "DEFINITION",
      "title": "Combination Reaction",
      "content_text": "A reaction in which a single product is formed...",
      "source_document": "Std-10_Science_English Medium.pdf",
      "source_page": 6,
      "source_reference": "Section 1.2.1",
      "chunk_identifier": "std10_sci_ch1_chunk_004",
      "content_metadata": { "reading_time_min": 2 },
      "created_at": "...",
      "updated_at": "..."
    }
  ]
  ```

---

## 4. MCQ Question Endpoints

### `POST /api/v1/mcqs`
Creates a curriculum-grounded question with automatic duplicate detection and provenance registration.
- **Query Param**: `force` (bool, optional, default `false`)
- **Request Body**:
  ```json
  {
    "topic_id": "topic-uuid",
    "question_text": "What type of reaction is 2Mg + O2 -> 2MgO?",
    "option_a": "Combination Reaction",
    "option_b": "Decomposition Reaction",
    "option_c": "Displacement Reaction",
    "option_d": "Double Displacement Reaction",
    "correct_option": "A",
    "explanation": "Two reactants form a single oxide product.",
    "difficulty": "EASY",
    "source_content_id": "content-uuid",
    "generation_model": "gemma-2-9b-it",
    "generation_version": "v1.2",
    "status": "DRAFT"
  }
  ```
- **Response**: `201 Created`
- **Error (Duplicate)**: `409 Conflict`
  ```json
  {
    "success": false,
    "error": {
      "code": "HTTP_409",
      "message": "Exact duplicate question already exists in repository history.",
      "field": null
    }
  }
  ```

### `GET /api/v1/mcqs/{id}`
Returns question details by ID.

### `GET /api/v1/topics/{id}/mcqs`
Lists questions for a topic with optional query filters:
- `status`: `DRAFT`, `PENDING_REVIEW`, `APPROVED`, `PUBLISHED`
- `difficulty`: `EASY`, `MEDIUM`, `HARD`

### `PATCH /api/v1/mcqs/{id}/status`
Updates question lifecycle status.
- **Request Body**: `{"status": "APPROVED"}`
- **Response**: `200 OK`

---

## 5. Assessment Endpoints

### `POST /api/v1/assessments`
Creates an assessment with optional question links.
- **Request Body**:
  ```json
  {
    "teacher_id": "teacher-uuid",
    "title": "Chemical Equations Quiz",
    "description": "Weekly formative quiz",
    "topic_id": "topic-uuid",
    "questions": [
      { "question_id": "mcq-1-uuid", "question_order": 1, "points": 2.0 }
    ]
  }
  ```
- **Response**: `201 Created`

### `GET /api/v1/assessments/{id}`
Returns assessment details along with linked questions.

### `POST /api/v1/assessments/{id}/publish`
Publishes an assessment to students.
- **Response**: `200 OK` (status set to `PUBLISHED`)

---

## 6. Student Attempt Endpoints

### `POST /api/v1/attempts`
Starts an attempt on a published assessment.
- **Request Body**:
  ```json
  {
    "student_id": "student-uuid",
    "assessment_id": "assessment-uuid"
  }
  ```
- **Response**: `201 Created` (status: `STARTED`)

### `POST /api/v1/attempts/{id}/answers`
Submits an answer during an attempt. Automatically evaluates correctness, registers latency, and emits an immutable `LearningEvent`.
- **Request Body**:
  ```json
  {
    "question_id": "mcq-uuid",
    "selected_option": "A",
    "response_time_ms": 14200,
    "hint_used": false
  }
  ```
- **Response**: `201 Created`

### `POST /api/v1/attempts/{id}/submit`
Finalizes an attempt, calculates total score, percentage, and duration in seconds.
- **Response**: `200 OK` (status: `SUBMITTED`)

### `GET /api/v1/attempts/{id}`
Retrieves complete attempt breakdown and question answers.

---

## 7. Longitudinal Research & Evidence Endpoints

### `POST /api/v1/learning-events`
Directly logs a raw longitudinal interaction event (e.g. self-study, reading, practice).
- **Request Body**:
  ```json
  {
    "student_id": "student-uuid",
    "topic_id": "topic-uuid",
    "event_type": "PRACTICE",
    "score": 5.0,
    "correctness": true,
    "response_time_ms": 11500,
    "hint_used": false,
    "attempt_number": 2,
    "event_metadata": { "platform": "web", "session_id": "sess-01" }
  }
  ```
- **Response**: `201 Created`

### `GET /api/v1/students/{id}/learning-events`
Returns paginated, filterable raw learning events for a student.
- **Query Params**: `topic_id`, `event_type`, `since`, `until`, `page`, `page_size`
- **Response**: `200 OK` (Paginated structure)

### `GET /api/v1/students/{id}/topics/{topic_id}/performance`
Returns aggregated evidence metrics for a student on a specific topic.
- **Response**: `200 OK`
  ```json
  {
    "student_id": "student-uuid",
    "topic_id": "topic-uuid",
    "total_attempts": 6,
    "correct_attempts": 5,
    "accuracy": 83.33,
    "last_activity_at": "...",
    "last_success_at": "...",
    "practice_count": 2,
    "revision_count": 1,
    "average_response_time": 13200.0,
    "hint_usage_count": 1,
    "mastery_state": "MASTERED"
  }
  ```

### `GET /api/v1/students/{id}/revision-plan`
Lists revision scheduling recommendations for a student.

### `GET /api/v1/students/{id}/forgetting-signals`
Lists empirical evidence signals of performance degradation across time gaps.

### `POST /api/v1/teacher-actions`
Logs teacher pedagogical interventions (e.g. `RECOMMEND_REVISION`, `ASSIGN_PRACTICE`, `FLAG_TOPIC`).
