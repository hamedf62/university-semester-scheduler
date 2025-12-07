<script lang="ts">
    import { page } from "$app/stores";
    import { onMount } from "svelte";
    import {
        API_BASE,
        getTeachers,
        getCourses,
        getLessons,
        linkTeacherToProject,
        linkCourseToProject,
        type Project,
        type Classroom,
        type Teacher,
        type Course,
        type StudentGroup,
        type Lesson,
    } from "$lib/api";
    import { formatDate } from "$lib/utils";
    import FileUpload from "../../../components/FileUpload.svelte";
    import ScheduleGrid from "../../../components/ScheduleGrid.svelte";
    import EditableTable from "../../../components/EditableTable.svelte";
    import TimeSlotModal from "../../../components/TimeSlotModal.svelte";
    import DaySelector from "../../../components/DaySelector.svelte";
    import CourseSelector from "../../../components/CourseSelector.svelte";

    let projectId = $derived($page.params.id ?? "");
    let activeTab = $state("data"); // 'data', 'solver', 'results'
    let dataTab = $state("upload"); // 'upload', 'classrooms', 'teachers', 'courses', 'groups'
    let project: Project | null = $state(null);

    // Data State
    let classrooms: Classroom[] = $state([]);
    let teachers: Teacher[] = $state([]);
    let courses: Course[] = $state([]);
    let groups: StudentGroup[] = $state([]);
    let lessons: Lesson[] = $state([]);
    let timeSlots: any[] = $state([]);

    // Solver State
    let weights = $state({
        teacher_idle: 1.0,
        student_idle: 1.0,
        student_compactness: 1.0,
    });
    let maxStagnantGenerations = $state(150);
    let solverStatus = $state("idle"); // idle, running, completed, failed
    let solverProgress = $state(0);
    let runId = $state(null);
    let scheduleResults = $state([]);
    let solverRuns: any[] = $state([]);
    let currentRun: any = $state(null);

    // Linking State
    let showLinkTeacherModal = $state(false);
    let showLinkCourseModal = $state(false);
    let globalTeachers: Teacher[] = $state([]);
    let globalCourses: Course[] = $state([]);

    async function fetchProject() {
        const res = await fetch(`${API_BASE}/projects/${projectId}`);
        if (res.ok) project = await res.json();
    }

    async function fetchSolverRuns() {
        const res = await fetch(`${API_BASE}/projects/${projectId}/runs`);
        if (res.ok) {
            solverRuns = await res.json();
        }
    }

    async function fetchTimeSlots() {
        const res = await fetch(`${API_BASE}/timeslots/`);
        if (res.ok) timeSlots = await res.json();
    }

    async function fetchData(type: string) {
        try {
            let url = "";
            if (type === "classrooms")
                url = `${API_BASE}/classrooms/?project_id=${projectId}`;
            else if (type === "teachers")
                url = `${API_BASE}/teachers/?project_id=${projectId}`;
            else if (type === "courses")
                url = `${API_BASE}/courses/?project_id=${projectId}`;
            else if (type === "groups")
                url = `${API_BASE}/student_groups/?project_id=${projectId}`;
            else if (type === "lessons")
                url = `${API_BASE}/lessons/?project_id=${projectId}`;

            if (url) {
                const res = await fetch(url);
                if (res.ok) {
                    const data = await res.json();
                    if (type === "classrooms") classrooms = data;
                    else if (type === "teachers") teachers = data;
                    else if (type === "courses") courses = data;
                    else if (type === "groups") groups = data;
                    else if (type === "lessons") lessons = data;
                }
            }
        } catch (e) {
            console.error(e);
        }
    }

    onMount(() => {
        fetchProject();
        fetchTimeSlots();
    });

    $effect(() => {
        if (activeTab === "data" && dataTab !== "upload") {
            fetchData(dataTab);
        }
        if (activeTab === "solver") {
            fetchSolverRuns();
        }
    });

    // --- CRUD Handlers ---

    // Classrooms
    async function handleClassroomUpdate(event: CustomEvent) {
        const updated = event.detail;
        const res = await fetch(`${API_BASE}/classrooms/${updated.id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updated),
        });
        if (res.ok) {
            const data = await res.json();
            classrooms = classrooms.map((c) => (c.id === data.id ? data : c));
        }
    }
    async function handleClassroomCreate() {
        const newRoom = {
            name: "New Room",
            faculty: "Eng",
            capacity: 30,
            type: "normal",
            project_id: parseInt(projectId),
        };
        const res = await fetch(`${API_BASE}/classrooms`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(newRoom),
        });
        if (res.ok) {
            const data = await res.json();
            classrooms = [...classrooms, data];
        }
    }
    async function handleClassroomDelete(event: CustomEvent) {
        const row = event.detail;
        const res = await fetch(`${API_BASE}/classrooms/${row.id}`, {
            method: "DELETE",
        });
        if (res.ok) {
            classrooms = classrooms.filter((c) => c.id !== row.id);
        }
    }

    // Teachers
    async function handleTeacherUpdate(event: CustomEvent) {
        const updated = event.detail;
        const payload = { ...updated, project_id: parseInt(projectId) };
        const res = await fetch(`${API_BASE}/teachers/${updated.id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        if (res.ok) {
            const data = await res.json();
            teachers = teachers.map((t) => (t.id === data.id ? data : t));
        }
    }
    async function handleTeacherCreate() {
        const newTeacher = {
            name: "New Teacher",
            available_slots: [],
            project_id: parseInt(projectId),
        };
        const res = await fetch(`${API_BASE}/teachers/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(newTeacher),
        });
        if (res.ok) {
            const data = await res.json();
            teachers = [...teachers, data];
        }
    }
    async function handleTeacherDelete(event: CustomEvent) {
        const row = event.detail;
        const res = await fetch(`${API_BASE}/teachers/${row.id}`, {
            method: "DELETE",
        });
        if (res.ok) {
            teachers = teachers.filter((t) => t.id !== row.id);
        }
    }

    // Courses
    async function handleCourseUpdate(event: CustomEvent) {
        const updated = event.detail;
        const res = await fetch(`${API_BASE}/courses/${updated.id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updated),
        });
        if (res.ok) {
            const data = await res.json();
            courses = courses.map((c) => (c.id === data.id ? data : c));
        }
    }
    async function handleCourseCreate() {
        const newCourse = {
            name: "New Course",
            units: 3,
            required_room_type: "normal",
            min_population: 20,
            max_population: 40,
            project_id: parseInt(projectId),
        };
        const res = await fetch(`${API_BASE}/courses/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(newCourse),
        });
        if (res.ok) {
            const data = await res.json();
            courses = [...courses, data];
        }
    }
    async function handleCourseDelete(event: CustomEvent) {
        const row = event.detail;
        const res = await fetch(`${API_BASE}/courses/${row.id}`, {
            method: "DELETE",
        });
        if (res.ok) {
            courses = courses.filter((c) => c.id !== row.id);
        }
    }

    // Groups
    async function handleGroupUpdate(event: CustomEvent) {
        const updated = event.detail;
        const res = await fetch(`${API_BASE}/student_groups/${updated.id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updated),
        });
        if (res.ok) {
            const data = await res.json();
            groups = groups.map((g) => (g.id === data.id ? data : g));
        }
    }
    async function handleGroupCreate() {
        const newGroup = {
            name: "New Group",
            population: 30,
            degree: "bachelor",
            allowed_days: "",
            course_ids: [],
            project_id: parseInt(projectId),
        };
        const res = await fetch(`${API_BASE}/student_groups/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(newGroup),
        });
        if (res.ok) {
            const data = await res.json();
            groups = [...groups, data];
        }
    }
    async function handleGroupDelete(event: CustomEvent) {
        const row = event.detail;
        const res = await fetch(`${API_BASE}/student_groups/${row.id}`, {
            method: "DELETE",
        });
        if (res.ok) {
            groups = groups.filter((g) => g.id !== row.id);
        }
    }

    async function startSolver() {
        const res = await fetch(`${API_BASE}/solver/solve`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                project_id: parseInt(projectId),
                weights: weights,
                max_stagnant_generations: maxStagnantGenerations,
            }),
        });
        if (res.ok) {
            const data = await res.json();
            runId = data.run_id;
            solverStatus = "running";
            pollStatus();
        }
    }

    async function pollStatus() {
        if (!runId) return;
        const interval = setInterval(async () => {
            const res = await fetch(`${API_BASE}/solver/status/${runId}`);
            const data = await res.json();
            solverStatus = data.status;
            solverProgress = data.progress || 0;

            if (data.status === "completed" || data.status === "failed") {
                clearInterval(interval);
                if (data.status === "completed") {
                    fetchResults(runId);
                }
            }
        }, 1000);
    }

    async function fetchResults(id = runId) {
        if (!id) return;
        const res = await fetch(`${API_BASE}/results/${id}`);
        if (res.ok) {
            scheduleResults = await res.json();
            activeTab = "results";
            currentRun = solverRuns.find((r) => r.run_id === id);
        }
    }

    async function fetchProjectResults() {
        // Deprecated in favor of fetchSolverRuns
    }

    onMount(async () => {
        await fetchProject();
        await fetchProjectResults();
    });

    async function openLinkTeacherModal() {
        const res = await getTeachers(undefined, 1, 1000); // Fetch all
        globalTeachers = res.items;
        // Filter out already linked
        const linkedIds = new Set(teachers.map((t) => t.id));
        globalTeachers = globalTeachers.filter((t) => !linkedIds.has(t.id));
        showLinkTeacherModal = true;
    }

    async function openLinkCourseModal() {
        const res = await getCourses(undefined, 1, 1000); // Fetch all
        globalCourses = res.items;
        const linkedIds = new Set(courses.map((c) => c.id));
        globalCourses = globalCourses.filter((c) => !linkedIds.has(c.id));
        showLinkCourseModal = true;
    }

    async function handleLinkTeacher(teacherId: number) {
        await linkTeacherToProject(teacherId, parseInt(projectId));
        showLinkTeacherModal = false;
        await fetchData("teachers");
    }

    async function handleLinkCourse(courseId: number) {
        await linkCourseToProject(courseId, parseInt(projectId));
        showLinkCourseModal = false;
        await fetchData("courses");
    }
</script>

<div class="container mx-auto p-4">
    <div class="text-sm breadcrumbs mb-4">
        <ul>
            <li><a href="/">Projects</a></li>
            <li>{project ? `Term ${project.term_id}` : "Loading..."}</li>
        </ul>
    </div>

    <div role="tablist" class="tabs tabs-boxed mb-6">
        <button
            role="tab"
            class="tab"
            class:tab-active={activeTab === "data"}
            onclick={() => (activeTab = "data")}>Data Entry</button
        >
        <button
            role="tab"
            class="tab"
            class:tab-active={activeTab === "solver"}
            onclick={() => (activeTab = "solver")}>Solver</button
        >
        <button
            role="tab"
            class="tab"
            class:tab-active={activeTab === "results"}
            onclick={() => (activeTab = "results")}>Results</button
        >
    </div>

    {#if activeTab === "data"}
        <div class="flex flex-col md:flex-row gap-6">
            <ul class="menu bg-base-200 w-full md:w-56 rounded-box h-fit">
                <li>
                    <button
                        class:active={dataTab === "upload"}
                        onclick={() => (dataTab = "upload")}
                        >Upload Excel</button
                    >
                </li>
                <li>
                    <button
                        class:active={dataTab === "classrooms"}
                        onclick={() => (dataTab = "classrooms")}
                        >Classrooms</button
                    >
                </li>
                <li>
                    <button
                        class:active={dataTab === "teachers"}
                        onclick={() => (dataTab = "teachers")}>Teachers</button
                    >
                </li>
                <li>
                    <button
                        class:active={dataTab === "courses"}
                        onclick={() => (dataTab = "courses")}>Courses</button
                    >
                </li>
                <li>
                    <button
                        class:active={dataTab === "groups"}
                        onclick={() => (dataTab = "groups")}
                        >Student Groups</button
                    >
                </li>
                <li>
                    <button
                        class:active={dataTab === "lessons"}
                        onclick={() => (dataTab = "lessons")}>Lessons</button
                    >
                </li>
            </ul>

            <div class="flex-1">
                {#if dataTab === "upload"}
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Upload Data</h2>
                            <p>Upload Excel files to populate the database.</p>
                            <FileUpload {projectId} />
                        </div>
                    </div>
                {:else if dataTab === "classrooms"}
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Classrooms</h2>
                            <EditableTable
                                columns={[
                                    {
                                        key: "id",
                                        label: "ID",
                                        type: "text",
                                        editable: false,
                                    },
                                    {
                                        key: "name",
                                        label: "Name",
                                        type: "text",
                                    },
                                    {
                                        key: "faculty",
                                        label: "Faculty",
                                        type: "text",
                                    },
                                    {
                                        key: "capacity",
                                        label: "Capacity",
                                        type: "number",
                                    },
                                    {
                                        key: "type",
                                        label: "Type",
                                        type: "select",
                                        options: [
                                            {
                                                value: "normal",
                                                label: "Normal",
                                            },
                                            {
                                                value: "computer_site",
                                                label: "Computer Site",
                                            },
                                            {
                                                value: "workshop",
                                                label: "Workshop",
                                            },
                                            {
                                                value: "gallery",
                                                label: "Gallery",
                                            },
                                        ],
                                    },
                                ]}
                                data={classrooms}
                                on:update={handleClassroomUpdate}
                                on:create={handleClassroomCreate}
                                on:delete={handleClassroomDelete}
                            />
                        </div>
                    </div>
                {:else if dataTab === "teachers"}
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <div class="flex justify-between items-center">
                                <h2 class="card-title">Teachers</h2>
                                <button
                                    class="btn btn-sm btn-outline"
                                    onclick={openLinkTeacherModal}
                                >
                                    Link Existing
                                </button>
                            </div>
                            <EditableTable
                                columns={[
                                    {
                                        key: "id",
                                        label: "ID",
                                        type: "text",
                                        editable: false,
                                    },
                                    {
                                        key: "name",
                                        label: "Name",
                                        type: "text",
                                    },
                                    {
                                        key: "available_slots",
                                        label: "Available Slots",
                                        type: "custom",
                                        component: TimeSlotModal,
                                        componentProps: { timeSlots },
                                    },
                                ]}
                                data={teachers}
                                on:update={handleTeacherUpdate}
                                on:create={handleTeacherCreate}
                                on:delete={handleTeacherDelete}
                            />
                        </div>
                    </div>
                {:else if dataTab === "courses"}
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <div class="flex justify-between items-center">
                                <h2 class="card-title">Courses</h2>
                                <button
                                    class="btn btn-sm btn-outline"
                                    onclick={openLinkCourseModal}
                                >
                                    Link Existing
                                </button>
                            </div>
                            <EditableTable
                                columns={[
                                    {
                                        key: "id",
                                        label: "ID",
                                        type: "text",
                                        editable: false,
                                    },
                                    {
                                        key: "name",
                                        label: "Name",
                                        type: "text",
                                    },
                                    {
                                        key: "units",
                                        label: "Units",
                                        type: "number",
                                    },
                                    {
                                        key: "required_room_type",
                                        label: "Req. Room Type",
                                        type: "select",
                                        options: [
                                            {
                                                value: "normal",
                                                label: "Normal",
                                            },
                                            {
                                                value: "computer_site",
                                                label: "Computer Site",
                                            },
                                            {
                                                value: "workshop",
                                                label: "Workshop",
                                            },
                                            {
                                                value: "gallery",
                                                label: "Gallery",
                                            },
                                        ],
                                    },
                                    {
                                        key: "min_population",
                                        label: "Min Pop",
                                        type: "number",
                                    },
                                    {
                                        key: "max_population",
                                        label: "Max Pop",
                                        type: "number",
                                    },
                                ]}
                                data={courses}
                                on:update={handleCourseUpdate}
                                on:create={handleCourseCreate}
                                on:delete={handleCourseDelete}
                            />
                        </div>
                    </div>
                {:else if dataTab === "groups"}
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Student Groups</h2>
                            <EditableTable
                                columns={[
                                    {
                                        key: "id",
                                        label: "ID",
                                        type: "text",
                                        editable: false,
                                    },
                                    {
                                        key: "name",
                                        label: "Name",
                                        type: "text",
                                    },
                                    {
                                        key: "population",
                                        label: "Population",
                                        type: "number",
                                    },
                                    {
                                        key: "degree",
                                        label: "Degree",
                                        type: "select",
                                        options: [
                                            {
                                                value: "bachelor",
                                                label: "Bachelor",
                                            },
                                            {
                                                value: "master",
                                                label: "Master",
                                            },
                                            { value: "phd", label: "PhD" },
                                            {
                                                value: "college",
                                                label: "College",
                                            },
                                        ],
                                    },
                                    {
                                        key: "allowed_days",
                                        label: "Allowed Days",
                                        type: "custom",
                                        component: DaySelector,
                                    },
                                    {
                                        key: "course_ids",
                                        label: "Courses",
                                        type: "custom",
                                        component: CourseSelector,
                                        componentProps: { courses },
                                    },
                                ]}
                                data={groups}
                                on:update={handleGroupUpdate}
                                on:create={handleGroupCreate}
                                on:delete={handleGroupDelete}
                            />
                        </div>
                    </div>
                {:else if dataTab === "lessons"}
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Lessons</h2>
                            <div class="overflow-x-auto">
                                <table class="table table-zebra w-full">
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>Course</th>
                                            <th>Group</th>
                                            <th>Teacher</th>
                                            <th>Duration</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {#each lessons as lesson}
                                            <tr>
                                                <td>{lesson.id}</td>
                                                <td>{lesson.course_name}</td>
                                                <td>{lesson.group_name}</td>
                                                <td>
                                                    {#if lesson.teacher_name}
                                                        {lesson.teacher_name}
                                                    {:else}
                                                        <span
                                                            class="badge badge-ghost"
                                                            >Dynamic</span
                                                        >
                                                    {/if}
                                                </td>
                                                <td>{lesson.duration_slots}</td>
                                            </tr>
                                        {/each}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                {/if}
            </div>
        </div>
    {/if}

    {#if activeTab === "solver"}
        <div class="card bg-base-100 shadow-xl max-w-2xl mx-auto">
            <div class="card-body">
                <h2 class="card-title">Solver Configuration</h2>

                <div class="form-control">
                    <label class="label" for="teacher-idle">
                        <span class="label-text"
                            >Teacher Idle Time Penalty (Weight: {weights.teacher_idle})</span
                        >
                    </label>
                    <input
                        id="teacher-idle"
                        type="range"
                        min="0"
                        max="10"
                        step="0.1"
                        class="range range-primary"
                        bind:value={weights.teacher_idle}
                    />
                </div>

                <div class="form-control">
                    <label class="label" for="student-idle">
                        <span class="label-text"
                            >Student Idle Time Penalty (Weight: {weights.student_idle})</span
                        >
                    </label>
                    <input
                        id="student-idle"
                        type="range"
                        min="0"
                        max="10"
                        step="0.1"
                        class="range range-secondary"
                        bind:value={weights.student_idle}
                    />
                </div>

                <div class="form-control">
                    <label class="label" for="student-compactness">
                        <span class="label-text"
                            >Student Compactness Reward (Weight: {weights.student_compactness})</span
                        >
                    </label>
                    <input
                        id="student-compactness"
                        type="range"
                        min="0"
                        max="10"
                        step="0.1"
                        class="range range-accent"
                        bind:value={weights.student_compactness}
                    />
                </div>

                <div class="form-control">
                    <label class="label" for="max-stagnant">
                        <span class="label-text"
                            >Max Stagnant Generations (Stop if no improvement)</span
                        >
                    </label>
                    <input
                        id="max-stagnant"
                        type="number"
                        min="10"
                        max="1000"
                        class="input input-bordered"
                        bind:value={maxStagnantGenerations}
                    />
                </div>

                <div class="divider"></div>

                {#if solverStatus === "idle" || solverStatus === "failed"}
                    <button class="btn btn-primary w-full" onclick={startSolver}
                        >Start Solver</button
                    >
                {:else if solverStatus === "running"}
                    <div class="flex flex-col items-center gap-2">
                        <span class="loading loading-spinner loading-lg"></span>
                        <p>Solving... Generation {solverProgress}</p>
                    </div>
                {:else if solverStatus === "completed"}
                    <div class="alert alert-success">
                        <span>Solver Completed Successfully!</span>
                        <button
                            class="btn btn-sm"
                            onclick={() => fetchResults(runId)}
                            >View Results</button
                        >
                    </div>
                {/if}

                <div class="divider">History</div>
                <div class="overflow-x-auto">
                    <table class="table table-zebra w-full">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Status</th>
                                <th>Score (Cost)</th>
                                <th>Satisfaction</th>
                                <th>Weights</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each solverRuns as run}
                                <tr>
                                    <td>{formatDate(run.start_time)}</td>
                                    <td>
                                        <span
                                            class="badge {run.status ===
                                            'completed'
                                                ? 'badge-success'
                                                : run.status === 'failed'
                                                  ? 'badge-error'
                                                  : 'badge-warning'}"
                                        >
                                            {run.status}
                                        </span>
                                    </td>
                                    <td>{run.fitness_score.toFixed(2)}</td>
                                    <td>
                                        <div class="flex items-center gap-2">
                                            <progress
                                                class="progress progress-success w-20"
                                                value={run.satisfaction_percentage}
                                                max="100"
                                            ></progress>
                                            <span
                                                >{run.satisfaction_percentage.toFixed(
                                                    1,
                                                )}%</span
                                            >
                                        </div>
                                    </td>
                                    <td>
                                        <div
                                            class="tooltip"
                                            data-tip={run.config_weights}
                                        >
                                            <button class="btn btn-xs btn-ghost"
                                                >View</button
                                            >
                                        </div>
                                    </td>
                                    <td>
                                        {#if run.status === "completed"}
                                            <button
                                                class="btn btn-xs btn-outline"
                                                onclick={() =>
                                                    fetchResults(run.run_id)}
                                                >View</button
                                            >
                                        {/if}
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    {/if}

    {#if activeTab === "results"}
        {#if currentRun}
            <div
                class="bg-base-100 p-4 rounded-lg shadow mb-4 grid grid-cols-1 md:grid-cols-4 gap-4"
            >
                <div class="stat">
                    <div class="stat-title">Fitness Score</div>
                    <div class="stat-value text-primary">
                        {currentRun.fitness_score.toFixed(2)}
                    </div>
                    <div class="stat-desc">Lower is better</div>
                </div>
                <div class="stat">
                    <div class="stat-title">Satisfaction</div>
                    <div class="stat-value text-success">
                        {currentRun.satisfaction_percentage.toFixed(1)}%
                    </div>
                    <div class="stat-desc">Higher is better</div>
                </div>
                <div class="stat col-span-2">
                    <div class="stat-title">Weights</div>
                    <div
                        class="stat-value text-sm font-normal whitespace-pre-wrap"
                    >
                        {currentRun.config_weights}
                    </div>
                </div>
            </div>
        {/if}
        <ScheduleGrid data={scheduleResults} />
    {/if}

    <!-- Link Teacher Modal -->
    {#if showLinkTeacherModal}
        <div class="modal modal-open">
            <div class="modal-box">
                <h3 class="font-bold text-lg">Link Existing Teacher</h3>
                <div class="py-4">
                    {#if globalTeachers.length === 0}
                        <p>No unlinked teachers found.</p>
                    {:else}
                        <ul class="menu bg-base-200 rounded-box">
                            {#each globalTeachers as teacher}
                                <li>
                                    <button
                                        onclick={() =>
                                            handleLinkTeacher(teacher.id)}
                                    >
                                        {teacher.name}
                                    </button>
                                </li>
                            {/each}
                        </ul>
                    {/if}
                </div>
                <div class="modal-action">
                    <button
                        class="btn"
                        onclick={() => (showLinkTeacherModal = false)}
                        >Close</button
                    >
                </div>
            </div>
        </div>
    {/if}

    <!-- Link Course Modal -->
    {#if showLinkCourseModal}
        <div class="modal modal-open">
            <div class="modal-box">
                <h3 class="font-bold text-lg">Link Existing Course</h3>
                <div class="py-4">
                    {#if globalCourses.length === 0}
                        <p>No unlinked courses found.</p>
                    {:else}
                        <ul class="menu bg-base-200 rounded-box">
                            {#each globalCourses as course}
                                <li>
                                    <button
                                        onclick={() =>
                                            handleLinkCourse(course.id)}
                                    >
                                        {course.name}
                                    </button>
                                </li>
                            {/each}
                        </ul>
                    {/if}
                </div>
                <div class="modal-action">
                    <button
                        class="btn"
                        onclick={() => (showLinkCourseModal = false)}
                        >Close</button
                    >
                </div>
            </div>
        </div>
    {/if}
</div>
