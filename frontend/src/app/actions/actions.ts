"use server";

import { fetcher } from "@/app/fetcher";
import getUrl from "@/app/url";
import { revalidateTag } from "next/cache";
import { cookies } from "next/headers";
import type { Settings } from "../settings/types";

export async function createWorkspace(body: FormData) {
  const response = await fetcher("/workspaces/", {
    cookies,
    next: {
      tags: ["workspaces"],
    },
    method: "POST",
    body,
  });
  const data = await response.json();
  revalidateTag("workspaces");
  return data;
}

type CreateNotebookArgs = {
  title: string;
  json_contents: string;
};

export async function createNotebook({
  title,
  json_contents,
}: CreateNotebookArgs) {
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

export async function updateNotebook(
  notebookId: string,
  { json_contents, title }: { json_contents?: string; title?: string },
) {
  const response = await fetcher(`/notebooks/${notebookId}/`, {
    cookies,
    method: "PUT",
    body: {
      ...(json_contents && { contents: json_contents }),
      ...(title && { title: title }),
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

export async function getAssets({
  query,
  page,
  sources,
  tags,
  types,
  sortBy,
  sortOrder,
}: {
  query: string;
  page: number;
  sources?: string[];
  tags?: string[];
  types?: string[];
  sortBy?: string;
  sortOrder?: "asc" | "desc";
}) {
  let url = `/assets/?q=${encodeURIComponent(query)}&page=${page}`;

  if (sources && sources.length > 0) {
    url += `&resources=${sources.map(encodeURIComponent).join(",")}`;
  }

  if (tags && tags.length > 0) {
    url += `&tags=${tags.map(encodeURIComponent).join(",")}`;
  }

  if (types && types.length > 0) {
    url += `&types=${types.map(encodeURIComponent).join(",")}`;
  }

  if (sortBy && sortOrder) {
    url += `&sort_by=${sortBy}&sort_order=${sortOrder}`;
  }

  const response = await fetcher(url, {
    cookies,
    method: "GET",
    next: {
      tags: ["assets"],
    },
  });
  const data = await response.json();
  return data;
}

export async function getColumns({
  query,
  page,
  sources,
  tags,
  types,
}: {
  query: string;
  page: number;
  sources?: string[];
  tags?: string[];
  types?: string[];
}) {
  let url = `/columns/?q=${encodeURIComponent(query)}&page=${page}`;

  if (sources && sources.length > 0) {
    url += `&resources=${sources.map(encodeURIComponent).join(",")}`;
  }

  if (tags && tags.length > 0) {
    url += `&tags=${tags.map(encodeURIComponent).join(",")}`;
  }

  if (types && types.length > 0) {
    url += `&types=${types.map(encodeURIComponent).join(",")}`;
  }

  const response = await fetcher(url, {
    cookies,
    method: "GET",
    next: {
      tags: ["columns"],
    },
  });
  const data = await response.json();
  return data;
}

export async function getAssetIndex() {
  const response = await fetcher("/assets/index/", {
    cookies,
    method: "GET",
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
    },
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
    },
  );

  return response.json();
}

export async function testGitConnection(
  public_key: string,
  git_repo_url: string,
) {
  const response = await fetcher(`/ssh/`, {
    cookies,
    method: "POST",
    body: {
      public_key,
      git_repo_url,
      action: "test_git_connection",
    },
  });

  return response.json();
}

type CreateResourcePayload = {
  resource: {
    name: string;
    type: string;
  };
  subtype: string;
  config: object;
};

export async function createResource(payload: CreateResourcePayload) {
  const response = await fetcher(`/resources/`, {
    cookies,
    method: "POST",
    next: {
      tags: ["resources"],
    },
    body: payload,
  });
  if (response.ok) {
    revalidateTag("resources");
    const data = await response.json();

    return data;
  } else {
    return false;
  }
}

export async function updateResource(id: string, payload: any) {
  const response = await fetcher(`/resources/${id}/`, {
    cookies,
    method: "PUT",
    next: {
      tags: ["resources"],
    },
    body: payload,
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

export async function getSettings() {
  const response = await fetcher(`/settings/`, {
    cookies,
    method: "GET",
  });
  return response.json();
}

export async function updateSettings(settings: Partial<Settings>) {
  const response = await fetcher(`/settings/`, {
    cookies,
    method: "POST",
    body: settings,
  });
  return response.json();
}

export async function getBackendUrl() {
  return getUrl();
}

export async function getBranches() {
  const response = await fetcher(`/project/branches/`, {
    cookies,
    method: "GET",
  });
  return response.json();
}

export async function createBranch(
  branchName: string,
  sourceBranch: string,
  schema: string,
) {
  const response = await fetcher(`/project/branches/`, {
    cookies,
    method: "POST",
    body: {
      branch_name: branchName,
      source_branch: sourceBranch,
      schema: schema,
    },
  });
  return response.json();
}

export async function getFileIndex(branchId: string) {
  const response = await fetcher(`/project/${branchId}/files/`, {
    cookies,
    method: "GET",
  });
  return response.json();
}

export async function fetchFileContents({
  branchId,
  path,
}: {
  branchId: string;
  path: string;
}) {
  const encodedPath = encodeURIComponent(path);
  const response = await fetcher(
    `/project/${branchId}/files/?filepath=${encodedPath}`,
    {
      cookies,
      method: "GET",
    },
  );
  return response.json();
}

type DbtQueryPreview = {
  signed_url: string;
  error?: string;
};

export async function executeQueryPreview({
  dbtSql,
  branchId,
}: {
  dbtSql: string;
  branchId: string;
}): Promise<DbtQueryPreview> {
  const response = await fetcher(`/query/dbt/`, {
    cookies,
    method: "POST",
    body: {
      query: dbtSql,
      project_id: branchId,
      use_fast_compile: true,
    },
  });
  return response.json();
}

type PersistFileArgs = {
  branchId: string;
  filePath: string;
  fileContents: string;
  format?: boolean;
};

export async function persistFile({
  branchId,
  filePath,
  fileContents,
  format,
}: PersistFileArgs) {
  const response = await fetcher(
    `/project/${branchId}/files/?filepath=${filePath}`,
    {
      cookies,
      method: "PUT",
      body: {
        contents: fileContents,
        ...(format !== undefined && { format }),
      },
    },
  );
  return response.json();
}

export async function changeFilePath(
  branchId: string,
  filePath: string,
  newPath: string,
) {
  const response = await fetcher(
    `/project/${branchId}/files/?filepath=${filePath}`,
    {
      cookies,
      method: "PATCH",
      body: {
        new_path: newPath,
      },
    },
  );
  return response.ok;
}

export async function createFile(
  branchId: string,
  path: string,
  isDirectory: boolean,
  fileContents: string,
) {
  const response = await fetcher(
    `/project/${branchId}/files/?filepath=${path}`,
    {
      cookies,
      method: "POST",
      body: {
        contents: fileContents,
        is_directory: isDirectory,
      },
    },
  );
  return response.ok;
}

export async function deleteFile(branchId: string, filePath: string) {
  const response = await fetcher(
    `/project/${branchId}/files/?filepath=${filePath}`,
    {
      cookies,
      method: "DELETE",
    },
  );
  return response.ok;
}

export async function duplicateFileOrFolder({
  branchId,
  filePath,
}: {
  branchId: string;
  filePath: string;
}) {
  const response = await fetcher(`/project/${branchId}/files/duplicate/`, {
    cookies,
    method: "POST",
    body: {
      filepath: filePath,
    },
  });
  return response.ok;
}

export async function infer({
  instructions,
  content,
  filepath,
}: {
  instructions: string;
  content: string;
  filepath: string;
}) {
  const response = await fetcher(`/infer/`, {
    cookies,
    method: "POST",
    body: {
      instructions,
      content,
      filepath,
    },
  });
  return response.json();
}

export async function getProjectBasedLineage({
  branchId,
  filePath,
  lineage_type,
  successor_depth,
  predecessor_depth,
}: {
  branchId: string;
  filePath: string;
  lineage_type: "all" | "direct_only";
  successor_depth: number;
  predecessor_depth: number;
}) {
  const encodedPath = encodeURIComponent(filePath);
  const response = await fetcher(
    `/project/${branchId}/lineage/?filepath=${encodedPath}&predecessor_depth=${predecessor_depth}&successor_depth=${successor_depth}&lineage_type=${lineage_type}`,
    {
      cookies,
      method: "GET",
    },
  );
  return response.json();
}

export async function getMetabaseEmbedUrlForAsset(assetId: string) {
  const response = await fetcher(`/embedding/metabase/?asset_id=${assetId}`, {
    cookies,
    method: "GET",
  });
  return response.json();
}

export async function makeMetabaseAssetEmbeddable(assetId: string) {
  const response = await fetcher(
    `/embedding/metabase_make_embeddable/?asset_id=${assetId}`,
    {
      cookies,
      method: "POST",
    },
  );
  return response.json();
}

export type ProjectChanges = {
  untracked: Array<{
    path: string;
    before: string;
    after: string;
  }>;
  modified: Array<{
    path: string;
    before: string;
    after: string;
  }>;
  deleted: Array<{
    path: string;
    before: string;
    after: string;
  }>;
};

export async function getProjects() {
  const response = await fetcher(`/project/`, {
    cookies,
    method: "GET",
  });
  return response.json();
}

export async function getBranch(id: string) {
  const response = await fetcher(`/project/${id}/`, {
    cookies,
    method: "GET",
  });
  return response.json();
}

export async function getProjectChanges(
  branchId: string,
): Promise<ProjectChanges> {
  const response = await fetcher(`/project/${branchId}/changes/`, {
    cookies,
    method: "GET",
  });

  return response.json();
}

export async function cloneBranchAndMount(branchId: string) {
  const response = await fetcher(`/project/${branchId}/clone/`, {
    cookies,
    method: "POST",
  });
  return response.ok;
}

export async function commit(
  branchId: string,
  commitMessage: string,
  filePaths: string[],
) {
  const response = await fetcher(`/project/${branchId}/commit/`, {
    cookies,
    method: "POST",
    body: { commit_message: commitMessage, file_paths: filePaths },
  });
  return response.ok;
}

export async function discardBranchChanges(branchId: string) {
  const response = await fetcher(`/project/${branchId}/discard/`, {
    cookies,
    method: "POST",
  });
  return response.ok;
}

export async function formatDbtQuery(payload: { query: string }) {
  const response = await fetcher("/query/format/", {
    cookies,
    method: "POST",
    body: payload,
  });
  return response.json();
}

export async function compileDbtQuery(
  project_id: string,
  payload: {
    filepath: string;
  },
) {
  const response = await fetcher(`/project/${project_id}/compile/`, {
    cookies,
    method: "POST",
    body: payload,
  });
  return await response.json();
}
