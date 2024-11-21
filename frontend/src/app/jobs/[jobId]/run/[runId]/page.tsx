type JobRunPageProps = {
  params: { jobId: string; runId: string };
};

export default function JobRunPage({ params }: JobRunPageProps) {
  return (
    <div>
      <h1>Job: {params.jobId}</h1>
      <h2>Run: {params.runId}</h2>
    </div>
  );
}
