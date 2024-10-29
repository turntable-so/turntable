// 'use client'
// import { $getRoot, $getSelection } from 'lexical';

// import { AutoFocusPlugin } from '@lexical/react/LexicalAutoFocusPlugin';
// import { LexicalComposer } from '@lexical/react/LexicalComposer';
// import { RichTextPlugin } from '@lexical/react/LexicalRichTextPlugin';
// import { ContentEditable } from '@lexical/react/LexicalContentEditable';
// import { HistoryPlugin } from '@lexical/react/LexicalHistoryPlugin';
// import LexicalErrorBoundary from '@lexical/react/LexicalErrorBoundary';
// import ToolbarPlugin from "@/components/doc_editor/plugins/ToolbarPlugin"
// import TreeViewPlugin from "@/components/doc_editor/plugins/TreeViewPlugin"

// function Placeholder() {
//     return <div className="editor-placeholder">Enter some rich text...</div>;
// }

// const ExampleTheme = {
//     code: 'editor-code',
//     heading: {
//         h1: 'editor-heading-h1',
//         h2: 'editor-heading-h2',
//         h3: 'editor-heading-h3',
//         h4: 'editor-heading-h4',
//         h5: 'editor-heading-h5',
//     },
//     image: 'editor-image',
//     link: 'editor-link',
//     list: {
//         listitem: 'editor-listitem',
//         nested: {
//             listitem: 'editor-nested-listitem',
//         },
//         ol: 'editor-list-ol',
//         ul: 'editor-list-ul',
//     },
//     ltr: 'ltr',
//     paragraph: 'editor-paragraph',
//     placeholder: 'editor-placeholder',
//     quote: 'editor-quote',
//     rtl: 'rtl',
//     text: {
//         bold: 'editor-text-bold',
//         code: 'editor-text-code',
//         hashtag: 'editor-text-hashtag',
//         italic: 'editor-text-italic',
//         overflowed: 'editor-text-overflowed',
//         strikethrough: 'editor-text-strikethrough',
//         underline: 'editor-text-underline',
//         underlineStrikethrough: 'editor-text-underlineStrikethrough',
//     },
// };

// const editorConfig = {
//     namespace: 'React.js Demo',
//     nodes: [],
//     // Handling of errors during update
//     onError(error: Error) {
//         throw error;
//     },
//     // The editor theme
//     theme: ExampleTheme,
// };

// export default function Editor() {

//     return (
//         <LexicalComposer initialConfig={editorConfig}>
//             <div className="editor-container">
//                 <ToolbarPlugin />
//                 <div className="editor-inner">
//                     <RichTextPlugin
//                         contentEditable={<ContentEditable />}
//                         placeholder={<Placeholder />}
//                         ErrorBoundary={LexicalErrorBoundary}
//                     />
//                     <HistoryPlugin />
//                     <AutoFocusPlugin />
//                     <TreeViewPlugin />
//                 </div>
//             </div>
//         </LexicalComposer>
//     );
// }
