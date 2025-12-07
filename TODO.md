# Project: University Semester Scheduler

## Phase 1: Environment & Database Setup
- [ ] **Setup Docker Environment**
    - **File:** `docker-compose.yml`
    - **Description:** Configure services for PostgreSQL (db) and Adminer (db-admin). Ensure persistent volumes for data.
    - **Key Considerations:** Use official images. Expose ports 5432 (Postgres) and 8080 (Adminer).

- [ ] **Initialize Backend Project Structure**
    - **File:** `backend/`
    - **Description:** Set up a high-performance Python FastAPI project structure using `poetry`.
    - **Key Considerations:** Dependencies: `fastapi`, `uvicorn[standard]`, `sqlmodel`, `pydantic`, `asyncpg` (high-perf async DB), `pandas`, `numpy` (vectorized operations), `openpyxl`.

- [ ] **Define Database Models**
    - **File:** `backend/app/models.py`
    - **Description:** Create SQLModel classes for the domain entities.
    - **Entities:**
        - `EntranceTerm`: id (e.g., 14031), year, semester (1 or 2).
        - `Classroom`: id, faculty, capacity, type (Computer Site, Normal, Gallery, Workshop), accessibility_features.
        - `Course`: id, name, required_room_type.
        - `Teacher`: id, name.
        - `TeacherCourseLink`: teacher_id, course_id (Capabilities).
        - `TeacherEntranceLink`: teacher_id, entrance_term_id (Allowed/Restricted).
        - `StudentGroup`: id, field (major), degree (Bachelor, Master, PhD), entrance_term_id, population.
        - `Lesson`: id, course_id, teacher_id, group_id, duration_slots.
        - `TimeSlot`: id, day_of_week, start_time, end_time.
        - `ScheduleResult`: id, lesson_id, room_id, timeslot_id, run_id.
    - **Key Considerations:** Ensure relationships are defined correctly. `StudentGroup` is defined by field, degree, and entrance year. `Classroom` has specific types and faculty association.

- [ ] **Database Connection & Migration**
    - **File:** `backend/app/db.py`
    - **Description:** Setup database engine and session management using SQLModel.
    - **Key Considerations:** Use `asyncpg` for asynchronous database operations if possible, or standard synchronous engine for simplicity with Pandas.

## Phase 2: Backend Services & Data Ingestion
- [ ] **Implement File Upload Endpoint**
    - **File:** `backend/app/api/upload.py`
    - **Description:** Create a FastAPI endpoint to accept `.xlsx` or `.csv` files.
    - **Key Considerations:** Use `python-multipart`. Validate file extension.

- [ ] **Implement Excel Parser & Data Cleaning**
    - **File:** `backend/app/services/parser.py`
    - **Description:** Use Pandas to read the uploaded file. Clean column names, handle Persian characters/encoding, and validate data types.
    - **Key Considerations:** Map Excel columns to DB models. Handle missing values.

- [ ] **Implement Logic for Merging Small Sections**
    - **File:** `backend/app/services/preprocessor.py`
    - **Description:** Implement logic to identify lessons with the same name/type and total population < 50. Merge them into a single `Lesson` entry.
    - **Key Considerations:** This is a "Bin Packing" preprocessing step to optimize resource usage before scheduling.

- [ ] **Classroom Management API**
    - **File:** `backend/app/api/classrooms.py`
    - **Description:** Endpoints to CRUD classrooms (or seed script).
    - **Key Considerations:** Need to define available rooms and their capacities before running the solver.

## Phase 3: Genetic Algorithm (Metaheuristic Solver for NP-Hard Problem)
- [ ] **Define Genome & Population Structure**
    - **File:** `backend/app/solver/genome.py`
    - **Description:** Define how a single schedule solution is represented. Use NumPy arrays for high-performance vectorization.
    - **Key Considerations:** A genome is likely a mapping of `Lesson -> (TimeSlot, Classroom)`. Optimize data structures for speed.

- [ ] **Implement Hard Constraints (Validity Check)**
    - **File:** `backend/app/solver/constraints.py`
    - **Description:** Functions to check if a schedule is valid.
    - **Checks:**
        - **Teacher Conflict:** Teacher cannot be in two places at once.
        - **Teacher Capability:** Teacher must be allowed to teach the assigned Course.
        - **Teacher Entrance Restriction:** Teacher must be allowed to teach the Student Group's Entrance Term.
        - **Room Conflict:** Room cannot host two classes at once.
        - **Room Capacity:** `StudentGroup.population <= Classroom.capacity`.
        - **Room Type:** `Classroom.type` must match `Course.required_room_type`.
        - **Student Group Conflict:** Group cannot have two classes at once.

- [ ] **Implement Weighted Fitness Function (Cost Reduction)**
    - **File:** `backend/app/solver/fitness.py`
    - **Description:** Calculate a total cost score for a valid schedule based on weighted soft constraints. The goal is to minimize this cost.
    - **Scoring (Configurable Weights):**
        - **Teacher Gaps:** Penalize gaps in teacher schedules.
        - **Student Compactness:** Reward schedules compressed into 3 days.
        - **Student Gaps:** Penalize gaps for students on the same day.
        - **Room Utilization:** Optimize for best fit (don't put small class in huge hall).
    - **Key Considerations:** Weights must be configurable per run to prioritize different goals (e.g., "Teacher Comfort" vs "Student Compactness").

- [ ] **Implement Genetic Operators (Crossover & Mutation)**
    - **File:** `backend/app/solver/operators.py`
    - **Description:**
        - `Mutation`: Randomly move a class to a different slot/room.
        - `Crossover`: Combine parts of two parent schedules.
    - **Key Considerations:** Ensure operators respect hard constraints or repair invalid solutions.

- [ ] **Implement Main Solver Loop (Performance Optimized)**
    - **File:** `backend/app/solver/engine.py`
    - **Description:** The main loop: Initialize Population -> Evaluate -> Select -> Crossover -> Mutate -> Repeat.
    - **Key Considerations:**
        - Run as a background task.
        - Implement adaptive parameters or early stopping for Speed vs Accuracy balance.
        - Target only the active semester's courses.

## Phase 4: Frontend (SvelteKit 5 & DaisyUI 5)
- [ ] **Initialize SvelteKit 5 Project**
    - **File:** `frontend/`
    - **Description:** Create a new SvelteKit project. Install TailwindCSS and DaisyUI 5.
    - **Key Considerations:** Enable Runes mode (Svelte 5). Use DaisyUI 5 for high-quality UI/UX components.

- [ ] **Create File Upload Component**
    - **File:** `frontend/src/components/FileUpload.svelte`
    - **Description:** UI to drag-and-drop Excel file and send to backend.
    - **Key Considerations:** Show upload progress and success/error messages.

- [ ] **Create Schedule Grid Component**
    - **File:** `frontend/src/components/ScheduleGrid.svelte`
    - **Description:** A visual representation of the week (Sat-Fri) and time slots.
    - **Key Considerations:** Needs to be flexible to show Teacher View or Student Group View.

- [ ] **Implement State Management**
    - **File:** `frontend/src/lib/scheduleState.svelte.ts`
    - **Description:** Use Svelte 5 `$state` to store the fetched schedule data and current filters (Teacher/Group).
    - **Key Considerations:** Use `$derived` for filtered views.

- [ ] **Dashboard & Visualization**
    - **File:** `frontend/src/routes/+page.svelte`
    - **Description:** Main dashboard combining Upload, "Run Solver" button, and the Schedule Grid.
    - **Key Considerations:** Display conflict alerts if the solver couldn't resolve all hard constraints.

## Phase 5: Integration & Testing
- [ ] **Connect Solver to Frontend**
    - **File:** `frontend/src/lib/api.ts`
    - **Description:** API calls to trigger the solver with specific weights and parameters.
    - **Key Considerations:** Allow user to set weights (sliders/inputs) before running to depict goals.

- [ ] **Result Persistence**
    - **File:** `backend/app/api/solver.py`
    - **Description:** Save the best found schedule to the `ScheduleResult` table.

- [ ] **End-to-End Testing**
    - **Description:** Upload a sample Excel file, run the solver, and verify the output in the grid.
