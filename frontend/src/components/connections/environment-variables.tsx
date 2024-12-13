import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { XIcon } from "lucide-react";
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
  const [isAddingNew, setIsAddingNew] = useState(false);
  const [newKey, setNewKey] = useState("");
  const [newValue, setNewValue] = useState("");

  const updateEnvVar = (oldKey: string, newKey: string, newValue: string) => {
    const currentEnvVars = { ...form.getValues("env_vars") };
    
    // If key changed, remove old key and add new one
    if (oldKey !== newKey) {
      delete currentEnvVars[oldKey];
    }
    
    currentEnvVars[newKey] = newValue;
    
    form.setValue("env_vars", currentEnvVars, {
      shouldDirty: true,
      shouldTouch: true
    });
  };

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
      setNewKey("");
      setNewValue("");
      setIsAddingNew(false);
    }
  };

  const removeEnvVar = (keyToRemove: string) => {
    const newEnvVars = { ...envVars };
    delete newEnvVars[keyToRemove];
    form.setValue("env_vars", newEnvVars);
  };

  return (
    <div className="flex flex-col gap-4">
      <p className="text-lg font-medium">Environment Variables</p>
      <p className="text-sm text-gray-500">
        Environment variables are used to configure the dbt project.
      </p>
      
      {Object.entries(envVars).map(([key, value]) => (
        <div key={key} className="flex items-center gap-2">
          <Input
            defaultValue={key}
            onChange={(e) => {
              updateEnvVar(key, e.target.value, value as string);
            }}
            className="flex-1"
          />
          <Input
            defaultValue={value as string}
            onChange={(e) => {
              updateEnvVar(key, key, e.target.value);
            }}
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

      {isAddingNew && (
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
              }
            }}
          >
            Add
          </Button>
          <Button
            type="button"
            variant="ghost"
            onClick={() => {
              setIsAddingNew(false);
              setNewKey("");
              setNewValue("");
            }}
          >
            Cancel
          </Button>
        </div>
      )}

      {!isAddingNew && (
        <Button
          type="button"
          variant="outline"
          onClick={() => setIsAddingNew(true)}
          className="text-sm w-fit self-end"
        >
          Add Environment Variable
        </Button>
      )}
    </div>
  );
}
