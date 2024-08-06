'use client'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../../components/ui/card"
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuLabel, DropdownMenuItem } from "../../components/ui/dropdown-menu"
import { MoreHorizontal, Lock } from "lucide-react"
import { deleteAuthProfile } from "../actions/actions"
import { Button } from "../../components/ui/button"
import Link from 'next/link'

export default function AuthenticationProfiles({ authProfiles }: { authProfiles: any[] }) {
    return (
        <div className='w-full text-black' >
            <Card className="w-full rounded-sm">
                <CardHeader>
                    <CardTitle className='text-xl'>
                        <div className='flex items-center'>
                            <Lock className='mr-2' />Secrets
                        </div>
                    </CardTitle>

                    <CardDescription>
                        Your secrets are encrypted and stored securely
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className='space-y-4'>
                        {authProfiles.map((profile: any, i: number) => (
                            <div key={i} className='py-3 border text-sm px-2 rounded-lg'>
                                <div className='px-2 py-2 flex items-center justify-between'>
                                    <div className='font-semibold'>{profile.name}</div>
                                    <div className='flex items-center space-x-2'>
                                        <div className='rounded-lg text-muted-foreground bg-gray-100 p-2'>
                                            <div className='font-mono text-xs flex items-center'>
                                                <Lock className='size-3 mr-2' />Contents are encrypted

                                            </div>
                                        </div>
                                        <div>
                                            <DropdownMenu>
                                                <DropdownMenuTrigger asChild>
                                                    <Button aria-haspopup="true" size="icon" variant="ghost">
                                                        <MoreHorizontal className="h-4 w-4" />
                                                        <span className="sr-only">Toggle menu</span>
                                                    </Button>
                                                </DropdownMenuTrigger>
                                                <DropdownMenuContent align="end">
                                                    <DropdownMenuItem onClick={() => deleteAuthProfile(profile.id)} className='text-red-500 font-bold cursor-pointer'>Delete</DropdownMenuItem>
                                                </DropdownMenuContent>
                                            </DropdownMenu>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
                <CardFooter className="flex justify-end">
                    <Link href='/settings/add_profile'>
                        <Button>Add Secret</Button>
                    </Link>
                </CardFooter>
            </Card>
        </div >
    )
}