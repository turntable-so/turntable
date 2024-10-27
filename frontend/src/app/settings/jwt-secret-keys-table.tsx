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
import { capitalize } from "lodash";
import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { updateSettings } from "../actions/actions";
import type { Settings } from "./types";

type JwtSecretKeysProps = {
  jwtSharedSecrets: Settings["jwt_shared_secrets"];
};

export function JwtSecretKeysTable({ jwtSharedSecrets }: JwtSecretKeysProps) {
  const { register, handleSubmit, setValue } = useForm<JwtSecretKeysProps>({
    defaultValues: {
      jwtSharedSecrets,
    },
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (data: JwtSecretKeysProps) => {
    setIsLoading(true);
    setError(null);

    try {
      await updateSettings({
        jwt_shared_secrets: data.jwtSharedSecrets,
      });
    } catch (err) {
      setError("An error occurred while updating the JWT secret keys.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    setValue("jwtSharedSecrets", jwtSharedSecrets);
  }, [jwtSharedSecrets]);

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div className="flex flex-col gap-4">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Service</TableHead>
              <TableHead>JWT Secret Key</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {Object.entries(jwtSharedSecrets).map(([key, value]) => (
              <TableRow key={key}>
                <TableCell className="font-semibold">
                  {capitalize(key)}
                </TableCell>
                <TableCell>
                  <Input
                    className="w-2/3"
                    defaultValue={value}
                    {...register(`jwtSharedSecrets.${key}`)}
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
