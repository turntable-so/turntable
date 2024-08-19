"use client";

import { fetcher } from '@/app/fetcher'

const isDev = process.env.DEV ? true : false;


export async function executeQuery({ notebook_id, resource_id, sql, block_id }: { resource_id: any, sql: string, block_id: string, notebook_id: string}, signal : any = null) {
  try {
    const response = await fetcher(`/notebooks/${notebook_id}/blocks/${block_id}/query/`, {
      method: 'POST',
      body: JSON.stringify({
        resource_id,
        sql,
        limit: 10000,
      }),
    }, signal);
    return await response.json();
  }catch (error) {
    console.error("Error in executeQuery:", error);
    throw error; // Re-throw to be caught in runQuery
  }
}

export async function getWorkflow({ workflow_run_id }: { workflow_run_id: string }, signal : any = null) {
  const response = await fetcher(`/workflows/${workflow_run_id}/`, {
    method: 'GET'
  }, signal)
  const data = await response.json()
  return data
}