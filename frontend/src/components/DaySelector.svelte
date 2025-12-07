<script lang="ts">
    import { createEventDispatcher } from "svelte";

    export let value: string = ""; // "0,2,4"

    const dispatch = createEventDispatcher();
    const days = [
        { id: 0, label: "Saturday" },
        { id: 1, label: "Sunday" },
        { id: 2, label: "Monday" },
        { id: 3, label: "Tuesday" },
        { id: 4, label: "Wednesday" },
        { id: 5, label: "Thursday" },
        { id: 6, label: "Friday" },
    ];

    $: selectedDays = value ? value.split(",").map(Number) : [];

    function toggleDay(dayId: number) {
        let newSelection;
        if (selectedDays.includes(dayId)) {
            newSelection = selectedDays.filter((d) => d !== dayId);
        } else {
            newSelection = [...selectedDays, dayId].sort();
        }
        value = newSelection.join(",");
        dispatch("change", value);
    }
</script>

<div class="flex flex-wrap gap-2">
    {#each days as day}
        <button
            class="btn btn-xs {selectedDays.includes(day.id)
                ? 'btn-primary'
                : 'btn-outline'}"
            on:click={() => toggleDay(day.id)}
        >
            {day.label}
        </button>
    {/each}
</div>
