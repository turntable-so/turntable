import React, { useState, useRef, useEffect } from 'react';
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import { Loader2 } from 'lucide-react';
import Markdown from 'react-markdown'
import { useFiles } from '@/app/contexts/FilesContext';
import { Badge } from '../ui/badge';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vs } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { AuthActions } from '@/lib/auth';
import getUrl from '@/app/url';
import { useWebSocket } from '@/app/hooks/use-websocket';
import CustomEditor from './CustomEditor';


const baseUrl = getUrl();
const base = new URL(baseUrl).host;
const protocol = process.env.NODE_ENV === 'development' ? 'ws' : 'wss';


export default function AiSidebarChat() {
    const [isLoading, setIsLoading] = useState(false);
    const [input, setInput] = useState('');
    const [currentResponse, setCurrentResponse] = useState('');
    const [error, setError] = useState<string | null>(null);

    const { activeFile, lineageData } = useFiles()

    const visibleLineage = lineageData[activeFile?.node.path || ''] || null

    const { getToken } = AuthActions();
    const accessToken = getToken("access");

    const { startWebSocket, sendMessage, stopWebSocket, } = useWebSocket(`${protocol}://${base}/ws/infer/?token=${accessToken}`, {
        onOpen: () => {
            console.log('WebSocket connected')
            sendMessage(JSON.stringify(
                {
                    type: 'completion',
                    current_file: activeFile?.content || '',
                    asset_id: visibleLineage?.data?.asset_id,
                    related_assets: visibleLineage?.data?.assets,
                    asset_links: visibleLineage?.data?.asset_links,
                    column_links: visibleLineage?.data?.column_links,
                    instructions: input
                }))
        },
        onClose: () => {
            console.log('WebSocket disconnected')
        },
        onMessage: ({ event }) => {
            const data = JSON.parse(event.data);
            console.log({ data })
            if (data.type === 'message_chunk') {
                setCurrentResponse(prev => prev + data.content);
            } else if (data.type === 'message_end') {
                setIsLoading(false);
                stopWebSocket();
            }
        },
        onError: ({ event }) => {
            console.error('WebSocket error:', event);
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




    return (
        <div className="flex flex-col  w-full overflow-y-scroll h-full">
            <div className="space-y-2  bg-muted p-1 rounded">
                <Badge variant="outline" className='text-xs text-muted-foreground'>
                    {activeFile?.node.name} (Current file)
                </Badge>
                {visibleLineage && visibleLineage?.data?.assets && (
                    <div className="flex flex-wrap">
                        {visibleLineage.data.assets.map((node: any) => (
                            <Badge key={node.id} variant="outline" className='text-xs text-muted-foreground'>
                                {node.name}
                            </Badge>
                        ))}
                    </div>
                )}
                <Textarea
                    placeholder='Ask anything'
                    className='bg-white dark:bg-zinc-700 shadow-none border-none outline-none ring-0 resize-none w-full focus:outline-none focus:ring-0 focus:border-none focus:ring-offset-0 !border-0'
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
            <div className="overflow-x-hidden space-y-4 mt-4">
                {error && (
                    <div className="text-red-500">{error}</div>
                )}
                <Markdown
                    children={currentResponse}
                    className="prose dark:prose-invert max-w-none [&_pre]:!p-0 [&_pre]:!m-0 [&_pre]:!border-none [&_code]:!border-none"
                    components={{
                        code(props: any) {
                            const { children, className, node, ...rest } = props
                            const match = /language-(\w+)/.exec(className || '')
                            const lineCount = String(children).split('\n').length;
                            const height = `${lineCount * 22}px`;
                            const editorRef = useRef<any>(null);

                            return match ? (
                                <div style={{ height, overflow: 'hidden', border: 'none' }} className="pointer-events-none select-none">
                                    <CustomEditor
                                        key={'fixed'}
                                        value={String(children).replace(/\n$/, '')}
                                        language={match[1]}
                                        options={{
                                            minimap: { enabled: false },
                                            scrollbar: {
                                                vertical: "hidden",
                                                horizontal: "hidden",
                                                verticalScrollbarSize: 0,
                                                horizontalScrollbarSize: 0,
                                            },
                                            lineNumbers: "off",
                                            wordWrap: "on",
                                            fontSize: 14,
                                            lineNumbersMinChars: 3,
                                            renderLineHighlight: "none",
                                            readOnly: true,
                                            overviewRulerBorder: false,
                                            hideCursorInOverviewRuler: true,
                                            overviewRulerLanes: 0,
                                        }}
                                        height={height}
                                        onMount={(editor, monaco) => {
                                            editorRef.current = editor;
                                            // Initial content set
                                            const model = editor.getModel();
                                            if (model) {
                                                model.setValue(String(children).replace(/\n$/, ''));
                                            }
                                        }}
                                        onChange={(value, event) => {
                                            // If you need to handle changes
                                            if (editorRef.current) {
                                                const model = editorRef.current.getModel();
                                                if (model) {
                                                    model.applyEdits([
                                                        {
                                                            range: model.getFullModelRange(),
                                                            text: value
                                                        }
                                                    ]);
                                                }
                                            }
                                        }}
                                    />
                                </div>
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