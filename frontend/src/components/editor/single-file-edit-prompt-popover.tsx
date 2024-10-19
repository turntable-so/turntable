import { useState, useEffect, useRef } from 'react'
import { useFiles, OpenedFile } from '@/app/contexts/FilesContext'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Check, X, Loader2 } from 'lucide-react'
import { useLineage } from '@/app/contexts/LineageContext'
const ApiHost = true ? "http://localhost:8000" : process.env.BACKEND_HOST;
export default function PromptBox({ setPromptBoxOpen }: { setPromptBoxOpen: (open: boolean) => void }) {

    const { activeFile, setActiveFile, updateFileContent } = useFiles();
    const { lineageData } = useLineage();
    const visibleLineage = lineageData[activeFile?.node.path || '']


    const [prompt, setPrompt] = useState('')
    const [mode, setMode] = useState<'PROMPT' | 'CONFIRM'>('PROMPT')
    const [isLoading, setIsLoading] = useState(false)
    const [modifiedContent, setModifiedContent] = useState('')
    const ws = useRef<WebSocket | null>(null);

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

            if (data.type === 'single_file_edit_chunk') {
                console.log(data.content)
                setActiveFile((prev: OpenedFile) => {
                    return {
                        ...prev,
                        view: 'diff',
                        diff: {
                            original: prev.content,
                            modified: prev.diff?.modified + data.content
                        }
                    } as OpenedFile
                })
            } else if (data.type === 'single_file_edit_end') {
                setMode('CONFIRM')
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

    }, [activeFile, modifiedContent])

    useEffect(() => {
        connectWebSocket()
        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, []);

    const handleSubmit = async () => {
        setModifiedContent('')

        if (activeFile) {
            setIsLoading(true)
            setActiveFile({
                ...activeFile,
                view: 'diff',
                diff: {
                    original: activeFile.content,
                    modified: ""
                }
            })
            try {
                if (ws.current?.readyState === WebSocket.OPEN) {
                    ws.current.send(JSON.stringify(
                        {
                            type: 'single_file_edit',
                            current_file: activeFile.content,
                            related_assets: visibleLineage?.data?.lineage?.assets.map((asset: any) => asset.id),
                            asset_links: visibleLineage?.data?.lineage?.asset_links,
                            instructions: prompt
                        }));

                } else {
                    throw new Error('WebSocket is not connected');
                }
            } catch (err) {
                console.error('Message submission failed:', err);
                setIsLoading(false);
            }
        }
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
            e.preventDefault();
            handleSubmit();
        }
    }

    const handleEscape = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
            setPromptBoxOpen(false);
        }
    };

    useEffect(() => {
        document.addEventListener('keydown', handleEscape);
        return () => {
            document.removeEventListener('keydown', handleEscape);
        };
    }, []);

    useEffect(() => {
        const textarea = document.querySelector('textarea');
        if (textarea) {
            textarea.addEventListener('keydown', handleKeyDown as any);
            return () => {
                textarea.removeEventListener('keydown', handleKeyDown as any);
            };
        }
    }, []);

    return (
        <div className='border-b py-2 mb-2'>
            <div className="flex flex-col items-center w-full px-4">
                <Textarea className='w-full my-2 z-100' autoFocus placeholder="Add materialization to this model" value={prompt} onChange={(e) => setPrompt(e.target.value)} disabled={isLoading} />
                <div className='flex space-x-2 justify-end w-full'>
                    <>
                        {mode === 'PROMPT' ? (
                            <>
                                <Button
                                    size='sm'

                                    variant='outline'
                                    className='rounded-sm'
                                    onClick={() => {
                                        setPromptBoxOpen(false)
                                        setModifiedContent('')
                                        setActiveFile({
                                            ...activeFile,
                                            view: 'edit',
                                            diff: undefined
                                        } as OpenedFile)
                                    }}
                                >
                                    Cancel
                                </Button>
                                <Button
                                    size='sm'
                                    disabled={!prompt || isLoading}
                                    variant='default'
                                    className='rounded-sm'
                                    onClick={handleSubmit}
                                >
                                    {isLoading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : 'Generate'}
                                </Button>
                            </>
                        ) : (
                            <>
                                <Button
                                    size='sm'

                                    variant='destructive'
                                    className='rounded-sm'
                                    onClick={() => {
                                        if (activeFile) {
                                            setActiveFile({
                                                ...activeFile,
                                                view: 'edit',
                                                diff: undefined
                                            })
                                        }
                                        setPromptBoxOpen(false)
                                    }}
                                >
                                    <X className='mr-2 size-4' />
                                    Reject
                                </Button>
                                <Button
                                    size='sm'
                                    disabled={!prompt || isLoading}
                                    variant='default'
                                    className='rounded-sm'
                                    onClick={() => {
                                        updateFileContent(activeFile?.node.path || '', activeFile?.diff?.modified || '');
                                        setActiveFile({
                                            ...activeFile,
                                            isDirty: true,
                                            content: activeFile?.diff?.modified || '',
                                            view: 'edit',
                                            diff: undefined
                                        } as OpenedFile)
                                        setPromptBoxOpen(false)
                                    }}
                                >
                                    <Check className='mr-2 size-4' />
                                    Accept
                                </Button>
                            </>
                        )}
                    </>
                </div>
            </div>
        </div>
    )
}
