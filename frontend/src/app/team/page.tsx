"use client";
import CreateWorkspaceForm from "@/components/workspaces/create-workspace-form";
import FullWidthPageLayout from "../../components/layout/FullWidthPageLayout";

import * as React from "react";
import Modal from "react-modal";

import useSession from "@/app/hooks/use-session";
import { LoaderButton } from "@/components/ui/LoadingSpinner";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import UpdateWorkspaceForm from "@/components/workspaces/update-workspace-form";
import { DropdownMenu } from "@radix-ui/react-dropdown-menu";
import { getWorkspace } from "../actions/actions";
import { fetcher } from "../fetcher";

export default function Page() {
  const [workspace, setWorkspace] = React.useState<any>({});
  const [changedRoles, setChangedRoles] = React.useState<any>({});
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [modalIsOpen, setModalIsOpen] = React.useState<boolean>(false);
  const [invitations, setInvitations] = React.useState<any>([]);
  const [email, setEmail] = React.useState<string>("");

  const fetchWorkspaces = async () => {
    const workspace = await getWorkspace();
    setWorkspace(workspace);
  };

  const fetchInvitations = async () => {
    const resp = await fetcher("/invitations/");
    const data = await resp.json();
    setInvitations(data);
  };

  React.useEffect(() => {
    fetchWorkspaces();
    fetchInvitations();
  }, []);

  const saveRoles = async () => {
    try {
      setIsLoading(true);
      const resp = await fetcher("/workspace_groups/", {
        method: "POST",
        body: {
          workspace: workspace.id,
          groups: Object.keys(changedRoles).map((key) => ({
            user: key,
            name: changedRoles[key],
          })),
        },
        headers: {
          "Content-Type": "multipart/form-data", // This line should not be added as the browser will automatically set the correct boundary for multipart/form-data
        },
      });
      setIsLoading(false);
    } catch (err: any) {}
  };

  const openInviteMembers = () => {
    setModalIsOpen(true);
  };

  const sendInvitation = async () => {
    if (email && email.length > 0) {
      try {
        setIsLoading(true);
        const resp = await fetcher("/invitations/", {
          method: "POST",
          body: {
            email,
          },
        });
        setIsLoading(false);
        setModalIsOpen(false);
        fetchInvitations();
      } catch (err: any) {
        setIsLoading(false);
      }
    }
  };

  const { user } = useSession();

  const role = false ? "Member" : "Admin";
  return (
    <FullWidthPageLayout title="Workspace">
      <Modal
        isOpen={modalIsOpen}
        onRequestClose={() => setModalIsOpen(false)}
        contentLabel="Invite Members"
        style={{
          content: {
            width: "400px",
            margin: "auto",
            height: "fit-content",
          },
        }}
      >
        <h2>Invite Members</h2>
        <Label>Email:</Label>
        <Input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginTop: 20,
          }}
        >
          <Button onClick={sendInvitation}>Send Invitation</Button>

          <Button onClick={() => setModalIsOpen(false)}>Close</Button>
        </div>
      </Modal>
      <div className="space-y-8">
        <Card>
          <CardHeader>
            <CardTitle>Details</CardTitle>
          </CardHeader>
          <CardContent>
            {workspace && (
              <UpdateWorkspaceForm
                workspace={workspace}
                enabled={role === "Admin"}
              />
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Members</CardTitle>
          </CardHeader>
          <CardContent style={{ paddingBottom: 20 }}>
            <Tabs defaultValue="members">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="members" className="text-muted-foreground">
                  <div className="flex items-center space-x-2">
                    <div>Active</div>
                    <Badge variant="outline">{workspace?.users?.length}</Badge>
                  </div>
                </TabsTrigger>
                <TabsTrigger value="invitations">
                  <div className="flex items-center space-x-2">
                    <div>Invitations</div>
                    <Badge variant="outline">{invitations.length}</Badge>
                  </div>
                </TabsTrigger>
              </TabsList>
              <TabsContent value="members" className="w-full">
                <Table className="mt-4 w-full ">
                  <TableHeader>
                    <TableRow className="text-muted-foreground">
                      <TableHead className="">User</TableHead>
                      <TableHead>Joined</TableHead>
                      <TableHead>Role</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody style={{ width: "100%" }}>
                    {workspace?.users?.map((listUser: any) => (
                      <TableRow key={listUser.id}>
                        <TableCell className="font-medium">
                          <div className="space-x-4 flex items-center">
                            <div>
                              <Avatar className="size-8 border">
                                <AvatarImage src="" />
                                <AvatarFallback>
                                  {listUser.name?.slice(0, 2).toUpperCase() ||
                                    ""}
                                </AvatarFallback>
                              </Avatar>
                            </div>
                            <div>
                              <div>{listUser.name}</div>
                              <div>{listUser.email}</div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          -
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          {role === "Admin" && listUser.id !== user.id ? (
                            <Select
                              defaultValue={
                                changedRoles[listUser.id] ||
                                listUser.workspace_groups[0]?.name
                              }
                              onValueChange={(value) => {
                                setChangedRoles({
                                  ...changedRoles,
                                  [listUser.id]: value,
                                });
                              }}
                            >
                              <SelectTrigger className="w-full">
                                <SelectValue placeholder="" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="Admin">Admin</SelectItem>
                                <SelectItem value="Member">Member</SelectItem>
                              </SelectContent>
                            </Select>
                          ) : (
                            <DropdownMenu>
                              {listUser.workspace_groups[0]?.name}
                            </DropdownMenu>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TabsContent>
              <TabsContent value="invitations">
                <Table className="mt-4 w-full ">
                  <TableHeader>
                    <TableRow className="text-muted-foreground">
                      <TableHead>Email</TableHead>
                      <TableHead>Accepted</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody style={{ width: "100%" }}>
                    {(invitations || []).map((invitation: any) => (
                      <TableRow key={invitation.id}>
                        <TableCell className="font-medium">
                          {invitation.email}
                        </TableCell>
                        <TableCell className="font-medium">
                          {invitation.accepted ? "Yes" : "No"}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>

                <Button className="mt-4" onClick={openInviteMembers}>
                  Invite Members
                </Button>
              </TabsContent>
            </Tabs>
          </CardContent>
          <CardFooter style={{ flexDirection: "row-reverse" }}>
            {role === "Admin" && (
              <LoaderButton
                isLoading={isLoading}
                className="float-right"
                style={{ marginTop: 20 }}
                onClick={saveRoles}
              >
                Save
              </LoaderButton>
            )}
          </CardFooter>
        </Card>
      </div>
    </FullWidthPageLayout>
  );
}
