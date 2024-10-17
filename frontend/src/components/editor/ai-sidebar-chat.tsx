import React, { useState, useRef, useEffect } from 'react';
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import { Loader2 } from 'lucide-react';
import Markdown from 'react-markdown'
import { useFiles } from '@/app/contexts/FilesContext';
import { Badge } from '../ui/badge';
import { useLineage } from '@/app/contexts/LineageContext';
const ApiHost = true ? "http://localhost:8000" : process.env.BACKEND_HOST;
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { dark } from 'react-syntax-highlighter/dist/esm/styles/prism'

export default function AiSidebarChat() {
    const [isLoading, setIsLoading] = useState(false);
    const [input, setInput] = useState('');
    const [currentResponse, setCurrentResponse] = useState('');
    const [error, setError] = useState<string | null>(null);
    const ws = useRef<WebSocket | null>(null);

    const { activeFile } = useFiles()
    const { lineageData } = useLineage()

    const connectWebSocket = () => {
        console.log(`connecting to ws://${ApiHost}/ws/echo/123`)
        ws.current = new WebSocket(`ws://localhost:8000/ws/echo/123/`);

        // ws.current = new WebSocket('ws://localhost:8000/ws/subscribe/0/')


        ws.current.onopen = () => {
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
            // setError('WebSocket connection error. Please try again.');
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
                ws.current.send(JSON.stringify({ type: 'completion', related_assets: visibleLineage?.data?.lineage?.assets.map((asset: any) => asset.id), asset_links: visibleLineage?.data?.lineage?.asset_links, instructions: input }));
            } else {
                throw new Error('WebSocket is not connected');
            }
        } catch (err) {
            console.error('Message submission failed:', err);
            setError('Failed to send message. Please try again.');
            setIsLoading(false);
        }
    };






    console.log({ lineageData })
    console.log({ activeFile })
    const visibleLineage = lineageData[activeFile?.node.path || '']
    console.log({ visibleLineage })
    return (
        <div className="p-4 flex flex-col overflow-y-scroll">
            <div className="space-y-2 relative focus-within:border focus-within:border-primary rounded-md">
                <Badge variant="outline" className='text-xs text-muted-foreground'>
                    {activeFile?.node.name} (Current file)
                </Badge>
                {visibleLineage && visibleLineage?.data?.lineage?.assets && (
                    <div className="flex flex-wrap">
                        {visibleLineage.data.lineage.assets.map((node: any) => (
                            <Badge key={node.id} variant="outline" className='text-xs text-muted-foreground'>
                                {node.name}
                            </Badge>
                        ))}
                    </div>
                )}
                <Textarea
                    placeholder='Ask anything'
                    className='bg-transparent shadow-none border-none outline-none ring-0 resize-none w-full focus:outline-none focus:ring-0 focus:border-none'
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                />
                <Button
                    className='float-right'
                    onClick={handleSubmit}
                    disabled={isLoading || !input.trim()}
                >
                    {isLoading ? <Loader2 className='text-muted-foreground animate-spin h-5 w-5' /> : 'Send'}
                </Button>
            </div>
            <div className="overflow-y-scroll overflow-x-hidden space-y-4 mt-4">
                {isLoading && (
                    <div className='flex items-center justify-center'>
                        <Loader2 className='text-muted-foreground animate-spin h-5 w-5' />
                    </div>
                )}
                {error && (
                    <div className="text-red-500">{error}</div>
                )}
                <Markdown
                    children={currentResponse}
                    components={{
                        code(props) {
                            const { children, className, node, ...rest } = props
                            const match = /language-(\w+)/.exec(className || '')
                            return match ? (
                                <SyntaxHighlighter
                                    {...rest}
                                    PreTag="div"
                                    children={String(children).replace(/\n$/, '')}
                                    language={match[1]}
                                    style={dark}
                                />
                            ) : (
                                <code {...rest} className={className}>
                                    {children}
                                </code>
                            )
                        }
                    }}
                />
            </div>
        </div >
    );
}
