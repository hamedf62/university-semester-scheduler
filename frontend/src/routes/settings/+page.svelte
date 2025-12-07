<script lang="ts">
    import { onMount } from "svelte";
    import { formatDate } from "$lib/utils";
    import {
        getTeachers,
        getCourses,
        getStudentGroups,
        getClassrooms,
        createTeacher,
        updateTeacher,
        deleteTeacher,
        createCourse,
        updateCourse,
        deleteCourse,
        createStudentGroup,
        updateStudentGroup,
        deleteStudentGroup,
        createClassroom,
        updateClassroom,
        deleteClassroom,
        addTeacherCourseLink,
        removeTeacherCourseLink,
        type Teacher,
        type Course,
        type StudentGroup,
        type Classroom,
    } from "$lib/api";

    let teachers: Teacher[] = [];
    let courses: Course[] = [];
    let groups: StudentGroup[] = [];
    let classrooms: Classroom[] = [];
    let activeTab: "teachers" | "courses" | "groups" | "classrooms" =
        "teachers";

    // Pagination & Search
    let page = 1;
    let size = 10;
    let search = "";
    let total = 0;

    // Teacher Form
    let showTeacherModal = false;
    let editingTeacher: Teacher | null = null;
    let teacherForm = { name: "", course_ids: [] as number[] };

    // Course Form
    let showCourseModal = false;
    let editingCourse: Course | null = null;
    let courseForm = { name: "", units: 2, required_room_type: "normal" };

    // Group Form
    let showGroupModal = false;
    let editingGroup: StudentGroup | null = null;
    let groupForm = {
        name: "",
        degree: "bachelor",
        population: 30,
        allowed_days: "",
    };

    // Classroom Form
    let showClassroomModal = false;
    let editingClassroom: Classroom | null = null;
    let classroomForm = { name: "", faculty: "", capacity: 30, type: "normal" };

    onMount(async () => {
        await loadData();
    });

    async function loadData() {
        if (activeTab === "teachers") {
            const res = await getTeachers(undefined, page, size, search);
            teachers = res.items;
            total = res.total;
        } else if (activeTab === "courses") {
            const res = await getCourses(undefined, page, size, search);
            courses = res.items;
            total = res.total;
        } else if (activeTab === "groups") {
            const res = await getStudentGroups(undefined, page, size, search);
            groups = res.items;
            total = res.total;
        } else if (activeTab === "classrooms") {
            const res = await getClassrooms(undefined, page, size, search);
            classrooms = res.items;
            total = res.total;
        }
    }

    function handleTabChange(tab: typeof activeTab) {
        activeTab = tab;
        page = 1;
        search = "";
        loadData();
    }

    function handleSearch() {
        page = 1;
        loadData();
    }

    function handlePageChange(newPage: number) {
        if (newPage < 1 || newPage > Math.ceil(total / size)) return;
        page = newPage;
        loadData();
    }

    // Teacher Actions
    function openTeacherModal(teacher?: Teacher) {
        editingTeacher = teacher || null;
        teacherForm = teacher
            ? { name: teacher.name, course_ids: [...teacher.course_ids] }
            : { name: "", course_ids: [] };
        showTeacherModal = true;
    }

    async function saveTeacher() {
        if (editingTeacher) {
            // Update basic info
            await updateTeacher(editingTeacher.id, { name: teacherForm.name });

            // Update course links (naive approach: remove all and add selected)
            // Better approach: diff
            const currentIds = new Set(editingTeacher.course_ids);
            const newIds = new Set(teacherForm.course_ids);

            // Add new
            for (const id of newIds) {
                if (!currentIds.has(id))
                    await addTeacherCourseLink(editingTeacher.id, id);
            }
            // Remove old
            for (const id of currentIds) {
                if (!newIds.has(id))
                    await removeTeacherCourseLink(editingTeacher.id, id);
            }
        } else {
            const newTeacher = await createTeacher({ name: teacherForm.name });
            // Add course links
            for (const id of teacherForm.course_ids) {
                await addTeacherCourseLink(newTeacher.id, id);
            }
        }
        showTeacherModal = false;
        await loadData();
    }

    async function removeTeacher(id: number) {
        if (confirm("Are you sure?")) {
            await deleteTeacher(id);
            await loadData();
        }
    }

    // Course Actions
    async function saveCourse() {
        if (editingCourse) {
            await updateCourse(editingCourse.id, courseForm);
        } else {
            await createCourse(courseForm);
        }
        showCourseModal = false;
        editingCourse = null;
        courseForm = { name: "", units: 2, required_room_type: "normal" };
        await loadData();
    }

    function openCourseModal(course?: Course) {
        if (course) {
            editingCourse = course;
            courseForm = {
                name: course.name,
                units: course.units,
                required_room_type: course.required_room_type,
            };
        } else {
            editingCourse = null;
            courseForm = { name: "", units: 2, required_room_type: "normal" };
        }
        showCourseModal = true;
    }

    async function removeCourse(id: number) {
        if (confirm("Are you sure?")) {
            await deleteCourse(id);
            await loadData();
        }
    }

    // Group Actions
    async function saveGroup() {
        if (editingGroup) {
            await updateStudentGroup(editingGroup.id, groupForm);
        } else {
            await createStudentGroup(groupForm);
        }
        showGroupModal = false;
        editingGroup = null;
        groupForm = {
            name: "",
            degree: "bachelor",
            population: 30,
            allowed_days: "",
        };
        await loadData();
    }

    function openGroupModal(group?: StudentGroup) {
        if (group) {
            editingGroup = group;
            groupForm = {
                name: group.name,
                degree: group.degree,
                population: group.population,
                allowed_days: group.allowed_days || "",
            };
        } else {
            editingGroup = null;
            groupForm = {
                name: "",
                degree: "bachelor",
                population: 30,
                allowed_days: "",
            };
        }
        showGroupModal = true;
    }

    async function removeGroup(id: number) {
        if (confirm("Are you sure?")) {
            await deleteStudentGroup(id);
            await loadData();
        }
    }

    // Classroom Actions
    async function saveClassroom() {
        if (editingClassroom) {
            await updateClassroom(editingClassroom.id, classroomForm);
        } else {
            await createClassroom(classroomForm);
        }
        showClassroomModal = false;
        editingClassroom = null;
        classroomForm = { name: "", faculty: "", capacity: 30, type: "normal" };
        await loadData();
    }

    function openClassroomModal(classroom?: Classroom) {
        if (classroom) {
            editingClassroom = classroom;
            classroomForm = {
                name: classroom.name,
                faculty: classroom.faculty,
                capacity: classroom.capacity,
                type: classroom.type,
            };
        } else {
            editingClassroom = null;
            classroomForm = {
                name: "",
                faculty: "",
                capacity: 30,
                type: "normal",
            };
        }
        showClassroomModal = true;
    }

    async function removeClassroom(id: number) {
        if (confirm("Are you sure?")) {
            await deleteClassroom(id);
            await loadData();
        }
    }

    function toggleCourseSelection(courseId: number) {
        const index = teacherForm.course_ids.indexOf(courseId);
        if (index === -1) {
            teacherForm.course_ids = [...teacherForm.course_ids, courseId];
        } else {
            teacherForm.course_ids = teacherForm.course_ids.filter(
                (id) => id !== courseId,
            );
        }
    }
</script>

<div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Global Settings</h1>

    <div class="flex border-b mb-4">
        <button
            class="px-4 py-2 {activeTab === 'teachers'
                ? 'border-b-2 border-blue-500 font-bold'
                : ''}"
            on:click={() => handleTabChange("teachers")}
        >
            Teachers
        </button>
        <button
            class="px-4 py-2 {activeTab === 'courses'
                ? 'border-b-2 border-blue-500 font-bold'
                : ''}"
            on:click={() => handleTabChange("courses")}
        >
            Courses
        </button>
        <button
            class="px-4 py-2 {activeTab === 'groups'
                ? 'border-b-2 border-blue-500 font-bold'
                : ''}"
            on:click={() => handleTabChange("groups")}
        >
            Student Groups
        </button>
        <button
            class="px-4 py-2 {activeTab === 'classrooms'
                ? 'border-b-2 border-blue-500 font-bold'
                : ''}"
            on:click={() => handleTabChange("classrooms")}
        >
            Classrooms
        </button>
    </div>

    <div class="flex justify-between items-center mb-4">
        <div class="flex space-x-2">
            <input
                type="text"
                placeholder="Search..."
                class="border p-2 rounded"
                bind:value={search}
                on:input={() => handleSearch()}
            />
        </div>
        <div class="flex space-x-2 items-center">
            <button
                class="px-3 py-1 border rounded disabled:opacity-50"
                disabled={page === 1}
                on:click={() => handlePageChange(page - 1)}>Prev</button
            >
            <span>Page {page} of {Math.ceil(total / size) || 1}</span>
            <button
                class="px-3 py-1 border rounded disabled:opacity-50"
                disabled={page >= (Math.ceil(total / size) || 1)}
                on:click={() => handlePageChange(page + 1)}>Next</button
            >
        </div>
    </div>

    {#if activeTab === "teachers"}
        <div class="mb-4">
            <button
                class="bg-blue-500 text-white px-4 py-2 rounded"
                on:click={() => openTeacherModal()}
            >
                Add Teacher
            </button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each teachers as teacher}
                <div class="border p-4 rounded shadow">
                    <div class="flex justify-between items-start">
                        <h3 class="font-bold text-lg">{teacher.name}</h3>
                        <button
                            class="text-red-500"
                            on:click={() => removeTeacher(teacher.id)}
                            >Delete</button
                        >
                    </div>
                    <div class="mt-2 text-sm text-gray-600">
                        <p>Can teach: {teacher.course_ids.length} courses</p>
                        {#if teacher.created_at}
                            <p class="text-xs text-gray-400 mt-1">
                                Created: {formatDate(teacher.created_at)}
                            </p>
                        {/if}
                        {#if teacher.updated_at}
                            <p class="text-xs text-gray-400">
                                Updated: {formatDate(teacher.updated_at)}
                            </p>
                        {/if}
                        <div class="flex flex-wrap gap-1 mt-1">
                            {#each teacher.course_ids as cid}
                                <span
                                    class="bg-gray-200 px-2 py-0.5 rounded text-xs"
                                >
                                    {courses.find((c) => c.id === cid)?.name ||
                                        cid}
                                </span>
                            {/each}
                        </div>
                    </div>
                    <button
                        class="mt-4 text-blue-500 text-sm"
                        on:click={() => openTeacherModal(teacher)}>Edit</button
                    >
                </div>
            {/each}
        </div>
    {:else if activeTab === "courses"}
        <div class="mb-4">
            <button
                class="bg-blue-500 text-white px-4 py-2 rounded"
                on:click={() => openCourseModal()}
            >
                Add Course
            </button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each courses as course}
                <div class="border p-4 rounded shadow">
                    <div class="flex justify-between items-start">
                        <h3 class="font-bold text-lg">{course.name}</h3>
                        <button
                            class="text-red-500"
                            on:click={() => removeCourse(course.id)}
                            >Delete</button
                        >
                    </div>
                    <p class="text-sm">Units: {course.units}</p>
                    <p class="text-sm">Room: {course.required_room_type}</p>
                    {#if course.created_at}
                        <p class="text-xs text-gray-400 mt-1">
                            Created: {formatDate(course.created_at)}
                        </p>
                    {/if}
                    {#if course.updated_at}
                        <p class="text-xs text-gray-400">
                            Updated: {formatDate(course.updated_at)}
                        </p>
                    {/if}
                    <button
                        class="mt-4 text-blue-500 text-sm"
                        on:click={() => openCourseModal(course)}>Edit</button
                    >
                </div>
            {/each}
        </div>
    {:else if activeTab === "groups"}
        <div class="mb-4">
            <button
                class="bg-blue-500 text-white px-4 py-2 rounded"
                on:click={() => openGroupModal()}
            >
                Add Student Group
            </button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each groups as group}
                <div class="border p-4 rounded shadow">
                    <div class="flex justify-between items-start">
                        <h3 class="font-bold text-lg">{group.name}</h3>
                        <button
                            class="text-red-500"
                            on:click={() => removeGroup(group.id)}
                            >Delete</button
                        >
                    </div>
                    <p class="text-sm">Degree: {group.degree}</p>
                    <p class="text-sm">Population: {group.population}</p>
                    {#if group.created_at}
                        <p class="text-xs text-gray-400 mt-1">
                            Created: {formatDate(group.created_at)}
                        </p>
                    {/if}
                    {#if group.updated_at}
                        <p class="text-xs text-gray-400">
                            Updated: {formatDate(group.updated_at)}
                        </p>
                    {/if}
                    <button
                        class="mt-4 text-blue-500 text-sm"
                        on:click={() => openGroupModal(group)}>Edit</button
                    >
                </div>
            {/each}
        </div>
    {:else if activeTab === "classrooms"}
        <div class="mb-4">
            <button
                class="bg-blue-500 text-white px-4 py-2 rounded"
                on:click={() => openClassroomModal()}
            >
                Add Classroom
            </button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each classrooms as classroom}
                <div class="border p-4 rounded shadow">
                    <div class="flex justify-between items-start">
                        <h3 class="font-bold text-lg">{classroom.name}</h3>
                        <button
                            class="text-red-500"
                            on:click={() => removeClassroom(classroom.id)}
                            >Delete</button
                        >
                    </div>
                    <p class="text-sm">Faculty: {classroom.faculty}</p>
                    <p class="text-sm">Capacity: {classroom.capacity}</p>
                    {#if classroom.created_at}
                        <p class="text-xs text-gray-400 mt-1">
                            Created: {formatDate(classroom.created_at)}
                        </p>
                    {/if}
                    {#if classroom.updated_at}
                        <p class="text-xs text-gray-400">
                            Updated: {formatDate(classroom.updated_at)}
                        </p>
                    {/if}
                    <p class="text-sm">Type: {classroom.type}</p>
                    <button
                        class="mt-4 text-blue-500 text-sm"
                        on:click={() => openClassroomModal(classroom)}
                        >Edit</button
                    >
                </div>
            {/each}
        </div>
    {/if}

    <!-- Teacher Modal -->
    {#if showTeacherModal}
        <div
            class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
        >
            <div
                class="bg-white p-6 rounded w-full max-w-lg max-h-[90vh] overflow-y-auto"
            >
                <h2 class="text-xl font-bold mb-4">
                    {editingTeacher ? "Edit" : "Add"} Teacher
                </h2>
                <div class="mb-4">
                    <label class="block text-sm font-bold mb-1">Name</label>
                    <input
                        type="text"
                        class="border w-full p-2 rounded"
                        bind:value={teacherForm.name}
                    />
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-bold mb-1"
                        >Capable Courses</label
                    >
                    <div
                        class="border p-2 rounded max-h-40 overflow-y-auto grid grid-cols-2 gap-2"
                    >
                        {#each courses as course}
                            <label class="flex items-center space-x-2">
                                <input
                                    type="checkbox"
                                    checked={teacherForm.course_ids.includes(
                                        course.id,
                                    )}
                                    on:change={() =>
                                        toggleCourseSelection(course.id)}
                                />
                                <span class="text-sm">{course.name}</span>
                            </label>
                        {/each}
                    </div>
                </div>
                <div class="flex justify-end space-x-2">
                    <button
                        class="px-4 py-2 border rounded"
                        on:click={() => (showTeacherModal = false)}
                        >Cancel</button
                    >
                    <button
                        class="px-4 py-2 bg-blue-500 text-white rounded"
                        on:click={saveTeacher}>Save</button
                    >
                </div>
            </div>
        </div>
    {/if}

    <!-- Course Modal -->
    {#if showCourseModal}
        <div
            class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
        >
            <div class="bg-white p-6 rounded w-full max-w-md">
                <h2 class="text-xl font-bold mb-4">
                    {editingCourse ? "Edit" : "Add"} Course
                </h2>
                <div class="mb-4">
                    <label class="block text-sm font-bold mb-1">Name</label>
                    <input
                        type="text"
                        class="border w-full p-2 rounded"
                        bind:value={courseForm.name}
                    />
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-bold mb-1">Units</label>
                    <input
                        type="number"
                        class="border w-full p-2 rounded"
                        bind:value={courseForm.units}
                    />
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-bold mb-1">Room Type</label
                    >
                    <select
                        class="border w-full p-2 rounded"
                        bind:value={courseForm.required_room_type}
                    >
                        <option value="normal">Normal</option>
                        <option value="computer_site">Computer Site</option>
                        <option value="gallery">Gallery</option>
                        <option value="workshop">Workshop</option>
                    </select>
                </div>
                <div class="flex justify-end space-x-2">
                    <button
                        class="px-4 py-2 border rounded"
                        on:click={() => (showCourseModal = false)}
                        >Cancel</button
                    >
                    <button
                        class="px-4 py-2 bg-blue-500 text-white rounded"
                        on:click={saveCourse}>Save</button
                    >
                </div>
            </div>
        </div>
    {/if}

    <!-- Group Modal -->
    {#if showGroupModal}
        <div
            class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
        >
            <div class="bg-white p-6 rounded w-full max-w-md">
                <h2 class="text-xl font-bold mb-4">
                    {editingGroup ? "Edit" : "Add"} Student Group
                </h2>
                <div class="mb-4">
                    <label class="block text-sm font-bold mb-1">Name</label>
                    <input
                        type="text"
                        class="border w-full p-2 rounded"
                        bind:value={groupForm.name}
                    />
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-bold mb-1">Degree</label>
                    <select
                        class="border w-full p-2 rounded"
                        bind:value={groupForm.degree}
                    >
                        <option value="bachelor">Bachelor</option>
                        <option value="master">Master</option>
                        <option value="phd">PhD</option>
                    </select>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-bold mb-1"
                        >Population</label
                    >
                    <input
                        type="number"
                        class="border w-full p-2 rounded"
                        bind:value={groupForm.population}
                    />
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-bold mb-1"
                        >Allowed Days</label
                    >
                    <input
                        type="text"
                        class="border w-full p-2 rounded"
                        bind:value={groupForm.allowed_days}
                        placeholder="e.g. Mon,Tue,Wed"
                    />
                </div>
                <div class="flex justify-end space-x-2">
                    <button
                        class="px-4 py-2 border rounded"
                        on:click={() => (showGroupModal = false)}>Cancel</button
                    >
                    <button
                        class="px-4 py-2 bg-blue-500 text-white rounded"
                        on:click={saveGroup}>Save</button
                    >
                </div>
            </div>
        </div>
    {/if}

    <!-- Classroom Modal -->
    {#if showClassroomModal}
        <div
            class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
        >
            <div class="bg-white p-6 rounded w-full max-w-md">
                <h2 class="text-xl font-bold mb-4">
                    {editingClassroom ? "Edit" : "Add"} Classroom
                </h2>
                <div class="mb-4">
                    <label class="block text-sm font-bold mb-1">Name</label>
                    <input
                        type="text"
                        class="border w-full p-2 rounded"
                        bind:value={classroomForm.name}
                    />
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-bold mb-1">Faculty</label>
                    <input
                        type="text"
                        class="border w-full p-2 rounded"
                        bind:value={classroomForm.faculty}
                    />
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-bold mb-1">Capacity</label>
                    <input
                        type="number"
                        class="border w-full p-2 rounded"
                        bind:value={classroomForm.capacity}
                    />
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-bold mb-1">Type</label>
                    <select
                        class="border w-full p-2 rounded"
                        bind:value={classroomForm.type}
                    >
                        <option value="normal">Normal</option>
                        <option value="computer_site">Computer Site</option>
                        <option value="gallery">Gallery</option>
                        <option value="workshop">Workshop</option>
                    </select>
                </div>
                <div class="flex justify-end space-x-2">
                    <button
                        class="px-4 py-2 border rounded"
                        on:click={() => (showClassroomModal = false)}
                        >Cancel</button
                    >
                    <button
                        class="px-4 py-2 bg-blue-500 text-white rounded"
                        on:click={saveClassroom}>Save</button
                    >
                </div>
            </div>
        </div>
    {/if}
</div>
