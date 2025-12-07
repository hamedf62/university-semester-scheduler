export const API_BASE = import.meta.env.VITE_API_BASE || '/api';

export interface Project {
    id: number;
    name: string;
    description?: string;
    term_id?: number;
    is_active: boolean;
    created_at?: string;
    updated_at?: string;
}

export interface Term {
    id: number;
    year: number;
    semester: number; // 1 or 2
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    size: number;
}

export interface Teacher {
    id: number;
    name: string;
    available_slots: number[];
    course_ids: number[];
    created_at?: string;
    updated_at?: string;
}

export interface Course {
    id: number;
    name: string;
    units: number;
    required_room_type: string;
    min_population?: number;
    max_population?: number;
    created_at?: string;
    updated_at?: string;
}

export interface Classroom {
    id: number;
    name: string;
    faculty: string;
    capacity: number;
    type: string;
    created_at?: string;
    updated_at?: string;
}

export interface StudentGroup {
    id: number;
    name: string;
    degree: string;
    population: number;
    allowed_days?: string;
    course_ids: number[];
    created_at?: string;
    updated_at?: string;
}

export interface Lesson {
    id: number;
    course_name: string;
    group_name: string;
    teacher_name: string | null;
    duration_slots: number;
}

export async function getProjects(): Promise<Project[]> {
    const res = await fetch(`${API_BASE}/projects/`);
    if (!res.ok) throw new Error('Failed to fetch projects');
    return await res.json();
}

export async function createProject(name: string, description?: string): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description, is_active: true })
    });
    if (!res.ok) throw new Error('Failed to create project');
    return await res.json();
}

export async function getTerms(): Promise<Term[]> {
    const res = await fetch(`${API_BASE}/terms/`);
    if (!res.ok) throw new Error('Failed to fetch terms');
    return await res.json();
}

export async function createTerm(term: Term): Promise<Term> {
    const res = await fetch(`${API_BASE}/terms/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(term)
    });
    if (!res.ok) throw new Error('Failed to create term');
    return await res.json();
}

export async function getTeachers(projectId?: number, page: number = 1, size: number = 10, search: string = ''): Promise<PaginatedResponse<Teacher>> {
    let url = `${API_BASE}/teachers/?page=${page}&size=${size}`;
    if (projectId) url += `&project_id=${projectId}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch teachers');
    return await res.json();
}

export async function createTeacher(teacher: Partial<Teacher>): Promise<Teacher> {
    const res = await fetch(`${API_BASE}/teachers/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(teacher)
    });
    if (!res.ok) throw new Error('Failed to create teacher');
    return await res.json();
}

export async function updateTeacher(id: number, teacher: Partial<Teacher>): Promise<Teacher> {
    const res = await fetch(`${API_BASE}/teachers/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(teacher)
    });
    if (!res.ok) throw new Error('Failed to update teacher');
    return await res.json();
}

export async function deleteTeacher(id: number): Promise<void> {
    const res = await fetch(`${API_BASE}/teachers/${id}`, {
        method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to delete teacher');
}

export async function getCourses(projectId?: number, page: number = 1, size: number = 10, search: string = ''): Promise<PaginatedResponse<Course>> {
    let url = `${API_BASE}/courses/?page=${page}&size=${size}`;
    if (projectId) url += `&project_id=${projectId}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch courses');
    return await res.json();
}

export async function createCourse(course: Partial<Course>): Promise<Course> {
    const res = await fetch(`${API_BASE}/courses/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(course)
    });
    if (!res.ok) throw new Error('Failed to create course');
    return await res.json();
}

export async function updateCourse(id: number, course: Partial<Course>): Promise<Course> {
    const res = await fetch(`${API_BASE}/courses/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(course)
    });
    if (!res.ok) throw new Error('Failed to update course');
    return await res.json();
}

export async function deleteCourse(id: number): Promise<void> {
    const res = await fetch(`${API_BASE}/courses/${id}`, {
        method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to delete course');
}

export async function getClassrooms(projectId?: number, page: number = 1, size: number = 10, search: string = ''): Promise<PaginatedResponse<Classroom>> {
    let url = `${API_BASE}/classrooms/?page=${page}&size=${size}`;
    if (projectId) url += `&project_id=${projectId}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch classrooms');
    return await res.json();
}

export async function getStudentGroups(projectId?: number, page: number = 1, size: number = 10, search: string = ''): Promise<PaginatedResponse<StudentGroup>> {
    let url = `${API_BASE}/student_groups/?page=${page}&size=${size}`;
    if (projectId) url += `&project_id=${projectId}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch student groups');
    return await res.json();
}

export async function startSolver(weights: any) {
    const res = await fetch(`${API_BASE}/solve`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(weights)
    });
    return await res.json();
}

export async function getResults(runId: string) {
    const res = await fetch(`${API_BASE}/results/${runId}`);
    return await res.json();
}

export async function linkTeacherToProject(teacherId: number, projectId: number): Promise<void> {
    const res = await fetch(`${API_BASE}/teachers/${teacherId}/link?project_id=${projectId}`, {
        method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to link teacher to project');
}

export async function linkCourseToProject(courseId: number, projectId: number): Promise<void> {
    const res = await fetch(`${API_BASE}/courses/${courseId}/link?project_id=${projectId}`, {
        method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to link course to project');
}

export async function addTeacherCourseLink(teacherId: number, courseId: number): Promise<void> {
    const res = await fetch(`${API_BASE}/teachers/${teacherId}/courses/${courseId}`, {
        method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to add teacher course link');
}

export async function removeTeacherCourseLink(teacherId: number, courseId: number): Promise<void> {
    const res = await fetch(`${API_BASE}/teachers/${teacherId}/courses/${courseId}`, {
        method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to remove teacher course link');
}

export async function getLessons(projectId: number): Promise<Lesson[]> {
    const res = await fetch(`${API_BASE}/lessons/?project_id=${projectId}`);
    if (!res.ok) throw new Error('Failed to fetch lessons');
    return await res.json();
}

export async function createStudentGroup(group: Partial<StudentGroup>): Promise<StudentGroup> {
    const res = await fetch(`${API_BASE}/student_groups/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(group)
    });
    if (!res.ok) throw new Error('Failed to create student group');
    return await res.json();
}

export async function updateStudentGroup(id: number, group: Partial<StudentGroup>): Promise<StudentGroup> {
    const res = await fetch(`${API_BASE}/student_groups/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(group)
    });
    if (!res.ok) throw new Error('Failed to update student group');
    return await res.json();
}

export async function deleteStudentGroup(id: number): Promise<void> {
    const res = await fetch(`${API_BASE}/student_groups/${id}`, {
        method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to delete student group');
}

export async function linkStudentGroupToProject(groupId: number, projectId: number): Promise<void> {
    const res = await fetch(`${API_BASE}/student_groups/${groupId}/link?project_id=${projectId}`, {
        method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to link student group to project');
}

export async function createClassroom(classroom: Partial<Classroom>): Promise<Classroom> {
    const res = await fetch(`${API_BASE}/classrooms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(classroom)
    });
    if (!res.ok) throw new Error('Failed to create classroom');
    return await res.json();
}

export async function updateClassroom(id: number, classroom: Partial<Classroom>): Promise<Classroom> {
    const res = await fetch(`${API_BASE}/classrooms/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(classroom)
    });
    if (!res.ok) throw new Error('Failed to update classroom');
    return await res.json();
}

export async function deleteClassroom(id: number): Promise<void> {
    const res = await fetch(`${API_BASE}/classrooms/${id}`, {
        method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to delete classroom');
}

export async function linkClassroomToProject(classroomId: number, projectId: number): Promise<void> {
    const res = await fetch(`${API_BASE}/classrooms/${classroomId}/link?project_id=${projectId}`, {
        method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to link classroom to project');
}
