# Project Status

## Backend
- [x] Update `Lesson` model to make `teacher_id` optional.
- [x] Update `ScheduleResult` model to include `teacher_id`.
- [x] Update `Genome` to include teacher gene.
- [x] Update `ConstraintChecker` to handle dynamic teacher assignment.
- [x] Update `GeneticOperators` to mutate teacher gene.
- [x] Update `SolverEngine` to map teachers and handle dynamic assignment.
- [x] Update `FitnessCalculator` to use teacher index from genome.
- [x] Update API to support Global Resources (Teachers, Courses).
- [x] Update API to link Global Resources to Projects.
- [x] Update API to manage Teacher-Course capabilities.
- [x] Update `upload.py` to handle optional teachers.

## Frontend
- [ ] Create Global Settings Page (Teachers, Courses).
- [ ] Update Project Resources Page (Import from Global).
- [ ] Update Project Details Page (Show dynamic teacher status).
