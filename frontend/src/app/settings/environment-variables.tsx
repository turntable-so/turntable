import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Minus, Plus } from "lucide-react";
import { useEffect, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { z } from "zod";
import { updateSettings } from "../actions/actions";
import type { Settings } from "./types";

type EnvironmentVariablesProps = {
  env: Settings["env"];
};

const keySchema = z
  .string()
  .min(1, "Key is required")
  .refine((key) => !/\s/.test(key), "Key should not contain spaces")
  .refine((key) => !/^\d+$/.test(key), "Key should not be numbers only");

const valueSchema = z.string().min(1, "Value is required");

const envVarSchema = z.array(
  z.object({
    key: keySchema,
    value: valueSchema,
  })
);

export default function EnvironmentVariables({ env }: EnvironmentVariablesProps) {
  const [isSaving, setIsSaving] = useState(false);
  const [envVars, setEnvVars] = useState<
    Array<{ id: string; key: string; value: string }>
  >([]);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    const initialEnvVars = Object.entries(env || {}).map(([key, value]) => ({
      id: uuidv4(),
      key,
      value,
    }));
    setEnvVars(initialEnvVars);
  }, [env]);

  const handleKeyChange = (id: string, newKey: string) => {
    setEnvVars((prevVars) =>
      prevVars.map((envVar) =>
        envVar.id === id ? { ...envVar, key: newKey } : envVar
      )
    );
    const currentVar = envVars.find((envVar) => envVar.id === id);
    validateField(id, newKey, currentVar?.value || "");
  };

  const handleValueChange = (id: string, newValue: string) => {
    setEnvVars((prevVars) =>
      prevVars.map((envVar) =>
        envVar.id === id ? { ...envVar, value: newValue } : envVar
      )
    );
    const currentVar = envVars.find((envVar) => envVar.id === id);
    validateField(id, currentVar?.key || "", newValue);
  };

  const validateField = (id: string, key: string, value: string) => {
    const keyValidation = keySchema.safeParse(key);
    const valueValidation = valueSchema.safeParse(value);

    setErrors((prevErrors) => {
      const newErrors = { ...prevErrors };
      if (!keyValidation.success) {
        newErrors[id] = keyValidation.error.errors[0].message;
      } else if (!valueValidation.success) {
        newErrors[id] = valueValidation.error.errors[0].message;
      } else {
        delete newErrors[id];
      }
      return newErrors;
    });
  };

  const addEnvVar = () => {
    setEnvVars((prevVars) => [
      ...prevVars,
      { id: uuidv4(), key: "", value: "" },
    ]);
  };

  const removeEnvVar = (id: string) => {
    setEnvVars((prevVars) => prevVars.filter((envVar) => envVar.id !== id));
    setErrors((prevErrors) => {
      const { [id]: _, ...rest } = prevErrors;
      return rest;
    });
  };

  const handleSubmit = async () => {
    try {
      const varsToValidate = envVars.map(({ key, value }) => ({ key, value }));
      envVarSchema.parse(varsToValidate);
      setIsSaving(true);
      const envObject = varsToValidate.reduce<Record<string, string>>(
        (acc, { key, value }) => {
          acc[key] = value;
          return acc;
        },
        {}
      );
      await updateSettings({
        env: envObject,
      });
      setErrors({});
    } catch (error) {
      if (error instanceof z.ZodError) {
        const fieldErrors: Record<string, string> = {};
        error.errors.forEach((err) => {
          const index = err.path[0] as number;
          const message = err.message;
          const id = envVars[index].id;
          fieldErrors[id] = message;
        });
        setErrors(fieldErrors);
      } else {
        console.error("Error updating environment variables:", error);
      }
    } finally {
      setIsSaving(false);
    }
  };

  const canAddNew = envVars.every(({ key, value }) => key && value);
  const hasErrors = Object.keys(errors).length > 0;

  return (
    <div className="flex flex-col gap-4">
      {envVars.map(({ id, key, value }) => (
        <div key={id} className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <Input
              value={key}
              onChange={(e) => handleKeyChange(id, e.target.value)}
              placeholder="Key"
              className="flex-1"
            />
            <Input
              value={value}
              onChange={(e) => handleValueChange(id, e.target.value)}
              placeholder="Value"
              className="flex-1"
            />
            <Button
              variant="secondary"
              onClick={() => removeEnvVar(id)}
              size="icon"
            >
              <Minus className="w-4 h-4" />
            </Button>
          </div>
          {errors[id] && (
            <p className="text-sm text-red-500">{errors[id]}</p>
          )}
        </div>
      ))}
      <div className="flex justify-end gap-4 mt-4">
        <Button
          variant="secondary"
          onClick={addEnvVar}
          disabled={!canAddNew}
        >
          Add New <Plus className="ml-2 w-4 h-4" />
        </Button>
        <Button onClick={handleSubmit} disabled={isSaving || hasErrors}>
          {isSaving ? "Saving..." : "Save"}
        </Button>
      </div>
    </div>
  );
}
