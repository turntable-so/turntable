import * as React from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { ChevronDown, Info } from "lucide-react"

export default function NewJob() {
    return (
        <div className="container mx-auto p-4">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">Create new job</h1>
            </div>

            <form className="space-y-6">
                <Card>
                    <CardHeader>
                        <CardTitle>Job settings</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="job-name">Job name</Label>
                            <Input id="job-name" placeholder="New job" />
                        </div>
                        <Button variant="link" className="p-0">+ Add description</Button>
                        <div className="space-y-2">
                            <Label htmlFor="environment">Environment</Label>
                            <Select>
                                <SelectTrigger id="environment">
                                    <SelectValue placeholder="Select..." />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="dev">Development</SelectItem>
                                    <SelectItem value="staging">Staging</SelectItem>
                                    <SelectItem value="prod">Production</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Execution settings</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="command">Command</Label>
                            <div className="flex items-center space-x-2">
                                <Input id="command" defaultValue="dbt build" />
                                <Info className="text-muted-foreground" />
                            </div>
                        </div>
                        <Button variant="link" className="p-0">+ Add command</Button>
                        <div className="flex items-center space-x-2">
                            <Switch id="generate-docs" />
                            <Label htmlFor="generate-docs">Generate docs on run</Label>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Schedule</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex items-center space-x-2">
                            <Switch id="run-on-schedule" />
                            <Label htmlFor="run-on-schedule">Run on schedule</Label>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="timing">Timing</Label>
                            <Select>
                                <SelectTrigger id="timing">
                                    <SelectValue placeholder="Intervals" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="hourly">Hourly</SelectItem>
                                    <SelectItem value="daily">Daily</SelectItem>
                                    <SelectItem value="weekly">Weekly</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="run-every">Run every (UTC)</Label>
                            <Input id="run-every" placeholder="Every 12 hours" />
                        </div>
                        <div className="space-y-2">
                            <Label>Days of the week</Label>
                            <div className="flex space-x-2">
                                {["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"].map((day) => (
                                    <Button key={day} variant="outline" size="sm">
                                        {day.slice(0, 1)}
                                    </Button>
                                ))}
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent>
                        <Accordion type="single" collapsible className="w-full">
                            <AccordionItem value="advanced-settings">
                                <AccordionTrigger>Advanced settings</AccordionTrigger>
                                <AccordionContent>
                                    <div className="space-y-4">
                                        <div className="space-y-2">
                                            <Label htmlFor="target-name">Target name</Label>
                                            <Input id="target-name" placeholder="default" />
                                            <p className="text-sm text-muted-foreground">If you have logic that behaves differently depending on the specified target, set a value other than default.</p>
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="run-timeout">Run timeout</Label>
                                            <Input id="run-timeout" placeholder="0" />
                                            <p className="text-sm text-muted-foreground">Maximum number of seconds a run will execute before it is canceled. If this is set to 0 (the default), the run will be canceled after running for 24 hours.</p>
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="compare-changes">Compare changes against</Label>
                                            <Input id="compare-changes" placeholder="No defined" />
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="job-version">Job version</Label>
                                            <Select>
                                                <SelectTrigger id="job-version">
                                                    <SelectValue placeholder="Select..." />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="v1">Version 1</SelectItem>
                                                    <SelectItem value="v2">Version 2</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>
                                    </div>
                                </AccordionContent>
                            </AccordionItem>
                        </Accordion>
                    </CardContent>
                </Card>

                <div className="space-x-2 float-right">
                    <Button variant="outline">Cancel</Button>
                    <Button>Save</Button>
                </div>
            </form>
            <div className='h-48' />
        </div >
    )
}