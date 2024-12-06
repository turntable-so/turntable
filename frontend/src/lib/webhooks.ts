
export function buildWebhookUrl(jobId?: string) {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;

    if (!jobId) return `${apiUrl}/run_job/<job_id>`;
    return `${apiUrl}/run_job/${jobId}`;
}


