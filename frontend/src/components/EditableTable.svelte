<script lang="ts">
    import { createEventDispatcher } from "svelte";

    export let columns: {
        key: string;
        label: string;
        type: "text" | "number" | "select" | "custom";
        options?: { value: string | number; label: string }[];
        editable?: boolean;
        component?: any; // For custom type
        componentProps?: any;
    }[] = [];
    export let data: any[] = [];

    const dispatch = createEventDispatcher();

    function handleUpdate(row: any, key: string, value: any) {
        // Only dispatch if value changed
        // Deep compare for arrays/objects if needed, but simple ref check is ok for now
        if (row[key] !== value) {
            const updatedRow = { ...row, [key]: value };
            dispatch("update", updatedRow);
        }
    }

    function handleCreate() {
        dispatch("create");
    }

    function handleDelete(row: any) {
        if (confirm("Are you sure you want to delete this item?")) {
            dispatch("delete", row);
        }
    }
</script>

<div class="overflow-x-auto bg-base-100 rounded-lg shadow">
    <table class="table table-zebra w-full">
        <thead>
            <tr>
                {#each columns as col}
                    <th class="bg-base-200 text-base-content font-bold"
                        >{col.label}</th
                    >
                {/each}
                <th class="bg-base-200 w-16">Actions</th>
            </tr>
        </thead>
        <tbody>
            {#each data as row (row.id || Math.random())}
                <tr class="hover">
                    {#each columns as col}
                        <td class="p-2">
                            {#if col.editable === false}
                                <span class="opacity-70">{row[col.key]}</span>
                            {:else if col.type === "custom" && col.component}
                                <div class="w-full">
                                    <svelte:component
                                        this={col.component}
                                        {...col.componentProps}
                                        value={row[col.key]}
                                        on:change={(e: CustomEvent) =>
                                            handleUpdate(
                                                row,
                                                col.key,
                                                e.detail,
                                            )}
                                    />
                                </div>
                            {:else if col.type === "select"}
                                <select
                                    class="select select-bordered select-sm w-full max-w-xs"
                                    value={row[col.key]}
                                    on:change={(e) =>
                                        handleUpdate(
                                            row,
                                            col.key,
                                            e.currentTarget.value,
                                        )}
                                >
                                    {#each col.options || [] as opt}
                                        <option value={opt.value}
                                            >{opt.label}</option
                                        >
                                    {/each}
                                </select>
                            {:else if col.type === "number"}
                                <input
                                    type="number"
                                    class="input input-bordered input-sm w-full"
                                    value={row[col.key]}
                                    on:blur={(e) =>
                                        handleUpdate(
                                            row,
                                            col.key,
                                            parseFloat(e.currentTarget.value),
                                        )}
                                />
                            {:else}
                                <input
                                    type="text"
                                    class="input input-bordered input-sm w-full"
                                    value={row[col.key]}
                                    on:blur={(e) =>
                                        handleUpdate(
                                            row,
                                            col.key,
                                            e.currentTarget.value,
                                        )}
                                />
                            {/if}
                        </td>
                    {/each}
                    <td class="text-center">
                        <button
                            class="btn btn-ghost btn-xs text-error"
                            on:click={() => handleDelete(row)}
                            title="Delete"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke-width="1.5"
                                stroke="currentColor"
                                class="w-4 h-4"
                            >
                                <path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"
                                />
                            </svg>
                        </button>
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>
    <div class="p-4 border-t border-base-200 flex justify-center">
        <button
            class="btn btn-outline btn-primary btn-sm gap-2"
            on:click={handleCreate}
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-4 h-4"
            >
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M12 4.5v15m7.5-7.5h-15"
                />
            </svg>
            Add New Row
        </button>
    </div>
</div>
