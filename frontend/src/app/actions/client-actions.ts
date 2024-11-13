"use client";

import { fetcher } from "@/app/fetcher";

export async function executeQuery(
  {
    notebook_id,
    resource_id,
    sql,
    block_id,
  }: { resource_id: any; sql: string; block_id: string; notebook_id: string },
  signal: any = null,
) {
  try {
    const response = await fetcher(
      `/notebooks/${notebook_id}/blocks/${block_id}/query/`,
      {
        method: "POST",
        body: JSON.stringify({
          resource_id,
          sql,
          limit: 10000,
        }),
      },
      signal,
    );
    return await response.json();
  } catch (error) {
    console.error("Error in executeQuery:", error);
    throw error; // Re-throw to be caught in runQuery
  }
}

export async function getWorkflow(
  { task_id }: { task_id: string },
  signal: any = null,
) {
  const response = await fetcher(
    `/workflows/${task_id}/`,
    {
      method: "GET",
    },
    signal,
  );
  const data = await response.json();
  return data;
}

type DbtQueryValidateInput = {
  query: string;
  project_id: string;
  use_fast_compile?: boolean;
  limit?: number;
};

export async function validateDbtQuery(
  input: DbtQueryValidateInput,
  signal?: AbortSignal,
) {
  console.log("MAKING API CALL!!!", input);
  const response = await fetcher(
    "/validate/dbt/",
    {
      method: "POST",
      body: input,
    },
    signal,
  );
  return response.json();
}
