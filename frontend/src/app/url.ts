export default function getUrl() {
    return process.env.NEXT_PUBLIC_BACKEND_HOST || (typeof window === "undefined" ? "http://localhost:8000" : "http://localhost:8000")
} 
