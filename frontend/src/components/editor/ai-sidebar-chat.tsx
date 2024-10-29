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
import { vs } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { AuthActions } from '@/lib/auth';
import getUrl from '@/app/url';
import { useWebSocket } from '@/app/hooks/use-websocket';


const baseUrl = getUrl();
const base = new URL(baseUrl).host;
const protocol = process.env.NODE_ENV === 'development' ? 'ws' : 'wss';


export default function AiSidebarChat() {
    const [isLoading, setIsLoading] = useState(false);
    const [input, setInput] = useState('');
    const [currentResponse, setCurrentResponse] = useState('');
    const [error, setError] = useState<string | null>(null);

    const { activeFile } = useFiles()
    const { lineageData } = useLineage()

    const { getToken } = AuthActions();
    const accessToken = getToken("access");

    const { startWebSocket, sendMessage, stopWebSocket, } = useWebSocket(`${protocol}://${base}/ws/infer/?token=${accessToken}`, {
        onOpen: () => {
            console.log('WebSocket connected')
            sendMessage(JSON.stringify(
                {
                    type: 'completion',
                    current_file: activeFile?.content || '',
                    asset_id: visibleLineage?.data?.lineage?.asset_id,
                    related_assets: visibleLineage?.data?.lineage?.assets,
                    asset_links: visibleLineage?.data?.lineage?.asset_links,
                    column_links: visibleLineage?.data?.lineage?.column_links,
                    instructions: input
                }));

        },
        onClose: () => {
            console.log('WebSocket disconnected')
        },
        onMessage: (event) => {
            const data = JSON.parse(event.data);
            console.log({ data })
            if (data.type === 'message_chunk') {
                setCurrentResponse(prev => prev + data.content);
            } else if (data.type === 'message_end') {
                setIsLoading(false);
                stopWebSocket();
            }
        },
        onError: (error) => {
            console.error('WebSocket error:', error);
            // setError('WebSocket connection error. Please try again.');
            setIsLoading(false);
            stopWebSocket();
        }
    })



    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setCurrentResponse('');
        startWebSocket();
        setError(null);

    };




    const visibleLineage = lineageData[activeFile?.node.path || '']

    return (
        <div className="flex flex-col  w-full">
            <div className="space-y-2 relative bg-muted p-1 rounded">
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
                    className='bg-white shadow-none border-none outline-none ring-0 resize-none w-full focus:outline-none focus:ring-0 focus:border-none focus:ring-offset-0 !border-0'
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
                {error && (
                    <div className="text-red-500">{error}</div>
                )}
                <Markdown
                    children={currentResponse}
                    components={{
                        code(props: any) {
                            const { children, className, node, ...rest } = props
                            const match = /language-(\w+)/.exec(className || '')
                            return match ? (
                                <SyntaxHighlighter
                                    {...rest}
                                    PreTag="div"
                                    children={String(children).replace(/\n$/, '')}
                                    language={match[1]}
                                    style={vs}
                                    customStyle={{
                                        fontSize: '18px',
                                        background: 'gray-100'
                                    }}
                                    wrapLines={true}
                                    wrapLongLines={true}
                                />
                            ) : (
                                <code {...rest} className={className}>
                                    {children}
                                </code>
                            )
                        }
                    }}
                />
                <div className='h-12' />
            </div>
        </div >
    );
}
