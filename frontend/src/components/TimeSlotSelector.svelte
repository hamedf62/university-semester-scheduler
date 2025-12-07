<script lang="ts">
    import { createEventDispatcher } from "svelte";

    export let availableSlots: number[] = []; // List of selected TimeSlot IDs
    export let timeSlots: {
        id: number;
        day_of_week: number;
        start_time: string;
        end_time: string;
    }[] = [];

    const dispatch = createEventDispatcher();

    // Group slots by day
    // 0=Sat, 1=Sun, ...
    const days = [
        "Saturday",
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
    ];

    // Map day -> slots
    let slotsByDay: Record<number, typeof timeSlots> = {};

    $: {
        slotsByDay = {};
        timeSlots.forEach((slot) => {
            if (!slotsByDay[slot.day_of_week])
                slotsByDay[slot.day_of_week] = [];
            slotsByDay[slot.day_of_week].push(slot);
        });
        // Sort slots by time
        Object.keys(slotsByDay).forEach((d) => {
            slotsByDay[parseInt(d)].sort((a, b) =>
                a.start_time.localeCompare(b.start_time),
            );
        });
    }

    function toggleSlot(id: number) {
        if (availableSlots.includes(id)) {
            availableSlots = availableSlots.filter((s) => s !== id);
        } else {
            availableSlots = [...availableSlots, id];
        }
        dispatch("change", availableSlots);
    }

    function isSelected(id: number) {
        return availableSlots.includes(id);
    }
</script>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {#each Object.keys(slotsByDay) as dayStr}
        {@const day = parseInt(dayStr)}
        <div class="card bg-base-200 shadow-sm">
            <div class="card-body p-4">
                <h3 class="card-title text-sm">{days[day]}</h3>
                <div class="flex flex-wrap gap-2">
                    {#each slotsByDay[day] as slot}
                        <button
                            class="btn btn-xs {isSelected(slot.id)
                                ? 'btn-primary'
                                : 'btn-outline'}"
                            on:click={() => toggleSlot(slot.id)}
                        >
                            {slot.start_time} - {slot.end_time}
                        </button>
                    {/each}
                </div>
            </div>
        </div>
    {/each}
</div>
