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
import { ApiKeysTable } from "./api-keys-table";
import { AssetExclusionTable } from "./asset-exclusion-table";
import type { Settings } from "./types";

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings>({
    exclusion_filters: [],
    api_keys: {},
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
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-8">
          <Card>
            <CardHeader>
              <CardTitle>Exclude Assets</CardTitle>
              <CardDescription>
                Assets will be excluded using substring, case insensitive
                matches against the asset name
              </CardDescription>
            </CardHeader>
            <CardContent>
              <AssetExclusionTable
                exclusionFilters={settings.exclusion_filters}
              />
            </CardContent>
          </Card>
        </div>

        <div className="flex flex-col gap-8">
          <Card>
            <CardHeader>
              <CardTitle>API Keys</CardTitle>
            </CardHeader>
            <CardContent>
              <ApiKeysTable apiKeys={settings.api_keys} />
            </CardContent>
          </Card>
        </div>
      </div>
    </FullWidthPageLayout>
  );
}
