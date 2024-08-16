import {
  AIHighlight,
  CharacterCount,
  CodeBlockLowlight,
  HorizontalRule,
  Placeholder,
  StarterKit,
  TaskItem,
  TaskList,
  TiptapImage,
  TiptapLink,
  UpdatedImage,
  Youtube,
} from "novel/extensions";
import { UploadImagesPlugin } from "novel/plugins";

import { slashCommand } from './slash-command'
import { cx } from "class-variance-authority";
import { common, createLowlight } from "lowlight";
import Paragraph from '@tiptap/extension-paragraph'
import Heading from '@tiptap/extension-heading'
import GlobalDragHandle from 'tiptap-extension-global-drag-handle'
import AutoJoiner from 'tiptap-extension-auto-joiner' // optional

import Document from '@tiptap/extension-document'

import Text from '@tiptap/extension-text'
import Component, { sqlNodeExtension } from "./sql-node";


//TODO I am using cx here to get tailwind autocomplete working, idk if someone else can write a regex to just capture the class key in objects
const aiHighlight = AIHighlight;
//You can overwrite the placeholder with your own configuration
const placeholder = Placeholder.configure({
  placeholder: ({ node }) => {
    if (node.type.name === 'heading') {
      return '(Untitled))'
    }
    return "Press '/' for commands";
  },
  includeChildren: true,
});
const tiptapLink = TiptapLink.configure({
  HTMLAttributes: {
    class: cx(
      "text-muted-foreground underline underline-offset-[3px] hover:text-primary transition-colors cursor-pointer",
    ),
  },
});

const tiptapImage = TiptapImage.extend({
  addProseMirrorPlugins() {
    return [
      UploadImagesPlugin({
        imageClass: cx("opacity-40 rounded-lg border border-stone-200"),
      }),
    ];
  },
}).configure({
  allowBase64: true,
  HTMLAttributes: {
    class: cx("rounded-lg border border-muted"),
  },
});

const updatedImage = UpdatedImage.configure({
  HTMLAttributes: {
    class: cx("rounded-lg border border-muted"),
  },
});

const taskList = TaskList.configure({
  HTMLAttributes: {
    class: cx("not-prose pl-2 "),
  },
});
const taskItem = TaskItem.configure({
  HTMLAttributes: {
    class: cx("flex gap-2 items-start my-4"),
  },
  nested: true,
});

const horizontalRule = HorizontalRule.configure({
  HTMLAttributes: {
    class: cx("mt-4 mb-6 border-t border-muted-foreground"),
  },
});

const starterKit = StarterKit.configure({
  document: false,
  bulletList: {
    HTMLAttributes: {
      class: cx("list-disc list-outside leading-3 -mt-2"),
    },
  },
  orderedList: {
    HTMLAttributes: {
      class: cx("list-decimal list-outside leading-3 -mt-2"),
    },
  },
  listItem: {
    HTMLAttributes: {
      class: cx("leading-normal -mb-2"),
    },
  },
  blockquote: {
    HTMLAttributes: {
      class: cx("border-l-4 border-primary"),
    },
  },
  codeBlock: {
    HTMLAttributes: {
      class: cx("rounded-md bg-muted text-muted-foreground border p-5 font-mono font-medium"),
    },
  },
  code: {
    HTMLAttributes: {
      class: cx("rounded-md bg-muted  px-1.5 py-1 font-mono font-medium"),
      spellcheck: "false",
    },
  },
  horizontalRule: false,
  dropcursor: {
    color: "#DBEAFE",
    width: 4,
  },
  gapcursor: false,
});

const codeBlockLowlight = CodeBlockLowlight.configure({
  // configure lowlight: common /  all / use highlightJS in case there is a need to specify certain language grammars only
  // common: covers 37 language grammars which should be good enough in most cases
  lowlight: createLowlight(common),
});

const youtube = Youtube.configure({
  HTMLAttributes: {
    class: cx("rounded-lg border border-muted"),
  },
  inline: false,
});


const characterCount = CharacterCount.configure();

const CustomDocument = Document.extend({
})




export const extensions = [
  GlobalDragHandle.configure({
    dragHandleWidth: 30,
    scrollThreshold: 100,
  }),
  AutoJoiner.configure({
    elementsToJoin: ['bulletList', 'orderedList']
  }),
  starterKit,
  CustomDocument,
  Paragraph,
  Text,
  placeholder,
  Heading.configure({
    levels: [1, 2, 3],
  }),
  tiptapLink,
  tiptapImage,
  updatedImage,
  taskList,
  taskItem,
  horizontalRule,
  sqlNodeExtension,
  aiHighlight,
  // codeBlockLowlight,
  youtube,
  // characterCount,
];
