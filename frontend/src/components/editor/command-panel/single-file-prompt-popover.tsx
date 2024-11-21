import { useState, useEffect, useRef } from 'react'
import { useFiles, OpenedFile } from '@/app/contexts/FilesContext'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Check, X, Loader2 } from 'lucide-react'
import { useLineage } from '@/app/contexts/LineageContext'
import { AuthActions } from "@/lib/auth";
import { useWebSocket } from '@/app/hooks/use-websocket'
import getUrl from '@/app/url'

const baseUrl = getUrl();
const base = new URL(baseUrl).host;
const protocol = process.env.NODE_ENV === 'development' ? 'ws' : 'wss';

const ApiHost = true ? "http://localhost:8000" : process.env.BACKEND_HOST;
export default function SingleFileEditPromptPopover({ setPromptBoxOpen }: { setPromptBoxOpen: (open: boolean) => void }) {
    const { getToken } = AuthActions();
    const accessToken = getToken("access");
    const { startWebSocket, sendMessage, stopWebSocket, } = useWebSocket(`${protocol}://${base}/ws/infer/?token=${accessToken}`, {
        onOpen: () => {
            console.log('WebSocket connected')
            sendMessage(JSON.stringify(
                {
                    type: 'single_file_edit',
                    current_file: activeFile?.content || '',
                    asset_id: visibleLineage?.data?.asset_id,
                    related_assets: visibleLineage?.data?.assets,
                    asset_links: visibleLineage?.data?.asset_links,
                    column_links: visibleLineage?.data?.column_links,
                    instructions: prompt
                }));

        },
        onClose: () => {
            console.log('WebSocket disconnected')
        },
        onMessage: ({ event }) => {
            const data = JSON.parse(event.data);

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
                stopWebSocket();
                setMode('CONFIRM')
                setIsLoading(false);
            }
        },
        onError: ({ event }) => {
            console.error('WebSocket error:', event);
            setIsLoading(false);
        }
    })

    const { activeFile, setActiveFile, updateFileContent, lineageData } = useFiles();
    const visibleLineage = lineageData[activeFile?.node.path || '']


    const [prompt, setPrompt] = useState('')
    const [mode, setMode] = useState<'PROMPT' | 'CONFIRM'>('PROMPT')
    const [isLoading, setIsLoading] = useState(false)
    const [modifiedContent, setModifiedContent] = useState('')


    const handleSubmit = async () => {
        setModifiedContent('')
        if (activeFile) {
            startWebSocket();
            setIsLoading(true)
            setActiveFile({
                ...activeFile,
                view: 'diff',
                diff: {
                    original: activeFile.content,
                    modified: ""
                }
            })
            console.log('Sending message')


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