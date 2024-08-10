import { NodeViewContent, NodeViewWrapper, ReactNodeViewRendererOptions } from "@tiptap/react";
import QueryBlock from "../QueryBlock";
import { mergeAttributes, Node } from '@tiptap/core'
import { ReactNodeViewRenderer } from "@tiptap/react";
import { v4 as uuidv4 } from 'uuid';

type SQLNodeAttributes = {
    title?: string
    sql?: string
    resourceId: string
    limit: number
}

declare module '@tiptap/core' {
    interface Commands<ReturnType> {
        sqlNode: {
            setSqlNode: (options: SQLNodeAttributes) => ReturnType
        }
    }
}

export type ViewType = 'table' | 'chart'


export const sqlNodeExtension = Node.create({
    name: 'sqlNode',

    group: 'block',

    draggable: true,

    addAttributes(): any {
        return {
            title: {
                default: "(Untitled) query",
            },
            sql: {
                default: "",
            },
            resourceId: {
                default: 'unknown resource'
            },
            blockId: {
                default: `${uuidv4()}`
            },
            viewType: {
                default: 'table' as ViewType,
            },
            limit: {
                default: 1000
            },
            isLoading: {
                default: false,
            },
            records: {
                default: []
            },
            chartSettings: {
                default: {},
            }
        }
    },

    parseHTML() {
        return [
            {
                tag: 'div[data-sql-node]',
            },
        ]
    },

    renderHTML({ HTMLAttributes }) {
        return ['div', mergeAttributes({ "data-sql-node": "" }, HTMLAttributes)]
    },

    addNodeView() {
        return ReactNodeViewRenderer(SqlNodeComponent)
    },

    addCommands() {
        return {
            setSqlNode: (attrs: SQLNodeAttributes) => ({ commands }) => {
                console.log('attrs', { attrs })
                return commands.insertContent({
                    type: this.name,
                    attrs: {
                        title: attrs.title,
                        sql: attrs.sql,
                        resourceId: attrs.resourceId,
                        limit: attrs.limit,
                    }
                })
            }
        }
    }
})




const SqlNodeComponent = ({ node, updateAttributes, deleteNode }: {
    node: Partial<ReactNodeViewRendererOptions>,
    updateAttributes: any,
    deleteNode: any
}) => {
    return (
        <NodeViewWrapper>
            <div data-sql-node=''>
                <QueryBlock node={node as any} updateAttributes={updateAttributes} deleteNode={deleteNode}/>
            </div>
        </NodeViewWrapper>
    )
}

export default SqlNodeComponent