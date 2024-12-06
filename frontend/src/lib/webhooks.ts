
export function buildWebhookUrl(jobId?: string) {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;

    if (!jobId) return `${apiUrl}/webhooks/run_job/<job_id>/`;
    return `${apiUrl}/webhooks/run_job/${jobId}/`;
}


