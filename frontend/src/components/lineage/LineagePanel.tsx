// import React, { useContext, useState } from 'react';
// import { LineageViewContext } from '@/components/lineage/LineageView';
// // import { useHotkeys } from 'react-hotkeys-hook';

// function LineageIcon() {
//   return (
//     <svg className="h-3" viewBox="0 0 1024 1024" fill="currentColor">
//       <path d="M98 973.98h92V818H98zM98 718h92V562H98zm0-256h92V306H98zm0-256h92V50H98zm128 707.98h128V786h92v-36h-92V622H226v36h92v219.98h-92zM226 402h128V274h92v-36h-92V110H226v36h92v220h-92zm256 443.98h92V690h-92zM482 334h92V178h-92zm128 452h96V530h92v-36h-92V238h-96v36h60v476h-60zm224-196h92V434h-92z" />
//     </svg>
//   );
// }

// export function LineagePanel() {
//   const {
//     lineageData,
//     lineageOptions,
//     updateGraph,
//     isLineageOptionsPanelOpen,
//     setIsLineageOptionsPanelOpen,
//   } = useContext(LineageViewContext);

//   // useHotkeys('escape', e => {
//   //   if (isLineageOptionsPanelOpen) {
//   //     setIsLineageOptionsPanelOpen(false);
//   //     e.stopImmediatePropagation();
//   //     e.preventDefault();
//   //   }
//   // });

//   const activeResource = (lineageData as any).activeResource;

//   if (!isLineageOptionsPanelOpen) {
//     return (
//       <div
//         onClick={() => setIsLineageOptionsPanelOpen(true)}
//         className="
//         p-1.5
//         rounded-lg
//         bg-[color:var(--vscode-editor-background)]
//         hover:bg-[color:var(--vscode-button-secondaryHoverBackground)]
//         border border-[color:var(--vscode-notificationCenter-border)] border-solid
//         text-[color:var(--vscode-editor-foreground)]
//         flex items-center gap-1.5
//         cursor-pointer
//         "
//       >
//         <LineageIcon />
//         <span className="font-mono text-[11px] mr-1.5">
//           {lineageOptions.predecessor_depth} + {activeResource.name} +{' '}
//           {lineageOptions.successor_depth}
//         </span>
//       </div>
//     );
//   }

//   return (
//     <div
//       onClick={() => setIsLineageOptionsPanelOpen(true)}
//       className="
//         p-1.5
//         rounded-lg
//         bg-[color:var(--vscode-editor-background)]
//         hover:bg-[color:var(--vscode-button-secondaryHoverBackground)]
//         border border-[color:var(--vscode-notificationCenter-border)] border-solid
//         text-[color:var(--vscode-editor-foreground)]
//         flex items-center gap-1.5
//         cursor-pointer
//         "
//     >
//       <LineageIcon />
//       <form
//         className="flex items-center gap-1.5"
//         onSubmit={e => {
//           e.preventDefault();
//           const formData = new FormData(e.target as HTMLFormElement);
//           const predecessor_depth = formData.get('predecessor_depth');
//           const successor_depth = formData.get('successor_depth');

//           if (predecessor_depth && successor_depth) {
//             updateGraph({
//               predecessor_depth: parseInt(predecessor_depth as string),
//               successor_depth: parseInt(successor_depth as string),
//             });

//             setIsLineageOptionsPanelOpen(false);
//           }
//         }}
//       >
//         <span className="font-mono text-[11px] mr-1.5">
//           <input
//             name="predecessor_depth"
//             type="number"
//             min={1}
//             className="w-10"
//             defaultValue={lineageOptions.predecessor_depth}
//           />{' '}
//           + {activeResource.name} +{' '}
//           <input
//             name="successor_depth"
//             type="number"
//             min={1}
//             className="w-10"
//             defaultValue={lineageOptions.successor_depth}
//           />
//         </span>
//         {/*
//         <VSCodeButton appearance="primary" type="submit">
//           Update graph
//         </VSCodeButton> */}
//       </form>
//     </div>
//   );
// }
