import FullWidthPageLayout from "../../components/layout/FullWidthPageLayout";
import { getNotebooks, getResources } from "../actions/actions";
import Link from "next/link";
import CreateNotebookButton from "./CreateNotebookButton";
import { formatDistance, subDays } from "date-fns";
import { unstable_noStore as noStore } from 'next/cache';
import { Card, CardDescription, CardFooter, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getResourceIcon } from "@/lib/utils";
import dayjs from "dayjs";
import { Badge, Notebook, Plus } from "lucide-react";
import NotebookList from "@/components/notebook-list";



export default async function NotebooksPage() {

    const notebooks = await getNotebooks() || []

    return (
        <FullWidthPageLayout title='Projects' button={
            <CreateNotebookButton />
        }>
            <NotebookList notebooks={notebooks} />
        </FullWidthPageLayout >
    )
}
