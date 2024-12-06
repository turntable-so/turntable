export default function buildWebhookUrl(jobId: string) {
    return `${window.location.origin}/api/jobs/${jobId}/trigger`;
}
