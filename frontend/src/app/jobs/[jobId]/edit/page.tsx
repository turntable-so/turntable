
'use client'

import { getJob } from "@/app/actions/actions"
import JobForm from "@/components/jobs/job-form"
import { useEffect, useState } from "react"

export default function EditJobPage({ params }: { params: { jobId: string } }) {
    const [job, setJob] = useState(null)
    useEffect(() => {
        const fetchJob = async () => {
            const res = await getJob(params.jobId)
            if (res.id) {
                setJob(res as any)
            }
        }
        fetchJob()
    }, [])

    if (!job) {
        return null
    }

    console.log({ job })

    return (
        <JobForm title={`Edit ${job.name}`} job={job} job={job} />
    )
}