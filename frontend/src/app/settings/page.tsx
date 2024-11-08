"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useEffect, useState } from "react";
import FullWidthPageLayout from "../../components/layout/FullWidthPageLayout";
import { getSettings } from "../actions/actions";
import { AssetExclusionTable } from "./asset-exclusion-table";
import type { Settings } from "./types";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

function GenericSecret({
  name,
  placeholder,
}: {
  name: string;
  placeholder: string;
}) {
  const [value, setValue] = useState("");
  const slug = name.toLowerCase().replace(" ", "_");

  return (
    <div className="flex flex-row items-end gap-x-2 w-full">
      <div className="flex flex-col w-full gap-y-0.5">
        <Label htmlFor={slug}>{name}</Label>
        <Input
          id={slug}
          placeholder={placeholder}
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
      </div>
      <Button
        onClick={() => {
          // TODO: Save to the db
          console.log("Saving", name);
        }}
      >
        Save
      </Button>
    </div>
  );
}

const AI_PROVIDERS = ["OpenAI", "Anthropic"];

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings>({
    exclusion_filters: [],
  });

  useEffect(() => {
    const fetchSettings = async () => {
      const data = await getSettings();
      setSettings(data);
    };
    fetchSettings();
  }, []);

  return (
    <FullWidthPageLayout title="Settings">
      <div className="flex flex-col gap-8">
        <Card>
          <CardHeader>
            <CardTitle>Exclude Assets</CardTitle>
            <CardDescription>
              Assets will be excluded using substring, case insensitive matches
              against the asset name
            </CardDescription>
          </CardHeader>
          <CardContent>
            <AssetExclusionTable
              exclusionFilters={settings.exclusion_filters}
            />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>AI Providers</CardTitle>
            <CardDescription>Select an AI provider</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-y-2">
            <Select>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select an AI provider" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectLabel>Providers</SelectLabel>
                  {AI_PROVIDERS.map((provider) => (
                    <SelectItem value={provider.toLowerCase()}>
                      {provider}
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>API Keys</CardTitle>
            <CardDescription>
              Provide API keys for AI providers to enable AI features
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-y-2">
            {AI_PROVIDERS.map((provider) => (
              <GenericSecret name={provider} placeholder="sk-foobarbaz" />
            ))}
          </CardContent>
        </Card>
      </div>
    </FullWidthPageLayout>
  );
}
