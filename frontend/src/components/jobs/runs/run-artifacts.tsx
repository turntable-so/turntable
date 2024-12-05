import type { Run } from "@/app/actions/actions";
import { Button } from "@/components/ui/button";
import { useState } from "react";

type RunArtifactsProps = {
  run: Run;
};

export default function RunArtifacts({ run }: RunArtifactsProps) {
  const artifacts = run.artifacts;
  const [loadingArtifactIds, setLoadingArtifactIds] = useState<string[]>([]);

  const downloadFile = async (
    url: string,
    filename: string,
    artifactId: string,
  ) => {
    try {
      setLoadingArtifactIds((prev) => [...prev, artifactId]);

      const response = await fetch(url, {
        mode: "cors",
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
      console.error("Download failed:", error);
    } finally {
      setLoadingArtifactIds((prev) => prev.filter((id) => id !== artifactId));
    }
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Artifacts</h2>
      {artifacts.length > 0 ? (
        <ul className="space-y-2">
          {artifacts.map((artifact) => {
            const isLoading = loadingArtifactIds.includes(artifact.id);

            return (
              <li key={artifact.id} className="flex items-center space-x-4">
                <span className="flex-1">{artifact.artifact_type}</span>
                <Button
                  onClick={() =>
                    downloadFile(
                      artifact.artifact,
                      `${artifact.artifact_type}.zip`,
                      artifact.id,
                    )
                  }
                  disabled={isLoading}
                >
                  {isLoading ? "Loading..." : "Download"}
                </Button>
              </li>
            );
          })}
        </ul>
      ) : (
        <p>No artifacts available.</p>
      )}
    </div>
  );
}
