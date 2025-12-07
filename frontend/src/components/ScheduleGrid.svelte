<script lang="ts">
  let { schedule } = $props();
  
  const days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  const slots = ["08-10", "10-12", "12-14", "14-16", "16-18"];
  
  // Helper to find lesson in slot
  function getLesson(dayIdx: number, slotIdx: number) {
    // This logic depends on how 'schedule' data is structured.
    // Assuming schedule is a list of { day, slot, lessonName, roomName, teacherName }
    return schedule.find((s: any) => s.day === dayIdx && s.slot === slotIdx);
  }
</script>

<div class="overflow-x-auto">
  <table class="table table-zebra w-full border">
    <thead>
      <tr>
        <th>Time / Day</th>
        {#each days as day}
          <th>{day}</th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#each slots as slot, slotIdx}
        <tr>
          <td class="font-bold">{slot}</td>
          {#each days as day, dayIdx}
            {@const lesson = getLesson(dayIdx, slotIdx)}
            <td class="border min-h-[100px] p-2">
              {#if lesson}
                <div class="badge badge-primary p-3 h-auto flex flex-col items-start gap-1">
                  <span class="font-bold">{lesson.lessonName}</span>
                  <span class="text-xs">{lesson.teacherName}</span>
                  <span class="text-xs badge badge-outline">{lesson.roomName}</span>
                </div>
              {/if}
            </td>
          {/each}
        </tr>
      {/each}
    </tbody>
  </table>
</div>
