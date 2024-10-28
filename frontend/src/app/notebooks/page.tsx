import NotebookList from "@/components/notebook-list";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { getResourceIcon } from "@/lib/utils";
import { formatDistance, subDays } from "date-fns";
import dayjs from "dayjs";
import { Badge, Notebook, Plus } from "lucide-react";
import { unstable_noStore as noStore } from "next/cache";
import Link from "next/link";
import FullWidthPageLayout from "../../components/layout/FullWidthPageLayout";
import { getNotebooks, getResources } from "../actions/actions";
import CreateNotebookButton from "./CreateNotebookButton";

export default async function NotebooksPage() {
  const notebooks = (await getNotebooks()) || [];

  return (
    <FullWidthPageLayout title="Projects" button={<CreateNotebookButton />}>
      <NotebookList notebooks={notebooks} />
    </FullWidthPageLayout>
  );
}
