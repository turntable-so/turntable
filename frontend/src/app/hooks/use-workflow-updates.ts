'use client'
import { useEffect, useState } from 'react';
import getUrl from '@/app/url'

const baseUrl = getUrl()
const protocol = process.env.NODE_ENV === "development" ? "ws" : "wss";

const useWorkflowUpdates = (workspaceId: string) => {
    const [workflowStatus, setWorkflowStatus] = useState<string | null>(null);
    const [resource, setResource] = useState<any>(null);

    useEffect(() => {
        // Construct the WebSocket URL
        const base = baseUrl?.split("ttp://")[1];
        const socketUrl = `${protocol}://${base}/ws/subscribe/${workspaceId}/`;
        const socket = new WebSocket(socketUrl);

        socket.onopen = () => {
            console.log(`WebSocket connection established: ${socketUrl}`);
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setWorkflowStatus(data.status);
            setResource(data.resource_id);
            console.log(`Workflow Run ${data.workflow_run_id} status updated: ${data.status}`);
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        socket.onclose = (event) => {
            console.log('WebSocket connection closed:', event);
        };

        // Cleanup on component unmount
        return () => {
            socket.close();
        };
    }, [workspaceId]);

    return [workflowStatus, resource];
};

export default useWorkflowUpdates;