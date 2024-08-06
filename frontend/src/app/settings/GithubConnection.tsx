'use client'

import { Button } from "../../components/ui/button"
import { useEffect } from "react"
import { createGithubInstallation } from "../actions/actions"
import { useRouter } from "next/navigation"
import { useSearchParams } from 'next/navigation'
import { Code, ExternalLink, Github, Lock } from "lucide-react"
import { Badge } from "../../components/ui/badge"

import * as React from "react"

import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "../../components/ui/card"
import { Input } from "../../components/ui/input"
import { Label } from "../../components/ui/label"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "../../components/ui/select"
import Link from "next/link"

export function CardWithForm() {
    return (
        <div></div>
    )
}




const GithubLogo = () => (
    <div className='h-8'>
        <svg width="98" height="96" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M48.854 0C21.839 0 0 22 0 49.217c0 21.756 13.993 40.172 33.405 46.69 2.427.49 3.316-1.059 3.316-2.362 0-1.141-.08-5.052-.08-9.127-13.59 2.934-16.42-5.867-16.42-5.867-2.184-5.704-5.42-7.17-5.42-7.17-4.448-3.015.324-3.015.324-3.015 4.934.326 7.523 5.052 7.523 5.052 4.367 7.496 11.404 5.378 14.235 4.074.404-3.178 1.699-5.378 3.074-6.6-10.839-1.141-22.243-5.378-22.243-24.283 0-5.378 1.94-9.778 5.014-13.2-.485-1.222-2.184-6.275.486-13.038 0 0 4.125-1.304 13.426 5.052a46.97 46.97 0 0 1 12.214-1.63c4.125 0 8.33.571 12.213 1.63 9.302-6.356 13.427-5.052 13.427-5.052 2.67 6.763.97 11.816.485 13.038 3.155 3.422 5.015 7.822 5.015 13.2 0 18.905-11.404 23.06-22.324 24.283 1.78 1.548 3.316 4.481 3.316 9.126 0 6.6-.08 11.897-.08 13.526 0 1.304.89 2.853 3.316 2.364 19.412-6.52 33.405-24.935 33.405-46.691C97.707 22 75.788 0 48.854 0z" fill="#24292f" /></svg>
    </div>
)
const isDev = process.env.DEV ? true : false
const frontendHost = isDev ? 'http://localhost:3000' : 'https://notebook-flame.vercel.app'


export default function GithubConnection({ installation }: { installation: any[] }) {
    const GITHUB_APP_URL = `https://github.com/apps/turntable-cloud`

    const router = useRouter()
    const searchParams = useSearchParams()
    const installationId = searchParams.get('installation_id')

    console.log({ installation })

    useEffect(() => {
        const installGithubApp = async (installationId: string) => {
            const data = await createGithubInstallation({ installationId })
            if (data.installation_id) {
                router.replace('/settings')
            }
        }

        if (installationId) {
            installGithubApp(installationId)
        }
    }, [installationId])
    // < div className = 'bg-black p-2 rounded-lg mr-2' >
    //     <Github className='text-white' />
    //         </div >
    // <div>Github App</div>
    return (
        <div className='w-full text-black'>
            <Card className="w-full rounded-sm">
                <CardHeader>
                    <CardTitle className='text-xl'>
                        <div className='flex items-center'>
                            <Code className='mr-2' />
                            Repository Access
                        </div>
                    </CardTitle>
                    <CardDescription>
                        Used for code-backed data models like dbt Core
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {installation ? (
                        <div className='py-3 border text-sm px-2 rounded-lg'>
                            <div className='flex items-center space-x-2'>
                                <div className='opacity-70 w-fit bg-black p-2 rounded-full'>
                                    <Github className='text-white size-5' />
                                </div>
                                <div>
                                    <div className='font-semibold text-black'>
                                        Turntable Cloud
                                    </div>
                                    <a target='_blank' href={GITHUB_APP_URL} className='flex items-center text-gray-600 font-medium hover:opacity-60 cursor-pointer'>View Installation <ExternalLink className='size-3 ml-1' /></a>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <a href={GITHUB_APP_URL} target='_blank'>
                            <Button>
                                <Github className='text-white size-5 mr-2' />
                                Connect to Github
                            </Button>
                        </a>
                    )}
                </CardContent>
                <CardFooter className="flex justify-between">

                </CardFooter>
            </Card>

        </div >
    )
}

// { installation ? (
//     <Badge variant='secondary'>connected</Badge>
// ) : (
//     <div className='py-8 text-center'>
//         <Button onClick={() => window.location.href = GITHUB_APP_URL}>
//             <Github className='size-5 mr-2' />
//             Connect Github App
//         </Button>
//     </div >
// )}