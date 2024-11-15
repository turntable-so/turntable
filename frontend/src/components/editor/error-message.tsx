import { CircleAlertIcon } from "lucide-react";

export default function ErrorMessage({ error }: { error: string }) {
    return (
        <div className="text-red-500 text-sm flex items-center justify-center h-full">
            <div className="flex items-center">
                <CircleAlertIcon className="h-4 w-4 mr-2" />
                {error}
            </div>
        </div>
    )
}
