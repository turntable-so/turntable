"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { getProjects } from "@/app/actions/actions";
import FullWidthPageLayout from "@/components/layout/FullWidthPageLayout";
import { ProjectButtons } from "@/components/projects/project-buttons";
import { ProjectTable } from "@/components/projects/project-table";
import type { FilterValue, Project } from "@/components/projects/types";

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const searchParams = useSearchParams();
  const filter = (searchParams.get("filter") || "active") as FilterValue;

  useEffect(() => {
    const fetchProjects = async () => {
      setIsLoading(true);
      const projects = await getProjects({ filter });
      setProjects(projects);
      setIsLoading(false);
    };
    fetchProjects();
  }, [filter]);

  return (
    <FullWidthPageLayout title="Projects" button={<ProjectButtons />}>
      <ProjectTable projects={projects} isLoading={isLoading} />
    </FullWidthPageLayout>
  );
}
