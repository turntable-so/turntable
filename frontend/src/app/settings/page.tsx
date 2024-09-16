'use client'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import FullWidthPageLayout from "../../components/layout/FullWidthPageLayout";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableFooter,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useEffect, useState } from "react";
import { getSettings } from "../actions/actions";


type AssetExclusionFilter = {
  filter_name_contains: string
  count: number
}

type Settings = {
  exclusion_filters: AssetExclusionFilter[]
}

function AssetExclusionTable({ exclusionFilters }: { exclusionFilters: AssetExclusionFilter[] }) {

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Substring name match</TableHead>
          <TableHead>Number of Assets Excluded</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {exclusionFilters.map((filter: AssetExclusionFilter) => (
          <TableRow key={filter.filter_name_contains}>
            <TableCell className='font-semibold'>{filter.filter_name_contains}</TableCell>
            <TableCell>{filter.count}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}





export default function SettingsPage() {

  const [settings, setSettings] = useState<Settings>({
    exclusion_filters: []
  })

  useEffect(() => {
    const fetchSettings = async () => {
      const data = await getSettings()
      setSettings(data)
    }
    fetchSettings()
  }, [])


  return (
    <FullWidthPageLayout title="Settings">
      <>
        <Card>
          <CardHeader>
            <CardTitle>Exclude Assets</CardTitle>
            <CardDescription>Assets will be excluded using substring, case insensitive matches against the asset name</CardDescription>
          </CardHeader>
          <CardContent>
            <AssetExclusionTable exclusionFilters={settings.exclusion_filters} />
          </CardContent>
        </Card>
      </>
    </FullWidthPageLayout>
  );
}
