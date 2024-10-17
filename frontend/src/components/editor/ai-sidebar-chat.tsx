import React, { useState, useRef, useEffect } from 'react';
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import { Loader2 } from 'lucide-react';
import Markdown from 'react-markdown'
import { submitEcho } from '@/app/actions/actions';
import { toast } from 'sonner';
const ApiHost = true ? "http://localhost:8000" : process.env.BACKEND_HOST;

export default function AiSidebarChat() {
    const [isLoading, setIsLoading] = useState(false);
    const [input, setInput] = useState('');
    const [currentResponse, setCurrentResponse] = useState('');
    const [error, setError] = useState<string | null>(null);
    const ws = useRef<WebSocket | null>(null);

    const connectWebSocket = () => {
        console.log(`connecting to ws://${ApiHost}/ws/echo/123`)
        ws.current = new WebSocket(`ws://localhost:8000/ws/echo/123/`);

        // ws.current = new WebSocket('ws://localhost:8000/ws/subscribe/0/')


        ws.current.onopen = () => {
            toast.success('WebSocket connected');
            console.log('WebSocket connected');
        };

        ws.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log({ data })
            if (data.type === 'message_chunk') {
                setCurrentResponse(prev => prev + data.content);
            } else if (data.type === 'message_end') {
                setIsLoading(false);
            }
        };

        ws.current.onerror = (error) => {
            console.error('WebSocket error:', error);
            setError('WebSocket connection error. Please try again.');
            setIsLoading(false);
        };

        ws.current.onclose = () => {
            console.log('WebSocket disconnected');
        };

    };

    useEffect(() => {
        connectWebSocket()
        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setCurrentResponse('');
        setError(null);

        try {
            if (ws.current?.readyState === WebSocket.OPEN) {
                ws.current.send(JSON.stringify({ type: 'message', content: input }));
            } else {
                throw new Error('WebSocket is not connected');
            }
        } catch (err) {
            console.error('Message submission failed:', err);
            setError('Failed to send message. Please try again.');
            setIsLoading(false);
        }
    };

    return (
        <div className="p-4 flex flex-col overflow-y-scroll">
            <div className="space-y-2">
                <Textarea
                    placeholder="Ask a question..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                />
                <Button
                    className='float-right'
                    onClick={handleSubmit}
                    disabled={isLoading || !input.trim()}
                >
                    {isLoading ? 'Sending...' : 'Send'}
                </Button>
            </div>
            <div className="overflow-y-scroll space-y-4 mt-4">
                {isLoading && (
                    <div className='flex items-center justify-center'>
                        <Loader2 className='text-muted-foreground animate-spin h-5 w-5' />
                    </div>
                )}
                {error && (
                    <div className="text-red-500">{error}</div>
                )}
                <Markdown>{currentResponse}</Markdown>
            </div>
        </div>
    );
}
