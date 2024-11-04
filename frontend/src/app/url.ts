export default function getUrl() {
  return typeof window === "undefined"
    ? "http://api:8000"
    : "http://localhost:8000"; "http://localhost:8000";
}
