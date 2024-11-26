
interface ErrorDisplayProps {
  error: string | null;
}

export default function ErrorDisplay({ error }: ErrorDisplayProps) {
  if (!error) return null;
  return <div className="text-red-500 text-sm">{error}</div>;
}