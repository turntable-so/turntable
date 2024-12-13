import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, XIcon } from "lucide-react";
import { useState } from "react";
import type { UseFormReturn } from "react-hook-form";

type FormValues = {
  env_vars: Record<string, string>;
  [key: string]: any;
};

type EnvironmentVariablesProps = {
  form: UseFormReturn<FormValues>;
};

export default function EnvironmentVariables({
  form,
}: EnvironmentVariablesProps) {
  const envVars = form.watch("env_vars") || {};

  const addEnvVar = (key: string, value: string) => {
    if (key && value) {
      const currentEnvVars = form.getValues("env_vars") || {};
      const updatedEnvVars = {
        ...currentEnvVars,
        [key]: value,
      };
      form.setValue("env_vars", updatedEnvVars, { 
        shouldDirty: true,
        shouldTouch: true 
      });
    }
  };

  const removeEnvVar = (keyToRemove: string) => {
    const newEnvVars = { ...envVars };
    delete newEnvVars[keyToRemove];
    form.setValue("env_vars", newEnvVars);
  };

  const [newKey, setNewKey] = useState("");
  const [newValue, setNewValue] = useState("");

  return (
    <div className="flex flex-col gap-4">
      <p className="text-lg font-medium">Environment Variables</p>
      <p className="text-sm text-gray-500">
        Environment variables are used to configure the dbt project.
      </p>
      
      {Object.entries(envVars).map(([key, value]) => (
        <div key={key} className="flex items-center gap-2">
          <Input
            value={key}
            disabled
            className="flex-1"
          />
          <Input
            value={value as string}
            disabled
            className="flex-1"
          />
          <Button
            type="button"
            variant="secondary"
            onClick={() => removeEnvVar(key)}
            size="icon"
          >
            <XIcon className="w-4 h-4" />
          </Button>
        </div>
      ))}

      <div className="flex items-center gap-2">
        <Input
          value={newKey}
          onChange={(e) => setNewKey(e.target.value)}
          placeholder="Key"
          className="flex-1"
        />
        <Input
          value={newValue}
          onChange={(e) => setNewValue(e.target.value)}
          placeholder="Value"
          className="flex-1"
        />
        <Button
          type="button"
          variant="secondary"
          onClick={() => {
            if (newKey && newValue) {
              addEnvVar(newKey, newValue);
              setNewKey("");
              setNewValue("");
            }
          }}
          size="icon"
        >
          <Plus className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
