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
            <CardTitle>API Keys</CardTitle>
            <CardDescription>
              Provide API keys for OpenAI and Anthropic to enable AI features
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div>
              <Label htmlFor="openai_key">OpenAI</Label>
              <Input id="openai_key" placeholder="sk-foobarbaz" />{" "}
            </div>
          </CardContent>
        </Card>
      </div>
    </FullWidthPageLayout>
  );
}
