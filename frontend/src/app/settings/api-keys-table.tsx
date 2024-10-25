import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { updateSettings } from "../actions/actions";
import type { Settings } from "./types";

type ApiKeysProps = {
  apiKeys: Settings["api_keys"];
};

export function ApiKeysTable({ apiKeys }: ApiKeysProps) {
  const { register, handleSubmit, setValue } = useForm<ApiKeysProps>({
    defaultValues: {
      apiKeys,
    },
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (data: ApiKeysProps) => {
    setIsLoading(true);
    setError(null);

    try {
      await updateSettings({
        api_keys: data.apiKeys,
      });
    } catch (err) {
      setError("An error occurred while updating the API keys.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    setValue("apiKeys", apiKeys);
  }, [apiKeys]);

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div className="flex flex-col gap-4">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>API Key Name</TableHead>
              <TableHead>API Key Value</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {Object.entries(apiKeys).map(([key, value]) => (
              <TableRow key={key}>
                <TableCell className="font-semibold">{key}</TableCell>
                <TableCell>
                  <Input
                    className="w-2/3"
                    defaultValue={value}
                    {...register(`apiKeys.${key}`)}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        <div className="flex justify-end gap-4 items-center">
          {error && <p className="text-red-500">{error}</p>}
          <Button type="submit" disabled={isLoading}>
            {isLoading ? (
              <div className="flex items-center gap-2">
                <Loader2 className="animate-spin" />
                Saving
              </div>
            ) : (
              "Save"
            )}
          </Button>
        </div>
      </div>
    </form>
  );
}
