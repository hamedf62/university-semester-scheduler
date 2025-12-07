<script lang="ts">
    let { data }: { data: any[] } = $props();

    const days = [
        "Saturday",
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
    ];
    const slots = [
        "08:00-10:00",
        "10:00-12:00",
        "12:00-14:00",
        "14:00-16:00",
        "16:00-18:00",
    ];

    let viewMode = $state("odd"); // 'odd' or 'even'

    // Filters
    let selectedTeacher = $state("");
    let selectedGroup = $state("");
    let selectedRoom = $state("");

    // Derived lists for dropdowns
    let teachers = $derived(
        [...new Set(data.map((d) => d.teacher_name))].sort(),
    );
    let groups = $derived([...new Set(data.map((d) => d.group_name))].sort());
    let rooms = $derived([...new Set(data.map((d) => d.room_name))].sort());

    // Helper to find lessons in slot for the current view mode & filters
    function getLessons(dayIdx: number, slotIdx: number) {
        if (!data) return [];

        return data.filter((s: any) => {
            // Check Day & Slot
            if (s.day !== dayIdx || s.slot !== slotIdx) return false;

            // Check Parity
            if (s.week_parity !== "both" && s.week_parity !== viewMode)
                return false;

            // Check Filters
            if (selectedTeacher && s.teacher_name !== selectedTeacher)
                return false;
            if (selectedGroup && s.group_name !== selectedGroup) return false;
            if (selectedRoom && s.room_name !== selectedRoom) return false;

            return true;
        });
    }

    function clearFilters() {
        selectedTeacher = "";
        selectedGroup = "";
        selectedRoom = "";
    }
</script>

<div class="flex flex-col gap-4 mb-6">
    <!-- Controls -->
    <div class="flex flex-wrap gap-4 items-end bg-base-200 p-4 rounded-lg">
        <div class="form-control w-full max-w-xs">
            <span class="label-text mb-2">Week Parity</span>
            <div class="join">
                <button
                    class="join-item btn btn-sm"
                    class:btn-active={viewMode === "odd"}
                    onclick={() => (viewMode = "odd")}>Odd</button
                >
                <button
                    class="join-item btn btn-sm"
                    class:btn-active={viewMode === "even"}
                    onclick={() => (viewMode = "even")}>Even</button
                >
            </div>
        </div>

        <div class="form-control w-full max-w-xs">
            <label class="label" for="filter-teacher"
                ><span class="label-text">Filter by Teacher</span></label
            >
            <select
                id="filter-teacher"
                class="select select-bordered select-sm"
                bind:value={selectedTeacher}
            >
                <option value="">All Teachers</option>
                {#each teachers as t}
                    <option value={t}>{t}</option>
                {/each}
            </select>
        </div>

        <div class="form-control w-full max-w-xs">
            <label class="label" for="filter-group"
                ><span class="label-text">Filter by Group</span></label
            >
            <select
                id="filter-group"
                class="select select-bordered select-sm"
                bind:value={selectedGroup}
            >
                <option value="">All Groups</option>
                {#each groups as g}
                    <option value={g}>{g}</option>
                {/each}
            </select>
        </div>

        <div class="form-control w-full max-w-xs">
            <label class="label" for="filter-room"
                ><span class="label-text">Filter by Room</span></label
            >
            <select
                id="filter-room"
                class="select select-bordered select-sm"
                bind:value={selectedRoom}
            >
                <option value="">All Rooms</option>
                {#each rooms as r}
                    <option value={r}>{r}</option>
                {/each}
            </select>
        </div>

        <button class="btn btn-sm btn-ghost" onclick={clearFilters}
            >Clear Filters</button
        >
    </div>
</div>

<div class="overflow-x-auto">
    <table class="table table-zebra w-full border text-center table-fixed">
        <thead>
            <tr>
                <th class="bg-base-300 w-24">Time / Day</th>
                {#each days as day}
                    <th class="bg-base-300 text-lg">{day}</th>
                {/each}
            </tr>
        </thead>
        <tbody>
            {#each slots as slot, slotIdx}
                <tr>
                    <td class="font-bold bg-base-200 align-middle">{slot}</td>
                    {#each days as day, dayIdx}
                        {@const lessons = getLessons(dayIdx, slotIdx)}
                        <td
                            class="border p-1 align-top h-32 relative group hover:bg-base-100 transition-colors"
                        >
                            <div
                                class="flex flex-col gap-1 h-full overflow-y-auto max-h-48"
                            >
                                {#each lessons as lesson}
                                    <div
                                        class="card bg-primary text-primary-content shadow-sm p-2 text-left text-xs hover:scale-105 transition-transform cursor-default"
                                    >
                                        <div
                                            class="font-bold truncate"
                                            title={lesson.course_name}
                                        >
                                            {lesson.course_name}
                                        </div>
                                        <div
                                            class="opacity-90 truncate"
                                            title={lesson.teacher_name}
                                        >
                                            👨‍🏫 {lesson.teacher_name}
                                        </div>
                                        <div
                                            class="opacity-90 truncate"
                                            title={lesson.group_name}
                                        >
                                            👥 {lesson.group_name}
                                        </div>
                                        <div
                                            class="opacity-90 truncate"
                                            title={lesson.room_name}
                                        >
                                            📍 {lesson.room_name}
                                        </div>
                                        {#if lesson.week_parity !== "both"}
                                            <div
                                                class="badge badge-secondary badge-xs mt-1"
                                            >
                                                {lesson.week_parity}
                                            </div>
                                        {/if}
                                    </div>
                                {/each}
                            </div>
                        </td>
                    {/each}
                </tr>
            {/each}
        </tbody>
    </table>
</div>
