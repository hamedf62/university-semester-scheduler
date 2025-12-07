<script lang="ts">
    import { createEventDispatcher } from "svelte";
    import TimeSlotSelector from "./TimeSlotSelector.svelte";

    export let value: number[] = []; // Array of TimeSlot IDs
    export let timeSlots: any[] = []; // Passed from parent

    const dispatch = createEventDispatcher();
    let isOpen = false;

    const days = [
        "Saturday",
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
    ];
    const colors = [
        "badge-primary",
        "badge-secondary",
        "badge-accent",
        "badge-info",
        "badge-success",
        "badge-warning",
        "badge-error",
    ];

    function handleChange(e: CustomEvent) {
        value = e.detail;
        dispatch("change", value);
    }

    function getSlotLabel(id: number) {
        const slot = timeSlots.find((s) => s.id === id);
        if (!slot) return "";
        return `${slot.start_time}-${slot.end_time}`;
    }

    function getSlotDay(id: number) {
        const slot = timeSlots.find((s) => s.id === id);
        return slot ? slot.day_of_week : -1;
    }

    $: sortedSlots = [...(value || [])].sort((a, b) => {
        const dayA = getSlotDay(a);
        const dayB = getSlotDay(b);
        if (dayA !== dayB) return dayA - dayB;
        return a - b; // simple ID sort for same day
    });
</script>

<div>
    <div
        class="flex flex-wrap gap-1 mb-2 cursor-pointer"
        on:click={() => (isOpen = true)}
        role="button"
        tabindex="0"
        on:keypress={(e) => e.key === "Enter" && (isOpen = true)}
    >
        {#if sortedSlots.length > 0}
            {#each sortedSlots as slotId}
                {@const day = getSlotDay(slotId)}
                <div class="badge {colors[day]} badge-sm">
                    {days[day].substring(0, 3)}
                    {getSlotLabel(slotId)}
                </div>
            {/each}
        {:else}
            <span class="text-xs opacity-50">No slots selected</span>
        {/if}
    </div>
    <button
        class="btn btn-xs btn-outline w-full"
        on:click={() => (isOpen = true)}
    >
        Edit Slots
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
                class="bg-base-100 p-6 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            >
                <h3 class="text-lg font-bold mb-4">
                    Select Available Time Slots
                </h3>
                <TimeSlotSelector
                    availableSlots={value}
                    {timeSlots}
                    on:change={handleChange}
                />
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
