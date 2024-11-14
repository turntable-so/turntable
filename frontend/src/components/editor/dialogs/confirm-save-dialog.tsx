import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useFiles } from "@/app/contexts/FilesContext";

export default function ConfirmSaveDialog() {
  const {
    showConfirmSaveDialog,
    setShowConfirmSaveDialog,
    closeFile,
    saveFile,
    fileToClose,
    setFileToClose,
  } = useFiles();

  const handleNoSave = () => {
    if (fileToClose) {
      const fileToDiscard = { ...fileToClose, isDirty: false };
      closeFile(fileToDiscard);
      setFileToClose(null);
      setShowConfirmSaveDialog(false);
    }
  };

  const handleSave = () => {
    if (!fileToClose || typeof fileToClose.content !== "string") {
      alert("Unable to save the file. Invalid content.");
      return;
    }
    saveFile(fileToClose.node.path, fileToClose.content);
    const fileToProceed = { ...fileToClose, isDirty: false };
    closeFile(fileToProceed);
    setFileToClose(null);
    setShowConfirmSaveDialog(false);
  };

  return (
    <Dialog
      open={showConfirmSaveDialog}
      onOpenChange={setShowConfirmSaveDialog}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            Do you want to save the changes you made to {fileToClose?.node.name}
            ?
          </DialogTitle>
          <DialogDescription>
            Your changes will be lost if you don't save them.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={handleNoSave}>
            Don't Save
          </Button>
          <Button onClick={handleSave}>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
