// @ts-nocheck
import { Dialog } from "./ui/dialog";

export default function FullScreenDialog({ children, isOpen, onOpenChange }: any) {
    return (
        <Dialog.Root open={isOpen} onOpenChange={onOpenChange}>
            <Dialog.Portal>
                <Dialog.Overlay className="fixed inset-0 bg-black/50 z-40" />
                <Dialog.Content className="fixed inset-4 overflow-hidden z-50">
                    <div className="h-full bg-white p-4 rounded-md">
                        {children}
                    </div>
                </Dialog.Content>
            </Dialog.Portal>
        </Dialog.Root>
    )
}