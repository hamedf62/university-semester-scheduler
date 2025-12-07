export async function startSolver(weights: any) {
    const res = await fetch('/api/solve', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(weights)
    });
    return await res.json();
}

export async function getResults(runId: string) {
    const res = await fetch(`/api/results/${runId}`);
    return await res.json();
}
