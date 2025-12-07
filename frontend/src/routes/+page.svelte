<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { getProjects, createProject, type Project } from "$lib/api";
    import { formatDate } from "$lib/utils";

    let projects: Project[] = $state([]);
    let isModalOpen = $state(false);

    // Form state
    let newProjectName = $state("");
    let newProjectDescription = $state("");

    async function loadData() {
        try {
            projects = await getProjects();
        } catch (e) {
            console.error("Failed to load data", e);
        }
    }

    async function handleCreateProject() {
        try {
            if (newProjectName) {
                await createProject(newProjectName, newProjectDescription);
                isModalOpen = false;
                loadData();
                // Reset form
                newProjectName = "";
                newProjectDescription = "";
            }
        } catch (e) {
            console.error("Failed to create project", e);
            alert("Failed to create project. Check console for details.");
        }
    }

    function handleBackdropClick(e: MouseEvent) {
        if (e.target === e.currentTarget) {
            isModalOpen = false;
        }
    }

    onMount(() => {
        loadData();
    });
</script>

<div class="container mx-auto p-4">
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold">Semester Projects</h1>
        <button class="btn btn-primary" onclick={() => (isModalOpen = true)}>
            New Project
        </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each projects as project}
            <button
                class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow cursor-pointer text-left w-full"
                onclick={() => goto(`/project/${project.id}`)}
            >
                <div class="card-body">
                    <h2 class="card-title">{project.name}</h2>
                    {#if project.description}
                        <p>{project.description}</p>
                    {/if}
                    <p class="text-sm text-gray-500">ID: {project.id}</p>
                    {#if project.created_at}
                        <p class="text-xs text-gray-400">
                            Created: {formatDate(project.created_at)}
                        </p>
                    {/if}
                    <p>Status: {project.is_active ? "Active" : "Inactive"}</p>
                    <div class="card-actions justify-end">
                        <div class="btn btn-sm btn-ghost">Open</div>
                    </div>
                </div>
            </button>
        {/each}
    </div>

    <!-- Create Modal -->
    {#if isModalOpen}
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div class="modal modal-open" onclick={handleBackdropClick}>
            <div class="modal-box">
                <h3 class="font-bold text-lg">Create New Project</h3>

                <div class="form-control w-full mt-4">
                    <label class="label" for="project-name">
                        <span class="label-text">Project Name</span>
                    </label>
                    <input
                        id="project-name"
                        type="text"
                        placeholder="e.g. Semester 1403-1"
                        class="input input-bordered w-full"
                        bind:value={newProjectName}
                    />
                </div>

                <div class="form-control w-full mt-4">
                    <label class="label" for="project-desc">
                        <span class="label-text">Description (Optional)</span>
                    </label>
                    <textarea
                        id="project-desc"
                        class="textarea textarea-bordered h-24"
                        placeholder="Project description..."
                        bind:value={newProjectDescription}
                    ></textarea>
                </div>

                <div class="modal-action">
                    <button class="btn" onclick={() => (isModalOpen = false)}
                        >Cancel</button
                    >
                    <button
                        class="btn btn-primary"
                        onclick={handleCreateProject}
                        disabled={!newProjectName}
                    >
                        Create
                    </button>
                </div>
            </div>
        </div>
    {/if}
</div>
