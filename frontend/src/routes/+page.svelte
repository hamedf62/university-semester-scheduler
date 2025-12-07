<script lang="ts">
    import FileUpload from "../components/FileUpload.svelte";
    import ScheduleGrid from "../components/ScheduleGrid.svelte";

    // Mock data for now
    let scheduleData = $state([
        {
            day: 0,
            slot: 0,
            lessonName: "Math 101",
            teacherName: "Dr. Smith",
            roomName: "Room 101",
        },
        {
            day: 1,
            slot: 2,
            lessonName: "Physics",
            teacherName: "Dr. Jones",
            roomName: "Lab 2",
        },
    ]);

    let weights = $state({
        teacherGaps: 1.0,
        studentCompactness: 1.0,
        studentGaps: 1.0,
    });

    async function runSolver() {
        // Call API to run solver with weights
        console.log("Running solver with weights:", weights);
    }
</script>

<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
    <div class="col-span-1 space-y-4">
        <FileUpload />

        <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
                <h2 class="card-title">Solver Settings</h2>

                <div class="form-control">
                    <label class="label">
                        <span class="label-text">Teacher Gaps Penalty</span>
                    </label>
                    <input
                        type="range"
                        min="0"
                        max="10"
                        bind:value={weights.teacherGaps}
                        class="range range-xs"
                    />
                </div>

                <div class="form-control">
                    <label class="label">
                        <span class="label-text"
                            >Student Compactness Reward</span
                        >
                    </label>
                    <input
                        type="range"
                        min="0"
                        max="10"
                        bind:value={weights.studentCompactness}
                        class="range range-xs"
                    />
                </div>

                <div class="card-actions justify-end mt-4">
                    <button class="btn btn-secondary w-full" onclick={runSolver}
                        >Run Solver</button
                    >
                </div>
            </div>
        </div>
    </div>

    <div class="col-span-3">
        <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
                <h2 class="card-title">Schedule View</h2>
                <ScheduleGrid schedule={scheduleData} />
            </div>
        </div>
    </div>
</div>
