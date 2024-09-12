"use server";

import { fetcher } from '@/app/fetcher';
import { revalidateTag } from 'next/cache';
import { cookies } from 'next/headers';

const isDev = process.env.DEV ? true : false;

const ApiHost = isDev
  ? "http://localhost:8000"
  : process.env.BACKEND_HOST;

type CookiesContext = {
  cookies: any | undefined;
};



export async function createWorkspace(body: FormData) {
  const response = await fetcher(
    '/workspaces/',
    {
      cookies,
      next: {
        tags: ["workspaces"],
      },
      method: 'POST',
      body,
    }
  )
  const data = await response.json();
  revalidateTag("workspaces");
  return data;
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

export async function getWorkspaces() {
  const response = await fetcher("/workspaces/", {
    cookies,
    method: "GET",
  });
  const data = await response.json();
  return data;
}

export async function switchWorkspace(workspaceId: string) {
  const response = await fetcher(`/workspaces/switch_workspace/`, {
    cookies,
    method: "POST",
    body: {
      workspace_id: workspaceId,
    },
  });
  const data = await response.json();
  return data;
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

export async function testResource(resourceId: string) {
  const response = await fetcher(`/resources/${resourceId}/test/`, {
    cookies,
    method: "POST",
  });
  return response.json();
}

export async function getResource(id: string) {
  const response = await fetcher(`/resources/${id}/`, {
    cookies,
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

export async function testGitConnection(public_key: string, git_repo_url: string) {
  const response = await fetcher(
    `/ssh/`,
    {
      cookies,
      method: "POST",
      body: {
        public_key,
        git_repo_url,
        action: "test_git_connection",
      },
    }
  );

  return response.json();
}

type CreateResourcePayload = {
  resource: {
    name: string
    type: string
  }
  subtype: string
  config: object
}

export async function createResource(payload: CreateResourcePayload) {

  const response = await fetcher(`/resources/`, {
    cookies,
    method: "POST",
    next: {
      tags: ["resources"],
    },
    body: payload
  });
  if (response.ok) {
    revalidateTag("resources");
    const data = await response.json();
    console.log({ data })

    return data
  } else {
    return false
  }
}

export async function updateResource(id: string, payload: any) {
  const response = await fetcher(`/resources/${id}/`, {
    cookies,
    method: "PATCH",
    next: {
      tags: ["resources"],
    },
    body: payload
  });

  const data = await response.json();
  return data;
}

export async function deleteResource(id: string) {
  const response = await fetcher(`/resources/${id}/`, {
    cookies,
    method: "DELETE",
    next: {
      tags: ["resources"],
    },
  });
  if (response.ok) {
    revalidateTag("resources");
    return {
      success: true,
    };
  }
  return {
    success: false,
  };
}

export async function syncResource(id: string) {
  const response = await fetcher(`/resources/${id}/sync/`, {
    cookies,
    method: "POST",
    next: {
      tags: ["resources"],
    },
  });
  if (response.ok) {
    revalidateTag("resources");
    return {
      success: true,
    };
  }
  return {
    success: false,
  };
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
