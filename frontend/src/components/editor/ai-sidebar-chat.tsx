import React, { useState, useRef, useEffect } from 'react';
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

export default function AiSidebarChat() {
    const [question, setQuestion] = useState('');
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const socketRef = useRef<WebSocket | null>(null);
    const [currentResponse, setCurrentResponse] = useState('');

    useEffect(() => {
        // Create a WebSocket connection
        socketRef.current = new WebSocket('ws://localhost:8000/infer/stream');

        socketRef.current.onopen = () => {
            console.log('WebSocket Connected');
        };

        socketRef.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Received from server:', data);
            if (data.type === "message_chunk") {
                setCurrentResponse(prev => {
                    const updated = prev + data.content;
                    console.log('Current response:', updated);
                    return updated;
                });
            } else if (data.type === "message_end") {
                // setMessages(prevMessages => {
                //     const updatedMessages = [
                //         ...prevMessages,
                //         { role: 'assistant', content: currentResponse + data.content }
                //     ];
                //     console.log('Updated messages:', updatedMessages);
                //     return updatedMessages;
                // });
                // setCurrentResponse('');
            }
        };

        socketRef.current.onclose = () => {
            console.log('WebSocket Disconnected');
        };

        // Cleanup on component unmount
        return () => {
            if (socketRef.current) {
                socketRef.current.close();
            }
        };
    }, []);

    // useEffect(() => {
    //     messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    // }, [messages]);

    const handleSubmit = () => {
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
            setIsLoading(true);
            socketRef.current.send(JSON.stringify({ message: question }));
            setMessages(prevMessages => {
                const updatedMessages = [
                    ...prevMessages,
                    { role: 'user', content: question }
                ];
                console.log('Updated messages after user input:', updatedMessages);
                return updatedMessages;
            });
            setQuestion('');
            setIsLoading(false);
        } else {
            console.error('WebSocket is not connected');
        }
    };

    return (
        <div className="w-full space-y-2">
            <div className="max-h-60 overflow-y-auto mb-4">
                {/* {messages.map((message, index) => (
                    <div key={index} className={`p-2 ${message.role === 'user' ? 'bg-blue-100' : 'bg-gray-100'} rounded mb-2`}>
                        <strong>{message.role === 'user' ? 'You:' : 'AI:'}</strong> {message.content}
                    </div>
                ))}
                <div ref={messagesEndRef} /> */}
                {currentResponse}
            </div>
            <Textarea
                placeholder="Ask a question..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
            />
            <Button
                className='float-right'
                onClick={handleSubmit}
                disabled={isLoading || !question.trim()}
            >
                {isLoading ? 'Sending...' : 'Send'}
            </Button>
        </div>
    );
}
