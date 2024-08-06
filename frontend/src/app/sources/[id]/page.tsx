'use client'
import { createAuthProfile, createResource, getAuthProfiles, getGithubRepos } from "../../actions/actions"
import FullWidthPageLayout from "../../../components/layout/FullWidthPageLayout"
import { Button } from "../../../components/ui/button"
import { useEffect, useState } from "react"
import { useRouter } from 'next/navigation'

import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "../../../components/ui/card"
import { Input } from "../../../components/ui/input"
import { ScrollArea } from "../../../components/ui/scroll-area"
import { Github, Loader2, Search } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../components/ui/select"
import { LoaderButton } from "../../../components/ui/LoadingSpinner"
import { Textarea } from "../../../components/ui/textarea"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { DbtCorelogo } from "../../../components/sources/AddNewSourceSection"
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "../../../components/ui/form"

const formSchema = z.object({
    repositoryId: z.string({
        required_error: 'Please select a repository'
    }),
    dialect: z.string({
        required_error: "Please select a dialect",
    }),
    dbtVersion: z.string({
        required_error: "Please select a dbt version",
    }),
    dbtProjectPath: z.string({
        required_error: "Please enter a dbt project path",
    }),
    authProfileId: z.string({
        required_error: "Please select a service account",
    }),
    project: z.string({
        required_error: "Please enter a project id",
    }),
    dataset: z.string({
        required_error: "Please enter a dataset",
    }),
    threads: z.string({
        required_error: "Please enter number of threads",
    }),
})

function DbtProjectForm() {
    const [authProfiles, setAuthProfiles] = useState<any>([])
    const [githubReposLoading, setGithubReposLoading] = useState<boolean>(true)
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
    const [githubRepos, setGithubRepos] = useState<any>([])
    const [selectedRepoIndex, setSelectedRepoIndex] = useState<any>(null)
    const [repoSearchQuery, setRepoSearchQuery] = useState<string>('')

    const router = useRouter()

    useEffect(() => {
        const fetchAuthProfiles = async () => {
            const data = await getAuthProfiles()
            if (data) {
                setAuthProfiles(data)
            }
        }
        fetchAuthProfiles()
    }, [])


    useEffect(() => {
        const fetchRepos = async () => {
            const data = await getGithubRepos()
            if (data) {
                setGithubRepos(data)
            }
            setGithubReposLoading(false)
        }
        fetchRepos()
    }, [])


    // 1. Define your form.
    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            dialect: 'bigquery'
        }

    })


    // 2. Define a submit handler.
    async function onSubmit(values: z.infer<typeof formSchema>) {
        // Do something with the form values.
        // ✅ This will be type-safe and validated.
        setIsSubmitting(true)
        const resp = await createResource({
            authProfileId: values.authProfileId,
            dbtVersion: values.dbtVersion,
            dbtProjectPath: values.dbtProjectPath,
            dialect: values.dialect,
            githubRepositoryId: values.repositoryId,
            project: values.project,
            dataset: values.dataset,
            threads: values.threads,
            name: '',
            type: ''
        })
        setIsSubmitting(false)
        if (resp.id) {
            router.push('/sources')
        }
    }

    console.log({ githubRepos })
    const filteredGithubRepos = githubRepos.filter((repo: any) => repo.name.toLowerCase().includes(repoSearchQuery.toLowerCase()))

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
                <Card className="w-full rounded-sm">
                    <CardHeader>
                        <CardTitle className='text-xl'>
                            <div className='flex items-center'>
                                Select Git Repository
                            </div>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className='h-[350px]'>
                            <div className='pb-4'>
                                <div className="relative flex items-center">
                                    <Search className="absolute left-3 top-1/5 h-4 w-4 text-muted-foreground" />
                                    <Input
                                        onChange={(e) => setRepoSearchQuery(e.target.value)}
                                        value={repoSearchQuery}
                                        type="search"
                                        placeholder="Search..."
                                        className="w-full rounded-lg bg-background pl-8 h-10"
                                    />
                                </div>
                            </div>
                            <FormField
                                control={form.control}
                                name="repositoryId"
                                render={({ field }) => (
                                    <FormItem>
                                        {githubReposLoading ? (
                                            <div className='h-48 flex justify-center items-center'>
                                                <Loader2 className='h-8 w-8 animate-spin opacity-20' />
                                            </div>
                                        ) : (
                                            <div className='space-y-2'>
                                                {filteredGithubRepos.slice(0, 5).map((repo: any, i: number) => (
                                                    <div key={i}
                                                        onClick={() => form.setValue('repositoryId', repo.id.toString())}
                                                        className={`
                                            ${form.getValues().repositoryId === repo.id.toString() && 'border-2 border-black'}
                                            hover:bg-muted/50 cursor-pointer py-3 border text-sm px-2 rounded-lg`}>
                                                        <div className='flex items-center space-x-2'>
                                                            <div className='w-fit bg-black p-2 rounded-full'>
                                                                <Github className='text-white size-3' />
                                                            </div>
                                                            <div>
                                                                <div className='font-semibold text-black'>
                                                                    {repo.owner.login}/{repo.name}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                        <FormMessage />
                                    </FormItem>

                                )}
                            />
                        </div>
                    </CardContent>
                    <CardFooter className="flex justify-end">
                    </CardFooter>
                </Card>
                <Card className="w-full rounded-sm">
                    <CardHeader>
                        <CardTitle className='text-xl'>
                            <div className='flex items-center space-x-0'>
                                <DbtCorelogo />
                                <div className='pt-0.5'>details</div>
                            </div>
                        </CardTitle>
                    </CardHeader>
                    <CardContent className='space-y-4'>
                        <FormField
                            control={form.control}
                            name="dialect"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Dialect</FormLabel>
                                    <FormControl>
                                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                                            <SelectTrigger className="w-full">
                                                <SelectValue placeholder="" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="bigquery">BigQuery</SelectItem>
                                                {/* <SelectItem value="snowflake">Snowflake</SelectItem> */}
                                                {/* <SelectItem value="postgres">Postgres</SelectItem> */}
                                                {/* <SelectItem value="redshift">Redshift</SelectItem> */}
                                            </SelectContent>
                                        </Select>
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="dbtVersion"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>dbt Core Version</FormLabel>
                                    <FormControl>
                                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                                            <SelectTrigger className="w-full">
                                                <SelectValue placeholder="" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="1.3">1.3</SelectItem>
                                                <SelectItem value="1.4">1.4</SelectItem>
                                                <SelectItem value="1.5">1.5</SelectItem>
                                                <SelectItem value="1.6">1.6</SelectItem>
                                                <SelectItem value="1.7">1.7</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="dbtProjectPath"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>dbt Project Path</FormLabel>
                                    <FormControl>
                                        <Input placeholder="dbt Project Path" {...field} defaultValue={"/"} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="authProfileId"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Service Account</FormLabel>
                                    <FormControl>
                                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                                            <SelectTrigger className="w-full">
                                                <SelectValue placeholder="" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {authProfiles.map((profile: any, i: number) => (
                                                    <SelectItem key={i} value={profile.id}>
                                                        {profile.name}
                                                    </SelectItem>

                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="project"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Project</FormLabel>
                                    <FormControl>
                                        <Input placeholder="" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="dataset"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Dataset</FormLabel>
                                    <FormControl>
                                        <Input placeholder="" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="threads"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Threads</FormLabel>
                                    <FormControl>
                                        <Input type='number' placeholder="" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                    </CardContent>
                    <CardFooter className="flex justify-end">
                    </CardFooter>
                </Card>
                <div className="float-right">
                    <LoaderButton isLoading={isSubmitting} isDisabled={isSubmitting} type="submit">Add Source</LoaderButton>
                </div>
            </form>
        </Form >
    )
}
export default function AddSourcePage() {

    const [currentStep, setCurrentStep] = useState<number>(0)

    const [selectedRepoIndex, setSelectedRepoIndex] = useState<any>(null)


    const ProjectDetailStep = () => {
        return (
            <div>
                <DbtProjectForm />
            </div>
        )
    }

    const steps = [
        {
            title: 'dbt Core Project',
        },


    ]
    const current = steps[currentStep]
    return (
        <div className='flex'>
            <div className='w-[300px] flex flex-col h-screen py-12 bg-muted text-muted-foreground px-4 space-y-6'>
                <div className='px-4 text-lg font-semibold'>
                    Add Source
                </div>
                <div className='space-y-4 py-1'>
                    {steps.map((tab: any, i: number) => (
                        <div key={i}>
                            <Button
                                onClick={() => setCurrentStep(i)}

                                variant={currentStep === i ? 'ghost' : 'ghost'}
                                size="icon"
                                className={`w-full rounded-lg ${currentStep === i ? 'opacity-100' : 'opacity-50'} ${currentStep === i ? 'text-black' : 'bg-transparent'} `}
                                aria-label={tab.title}
                            >
                                <div className={`${currentStep === i ? 'bg-[#ebebeb]' : 'hover:bg-[#ebebeb]'} px-4 p-2 rounded-lg w-full flex  space-x-2`}>
                                    <p className="font-normal text-[15px]">{tab.title}</p>
                                </div>
                            </Button>
                        </div>

                    ))}
                </div>
            </div >
            <ScrollArea className='w-full'>
                <FullWidthPageLayout title={current.title}>
                    {currentStep === 0 && <ProjectDetailStep />}
                </FullWidthPageLayout>
            </ScrollArea>
        </div >
    )
}