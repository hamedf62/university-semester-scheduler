<script lang="ts">
    import "../app.css";
    let { children } = $props();
</script>

<div class="min-h-screen bg-base-200">
    <div class="navbar bg-base-100 shadow-lg mb-4">
        <div class="flex-1">
            <a class="btn btn-ghost text-xl">University Scheduler</a>
        </div>
        <div class="flex-none">
            <ul class="menu menu-horizontal px-1">
                <li><a href="/">Dashboard</a></li>
                <li><a href="/settings">Global Settings</a></li>
            </ul>
        </div>
    </div>

    <main class="container mx-auto p-4">
        {@render children()}
    </main>
</div>
