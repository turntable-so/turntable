'use client'
import { useEffect, useState } from 'react';
const baseUrl = process.env.NODE_ENV === "development" ? "localhost:8000" : process.env.NEXT_PUBLIC_API_BASE_URL;
const protocol = process.env.NODE_ENV === "development" ? "ws" : "wss";

const useWorkflowUpdates = (workspaceId: string) => {
    const [workflowStatus, setWorkflowStatus] = useState(null);

    useEffect(() => {
        const socket = new WebSocket(`${protocol}://${baseUrl}/ws/subscribe/${workspaceId}/`);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setWorkflowStatus(data.status);
            console.log(`Workflow Run ${data.workflow_run_id} status updated: ${data.status}`);
        };

        return () => {
            socket.close();
        };
    }, [workspaceId]);

    return workflowStatus;
};

export default useWorkflowUpdates;
