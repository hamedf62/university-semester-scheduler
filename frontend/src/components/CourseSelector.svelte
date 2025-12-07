<script lang="ts">
    import { createEventDispatcher } from "svelte";

    export let value: number[] = []; // Array of Course IDs
    export let courses: any[] = []; // Passed from parent

    const dispatch = createEventDispatcher();
    let isOpen = false;
    let searchTerm = "";

    function toggleCourse(id: number) {
        let newSelection;
        if (value.includes(id)) {
            newSelection = value.filter((v) => v !== id);
        } else {
            newSelection = [...value, id];
        }
        value = newSelection;
        dispatch("change", value);
    }

    $: filteredCourses = courses.filter((c) =>
        c.name.toLowerCase().includes(searchTerm.toLowerCase()),
    );
</script>

<div>
    <div
        class="flex flex-wrap gap-1 mb-2 cursor-pointer"
        on:click={() => (isOpen = true)}
        role="button"
        tabindex="0"
        on:keypress={(e) => e.key === "Enter" && (isOpen = true)}
    >
        {#if value && value.length > 0}
            <span class="badge badge-primary badge-sm"
                >{value.length} Courses</span
            >
        {:else}
            <span class="text-xs opacity-50">No courses selected</span>
        {/if}
    </div>
    <button
        class="btn btn-xs btn-outline w-full"
        on:click={() => (isOpen = true)}
    >
        Edit Courses
    </button>

    {#if isOpen}
        <div
            class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
            on:click|self={() => (isOpen = false)}
            on:keydown={(e) => e.key === "Escape" && (isOpen = false)}
            role="dialog"
            tabindex="-1"
        >
            <div
                class="bg-base-100 p-6 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
                <h3 class="text-lg font-bold mb-4">Select Courses</h3>
                <input
                    type="text"
                    placeholder="Search courses..."
                    class="input input-bordered w-full mb-4"
                    bind:value={searchTerm}
                />
                <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {#each filteredCourses as course}
                        <label
                            class="label cursor-pointer justify-start gap-2 border rounded p-2 hover:bg-base-200"
                        >
                            <input
                                type="checkbox"
                                class="checkbox checkbox-sm"
                                checked={value.includes(course.id)}
                                on:change={() => toggleCourse(course.id)}
                            />
                            <span class="label-text"
                                >{course.name} ({course.units} units)</span
                            >
                        </label>
                    {/each}
                </div>
                <div class="modal-action mt-6">
                    <button
                        class="btn btn-primary"
                        on:click={() => (isOpen = false)}>Done</button
                    >
                </div>
            </div>
        </div>
    {/if}
</div>
