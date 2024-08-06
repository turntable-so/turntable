"use server";

import { fetchApi } from '../../lib/api'
import { revalidateTag } from 'next/cache'
import { fetcher } from '@/app/fetcher'
import { cookies } from 'next/headers'

const isDev = process.env.DEV ? true : false;

const ApiHost = isDev
  ? "http://localhost:8000"
  : "https://notebook-backend-e9y5.onrender.com";

type CookiesContext = {
  cookies: any | undefined;
};



export async function createWorkspace({ name, iconUrl }: { name: string, iconUrl: string }) {
  const response = await fetcher(
    '/workspaces/',
    {
      cookies,
      next: {
        tags: ["workspaces"],
      },
      method: 'POST',
      body: {
        name,
        iconUrl,
      }
    }
  )
  if (response.ok) {
    return response.json();
  }
  return null;
}

type CreateNotebookArgs = {
  title: string
  json_contents: string
}

export async function createNotebook({ title, json_contents }: CreateNotebookArgs) {
  const response = await fetcher(`/notebooks/`, {
    cookies,
    method: "POST",
    next: {
      tags: ["notebooks"],
    },
    body: {
      title,
      contents: json_contents,
    },
  });
  const notebook = await response.json();
  revalidateTag("notebooks");
  return notebook;
}

export async function updateNotebook(notebookId: string, { json_contents, title }: { json_contents?: string, title?: string }) {
  const response = await fetcher(`/notebooks/${notebookId}/`, {
    cookies,
    method: "PUT",
    body: {
      ...(json_contents && { contents: json_contents }),
      ...(title && { title: title })
    },
  });
  return await response.json();
}

export async function getNotebooks() {
  const response = await fetcher(`/notebooks/`, {
    cookies,
    method: "GET",
    next: {
      tags: ["notebooks"],
    },
  });
  return await response.json();
}

export async function getNotebook(id: string) {
  const response = await fetcher(`/notebooks/${id}/`, {
    cookies,
    method: "GET",
  });

  return await response.json();
}

export async function getSources() {
  const response = await fetchApi(`${ApiHost}/sources`);
  const data = await response.json();

  return data["sources"];
}

export async function getAssets(resourceId: string) {
  const response = await fetcher(`/assets/?resource_id=${resourceId}`, {
    cookies,
    method: "GET",
    next: {
      tags: ["assets"],
    },
  });
  const data = await response.json();
  return data;
}
export async function getWorkspace() {
  const response = await fetcher("/workspaces/current/", {
    cookies,
    method: "GET",
  });
  const data = await response.json();
  return data;
}

export async function createSource() {
  const response = await fetchApi(`${ApiHost}/sources`, {
    next: {
      tags: ["sources"],
    },
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name: "dbt Project",
      type: "dbt_project",
    }),
  });
  const source = await response.json();
  revalidateTag("sources");
  return source.source;
}


export async function executeQuery({ notebook_id, resource_id, sql, block_id }: { resource_id: string, sql: string, block_id: string, notebook_id: string }) {
  const response = await fetcher(`/notebooks/${notebook_id}/blocks/${block_id}/query/`, {
    cookies,
    method: 'POST',
    body: JSON.stringify({
      resource_id,
      sql,
      limit: 10000,
    })
  })
  return await response.json()
}

export async function getWorkflow({ workflow_run_id }: { workflow_run_id: string }) {
  const response = await fetcher(`/workflows/${workflow_run_id}/`, {
    cookies,
    method: 'GET'
  })
  const data = await response.json()
  return data
}

export async function createBlock({
  type,
  notebook_id,
  sql,
  title,
  database,
}: {
  title: string;
  notebook_id: string;
  sql: string;
  database: string;
  type: "query" | "prompt";
}) {
  const response = await fetchApi(
    `${ApiHost}/notebooks/${notebook_id}/blocks`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        notebook_id,
        title,
        type,
        sql,
        database,
      }),
    }
  );
  const block = await response.json();
  return block;
}

export async function createGithubInstallation({
  installationId,
}: {
  installationId: string;
}) {
  console.log("createGithubInstallation", {
    installation_id: installationId,
  });
  const response = await fetchApi(
    `${ApiHost}/github_installations`,
    {
      method: "POST",
    },
    {
      installation_id: installationId,
    }
  );
  const text = await response.text();
  console.log({ text });
  if (response.ok) {
    revalidateTag("github");
    const data = await response.json();
    return data;
  } else {
    return null;
  }
}

export async function getGithubInstallation() {
  const response = await fetchApi(`${ApiHost}/github_installations`, {
    method: "GET",
    next: {
      tags: ["github"],
    },
  });
  if (response.ok) {
    const data = await response.json();
    return data;
  } else {
    return null;
  }
}

export async function getGithubRepos() {
  const response = await fetchApi(`${ApiHost}/github/repos`, {
    method: "GET",
    next: {
      tags: ["github"],
    },
  });
  if (response.ok) {
    const data = await response.json();
    return data["repos"];
  } else {
    return null;
  }
}

export async function getGithubInstallations() {
  const response = await fetcher(`/github/`, {
    cookies,
    method: "GET",
    next: {
      tags: ["github"],
    },
  });
  return response.json();
}


export async function getLineage({
  nodeId,
  successor_depth,
  predecessor_depth,
  lineage_type,
}: {
  nodeId: string;
  successor_depth: number;
  predecessor_depth: number;
  lineage_type: "all" | "direct_only";
}) {
  const response = await fetcher(
    `/lineage/${nodeId}?predecessor_depth=${predecessor_depth}&successor_depth=${successor_depth}&lineage_type=${lineage_type}`,
    {
      cookies,
      method: "GET",
    }
  );
  return await response.json();
}

export async function createGithubConnection(data: any) {
  const response = await fetcher(`/github/`, {
    method: "POST",
    body: data,
    cookies,
    next: {
      tags: ["github"],
    },
  });
  return response.json();
}

export async function getAssetPreview(assetId: string) {
  const response = await fetcher(`/assets/${assetId}/`, {
    cookies,
    method: "GET",
    next: {
      tags: ["assets"],
    },
  });
  const data = await response.json();
  return data;
}

export async function getResources() {
  const response = await fetcher("/resources/", {
    cookies,
    next: {
      tags: ["resources"],
    },
    method: "GET",
  });
  return response.json();
}

export async function getSshKey(tenant_id: string) {
  const response = await fetcher(
    `/ssh/?action=generate_ssh_key&tenant_id=${tenant_id}`,
    {
      cookies,
      method: "GET",
    }
  );

  return response.json();
}

export async function testGithubConnection(public_key: string, github_url: string) {
  const response = await fetcher(
    `/ssh/`,
    {
      cookies,
      method: "POST",
      body: {
        public_key,
        github_url,
        action: "test_github_connection",
      },
    }
  );

  return response.json();
}


export async function createResource({
  authProfileId,
  dbtVersion,
  dialect,
  githubRepositoryId,
  project,
  dataset,
  threads,
  dbtProjectPath,
  url,
  environment,
  name,
  type,
}: {
  authProfileId: string;
  dbtVersion?: string;
  dbtProjectPath?: string;
  dialect?: string;
  githubRepositoryId?: string;
  project?: string;
  dataset?: string;
  threads?: string;
  url?: string;
  environment?: string;
  name: string;
  type: string;
}) {
  const response = await fetchApi(
    `${ApiHost}/resources`,
    {
      next: {
        tags: ["resources"],
      },
      method: "POST",
    },
    {
      auth_profile_id: authProfileId,
      dbt_version: dbtVersion || "",
      dialect,
      github_repository_id: githubRepositoryId || "",
      dbt_project_path: dbtProjectPath || "",
      project: project || "",
      dataset: dataset || "",
      threads: threads || "",
      url: url || "",
      environment: environment || "",
      name,
      type,
    }
  );
  const data = await response.json();
  return data;
}

export async function createAuthProfile({
  name,
  description,
  service_account_key,
}: {
  name: string;
  description: string;
  service_account_key: any;
}) {
  const response = await fetcher(`/profiles/`, {
    cookies,
    method: "POST",
    next: {
      tags: ["profiles"],
    },
    body: {
      name: name,
      description: description,
      service_account_key: JSON.stringify(service_account_key),
    },
  });
  if (response.ok) {
    const data = await response.json();
    revalidateTag("profiles");
    return data;
  } else {
    return null;
  }
}

export async function getAuthProfiles() {
  const response = await fetcher(`/profiles/`, {
    cookies,
    next: {
      tags: ["profiles"],
    },
    method: "GET",
  });
  return response.json();
}

export async function deleteAuthProfile(id: string) {
  const response = await fetcher(`/profiles/${id}/`, {
    cookies,
    next: {
      tags: ["profiles"],
    },
    method: "DELETE",
  });
  revalidateTag("profiles");
  return response.ok;
}

export async function testConnection({
  name,
  description,
  service_account_key,
}: {
  name: string;
  description: string;
  service_account_key: string | undefined;
}) {
  const response = await fetchApi(
    `${ApiHost}/profiles/test`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    },
    {
      name: name,
      description: description,
      service_account_key: JSON.stringify(service_account_key),
    }
  );
  const data = await response.json();
  console.log({ data });
  return data;
}

export async function getColumnAutocomplete({
  resourceId,
  beforeSql,
  afterSql,
  schemaList = null,
}: {
  resourceId: string;
  beforeSql: string;
  afterSql: string;
  schemaList?: string[] | null;
}) {
  try {
    const response = await fetchApi(
      `${ApiHost}/${resourceId}/completion/column`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          before_sql: beforeSql,
          after_sql: afterSql,
          schema_list: schemaList,
        }),
      }
    );
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(error);
    return [];
  }
}

export const getTableAutocomplete = async ({
  resourceId,
  beforeSql,
  afterSql,
  schemaList = null,
}: {
  resourceId: string;
  beforeSql: string;
  afterSql: string;
  schemaList?: string[] | null;
}) => {
  try {
    const response = await fetchApi(
      `${ApiHost}/${resourceId}/completion/table`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          before_sql: beforeSql,
          after_sql: afterSql,
          schema_list: schemaList,
        }),
      }
    );
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(error);
    return { ctes: [], tables: [] };
  }
};

export async function getSchemaAutocomplete({
  resourceId,
}: {
  resourceId: string;
}) {
  try {
    const response = await fetchApi(
      `${ApiHost}/${resourceId}/completion/schema`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    const data = await response.json();
    return data;
  } catch (error) {
    console.log("entro error");
    console.error(error);
    return [];
  }
}

export async function getDBCatalogAutocomplete({
  resourceId,
}: {
  resourceId: string;
}) {
  try {
    const response = await fetchApi(
      `${ApiHost}/${resourceId}/completion/table/catalog`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          schema_list: null,
        }),
      }
    );

    const data = await response.json();
    return data;
  } catch (error) {
    console.log("entro error");
    console.error(error);
    return [];
  }
}

export async function getCTEAutocomplete({
  resourceId,
  beforeSql,
  afterSql,
  schemaList = null,
}: {
  resourceId: string;
  beforeSql: string;
  afterSql: string;
  schemaList?: string[] | null;
}) {
  try {
    const response = await fetchApi(
      `${ApiHost}/${resourceId}/completion/table/cte`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          before_sql: beforeSql,
          after_sql: afterSql,
          schema_list: schemaList,
        }),
      }
    );

    const data = await response.json();
    return data;
  } catch (error) {
    console.log("entro error");
    console.error(error);
    return [];
  }
}
