<script lang="ts">
  let files: FileList | null = $state(null);
  let uploading = $state(false);
  let message = $state("");

  async function handleUpload() {
    if (!files || files.length === 0) return;
    
    uploading = true;
    const formData = new FormData();
    formData.append('file', files[0]);

    try {
      const res = await fetch('/api/upload/data', {
        method: 'POST',
        body: formData
      });
      
      if (res.ok) {
        const data = await res.json();
        message = "Upload successful! " + JSON.stringify(data.details);
      } else {
        message = "Upload failed.";
      }
    } catch (e) {
      message = "Error uploading file.";
    } finally {
      uploading = false;
    }
  }
</script>

<div class="card bg-base-100 shadow-xl">
  <div class="card-body">
    <h2 class="card-title">Upload Data</h2>
    <p>Upload your Excel file containing Teachers, Courses, and Groups.</p>
    
    <div class="form-control w-full max-w-xs">
      <input type="file" class="file-input file-input-bordered w-full max-w-xs" bind:files accept=".xlsx, .xls" />
    </div>
    
    <div class="card-actions justify-end mt-4">
      <button class="btn btn-primary" onclick={handleUpload} disabled={uploading}>
        {#if uploading}
          <span class="loading loading-spinner"></span>
          Uploading...
        {:else}
          Upload
        {/if}
      </button>
    </div>
    
    {#if message}
      <div class="alert alert-info mt-4">
        <span>{message}</span>
      </div>
    {/if}
  </div>
</div>
