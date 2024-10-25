
import { ChevronDown, ChevronRight, File, FileText, Folder, FolderOpen, Plus, Trash, Ellipsis } from 'lucide-react'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Button } from '@/components/ui/button'
import { useState } from 'react'
import { useFiles } from '@/app/contexts/FilesContext'

const DbtLogo = () => (
    <svg
        width="14px"
        height="14px"
        viewBox="0 0 256 256"
        version="1.1"
        preserveAspectRatio="xMidYMid"
    >
        <g>
            <path
                d="M245.121138,10.6473813 C251.139129,16.4340053 255.074133,24.0723342 256,32.4050489 C256,35.8769778 255.074133,38.1917867 252.990862,42.5895822 C250.907876,46.9873778 225.215147,91.4286933 217.57696,103.696213 C213.179164,110.871609 210.864356,119.435947 210.864356,127.768462 C210.864356,136.3328 213.179164,144.6656 217.57696,151.840996 C225.215147,164.108516 250.907876,208.781084 252.990862,213.179164 C255.074133,217.57696 256,219.659947 256,223.131876 C255.074133,231.464676 251.370667,239.103147 245.352676,244.658347 C239.565938,250.676338 231.927751,254.611342 223.826489,255.305671 C220.35456,255.305671 218.039751,254.379804 213.873493,252.296533 C209.706951,250.213262 164.340053,225.215147 152.072249,217.57696 C151.146382,217.113884 150.220516,216.419556 149.063396,215.95648 L88.4195556,180.079502 C89.8082133,191.652693 94.9006222,202.763093 103.233138,210.864356 C104.853618,212.484551 106.473813,213.873493 108.325547,215.262151 C106.936604,215.95648 105.316409,216.651093 103.927751,217.57696 C91.6599467,225.215147 46.9873778,250.907876 42.5895822,252.990862 C38.1917867,255.074133 36.1085156,256 32.4050489,256 C24.0723342,255.074133 16.4340053,251.370667 10.8788338,245.352676 C4.86075733,239.565938 0.925858133,231.927751 0,223.594951 C0.231464676,220.123022 1.1573248,216.651093 3.00905244,213.641956 C5.09223822,209.24416 30.7848533,164.571307 38.42304,152.303787 C42.82112,145.128391 45.1356444,136.795591 45.1356444,128.231538 C45.1356444,119.6672 42.82112,111.3344 38.42304,104.159004 C30.7848533,91.4286933 4.86075733,46.75584 3.00905244,42.3580444 C1.1573248,39.3489067 0.231464676,35.8769778 0,32.4050489 C0.925858133,24.0723342 4.62930489,16.4340053 10.6473813,10.6473813 C16.4340053,4.62930489 24.0723342,0.925858133 32.4050489,0 C35.8769778,0.231464676 39.3489067,1.1573248 42.5895822,3.00905244 C46.2930489,4.62930489 78.9293511,23.6094009 96.28928,33.7939911 L100.224284,36.1085156 C101.612942,37.0343822 102.770347,37.7287111 103.696213,38.1917867 L105.547947,39.3489067 L167.348907,75.9204978 C165.960249,62.0324978 158.784853,49.3019022 147.674453,40.7378489 C149.063396,40.04352 150.683591,39.3489067 152.072249,38.42304 C164.340053,30.7848533 209.012622,4.86075733 213.410418,3.00905244 C216.419556,1.1573248 219.891484,0.231464676 223.594951,0 C231.696213,0.925858133 239.334684,4.62930489 245.121138,10.6473813 Z M131.240391,144.434062 L144.434062,131.240391 C146.285796,129.388658 146.285796,126.611342 144.434062,124.759609 L131.240391,111.565938 C129.388658,109.714204 126.611342,109.714204 124.759609,111.565938 L111.565938,124.759609 C109.714204,126.611342 109.714204,129.388658 111.565938,131.240391 L124.759609,144.434062 C126.379804,146.054258 129.388658,146.054258 131.240391,144.434062 Z"
                fill="#FF694A"
            ></path>
        </g>
    </svg>
);



export default function Node({ node, style, dragHandle, tree }: { node: any, style: any, dragHandle: any, tree: any }) {
    const { openFile, createFileAndRefresh, deleteFileAndRefresh, closeFile } = useFiles();
    const [showOptions, setShowOptions] = useState(false)

    const handleCreateFile = async (e: React.MouseEvent) => {
        e.stopPropagation();
        const newFileName = prompt("Enter new file name:");
        if (newFileName) {
            const newPath = `${node.data.path}/${newFileName}`;
            await createFileAndRefresh(newPath, ''); // Call your backend API to create the file
            openFile({
                name: newFileName,
                path: newPath,
                type: 'file'
            });
        }
    };


    const handleDelete = async (e: React.MouseEvent) => {
        e.stopPropagation();
        if (confirm(`Are you sure you want to delete ${node.data.name}?`)) {
            await deleteFileAndRefresh(node.data.path);
            closeFile(node.data.path);
        }
    };

    // const handleRename = async (e: React.MouseEvent) => {
    //     e.stopPropagation();
    //     const newName = prompt("Enter new name:", node.data.name);
    //     if (newName && newName !== node.data.name) {
    //         const newPath = node.data.path.replace(node.data.name, newName);
    //         await renameFile(node.data.path, newPath);
    //         node.submit(newName);
    //     }
    // };


    // const handleCreateFolder = async (e: React.MouseEvent) => {
    //     e.stopPropagation();
    //     const newFolderName = prompt("Enter new folder name:");
    //     if (newFolderName) {
    //         const newPath = `${node.data.path}/${newFolderName}`;
    //         await createFile(newPath, '', true); // Call your backend API to create the folder
    //         tree.create({
    //             parentId: node.id,
    //             type: 'directory',
    //             data: { name: newFolderName, path: newPath }
    //         });
    //     }
    // };

    return (
        <div style={style} onClick={() => {
            if (node.isLeaf) {
                openFile(node.data);
            } else {
                node.toggle()
            }
        }} ref={dragHandle} className={`${node.isSelected ? 'rounded font-medium bg-accent text-accent-foreground' : ''} hover:bg-white hover:cursor-pointer flex items-center rounded`}>
            {!node.isLeaf && (node.isOpen ? <FolderOpen className='mr-1 size-4' /> : <Folder className='mr-1 size-4' />)}
            {node.isLeaf && node.data.name.endsWith('.sql') && <div className={`mr-1 ${node.isSelected ? 'opacity-100' : 'opacity-70'}`}><DbtLogo /></div>}
            {node.isLeaf && node.data.name.endsWith('.yml') && <FileText className='mr-1 h-4 w-4' />}
            {node.isLeaf && !node.data.name.endsWith('.sql') && !node.data.name.endsWith('.yml') && <File className='mr-1 size-4' />}
            {node.isEditing ? (
                <input
                    type="text"
                    defaultValue={node.data.name}
                    onFocus={(e) => e.currentTarget.select()}
                    onBlur={() => node.reset()}
                    onKeyDown={(e) => {
                        if (e.key === "Escape") node.reset();
                        if (e.key === "Enter") node.submit(e.currentTarget.value);
                    }}
                    autoFocus
                />
            ) : (
                <div className='w-full flex items-center justify-between group'>
                    <div className='truncate'>
                        {node.data.name}
                    </div>
                    <div className='flex items-center opacity-0 group-hover:opacity-100 transition-opacity'>
                        <Popover open={showOptions} onOpenChange={setShowOptions}>
                            <PopoverTrigger asChild>
                                <div
                                    className='text-muted-foreground text-xs hover:cursor-pointer hover:text-foreground relative'
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setShowOptions(!showOptions);
                                    }}
                                >
                                    <Ellipsis className='mr-1 size-4' />
                                </div>
                            </PopoverTrigger>
                            <PopoverContent className="w-40 p-0" onClick={(e) => e.stopPropagation()}>
                                <div className='w-full'>
                                    {/* <Button className='w-full' variant="ghost" size="sm" onClick={handleRename}>
                                        <Pencil className="mr-2 h-3 w-3" />
                                        Rename
                                    </Button> */}
                                    <Button className='w-full' variant="ghost" size="sm" onClick={handleDelete}>
                                        <Trash className="mr-2 h-3 w-3" />
                                        Delete
                                    </Button>
                                </div>
                            </PopoverContent>
                        </Popover>
                        {!node.isLeaf && (
                            <>
                                <div
                                    className='text-muted-foreground text-xs hover:cursor-pointer hover:text-foreground relative'
                                    onClick={handleCreateFile}
                                >
                                    <Plus className='mr-1 size-4' />
                                </div>
                                {/* <div
                                    className='text-muted-foreground text-xs hover:cursor-pointer hover:text-foreground relative'
                                    onClick={handleCreateFolder}
                                >
                                    <Folder className='mr-1 size-4' />
                                    <span>New Folder</span>
                                </div> */}
                            </>
                        )}
                    </div>

                </div>
            )}
        </div>
    );
}