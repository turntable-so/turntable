// @ts-nocheck
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select";
import { sql } from "@codemirror/lang-sql";
import { ExclamationTriangleIcon } from "@radix-ui/react-icons";
import {
  ColDef
} from "ag-grid-community";
import { AgGridReact } from "ag-grid-react"; // React Data Grid Component
import {
  ChevronsDownUp,
  Clock,
  Download,
  Expand,
  Filter,
  Loader2,
  Play
} from "lucide-react";
import { Fragment, useEffect, useRef, useState } from "react";
import { useHotkeys } from "react-hotkeys-hook";
import {
  executeQuery,
  getWorkflow
} from "../app/actions/actions";
import "./ag-grid-custom-theme.css"; // Custom CSS Theme for Data Grid
import LoadingVinyl from "./loading-vinyl-spinner";
import { Alert, AlertDescription, AlertTitle } from "./ui/alert";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
// import 'codemirror/keymap/sublime';
// import 'codemirror/theme/quietlight.css';
import { getQueryBlockResult } from "@/app/actions/query-actions";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CompletionContext, autocompletion } from "@codemirror/autocomplete";
import { quietlight } from "@uiw/codemirror-theme-quietlight";
import CodeMirror, {
  EditorState,
  EditorView,
  ReactCodeMirrorRef
} from "@uiw/react-codemirror";
import { useParams } from "next/navigation";
import { v4 as uuidv4 } from 'uuid';
import { useAppContext } from "../contexts/AppContext";
import { ViewType } from "./notebook/sql-node";


const getColumnType = (pandasType: string) => {
  if (pandasType.toLowerCase().includes("date")) {
    return "date";
  }
  if (pandasType === "boolean") {
    return "string";
  }
  return pandasType;
};


import { ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Bar, BarChart, CartesianGrid, XAxis } from "recharts";

import { ChartConfig, ChartContainer } from "@/components/ui/chart";

const chartData = [
  { month: "January", desktop: 186, mobile: 80 },
  { month: "February", desktop: 305, mobile: 200 },
  { month: "March", desktop: 237, mobile: 120 },
  { month: "April", desktop: 73, mobile: 190 },
  { month: "May", desktop: 209, mobile: 130 },
  { month: "June", desktop: 214, mobile: 140 },
]

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "#2563eb",
  },
  mobile: {
    label: "Mobile",
    color: "#60a5fa",
  },
} satisfies ChartConfig

export function ChartComponent() {
  return (
    <ChartContainer config={chartConfig} className="min-h-[400px] w-full">
      <BarChart accessibilityLayer data={chartData}>
        <CartesianGrid vertical={false} />
        <XAxis
          dataKey="month"
          tickLine={false}
          tickMargin={10}
          axisLine={false}
          tickFormatter={(value) => value.slice(0, 3)}
        />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Bar dataKey="desktop" fill="var(--color-desktop)" radius={4} />
        <Bar dataKey="mobile" fill="var(--color-mobile)" radius={4} />
      </BarChart>
    </ChartContainer>
  )
}


interface Suggestion {
  label: string;
  type: string;
  detail: string;
  apply?: (view: EditorView, completion: any, from: number, to: number) => void;
}


type QueryBlockProps = {
  node: {
    attrs: {
      resourceId: string;
      blockId: string;
      title: string;
      sql: string;
      viewType: ViewType;
    };
  };
  updateAttributes: (attrs: any) => void;
}

export default function QueryBlock(props: QueryBlockProps) {
  const { resources, isFullScreen, setIsFullScreen, setFullScreenData } = useAppContext();


  const [records, setRecords] = useState([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [workflowId, setWorkflowId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [rowData, setRowData] = useState<any[] | null>(null);
  const [time, setTime] = useState<number>(0);
  const [colDefs, setColDefs] = useState<ColDef[] | null>(null);
  const [schemas, setSchemas] = useState<any[] | null>(null);
  const [dbCatalog, setDBCatalog] = useState<any[] | null>(null);
  const [resourceType, setResourceType] = useState<string>("bigquery");
  const [syntaxObject, setSyntaxObject] = useState<any>({});

  const gridRef = useRef<AgGridReact>(null);
  const timeIntervalRef = useRef<number | null>(null);
  const { id: notebookId } = useParams()


  const codeMirrorRef = useRef<ReactCodeMirrorRef | null>(null);
  let columnAutocomplete = useRef<any[] | null>(null);
  let tableAutocomplete = useRef<any[] | null>(null);

  const exportCsv = () => {
    gridRef.current!.api.exportDataAsCsv();
  };

  const onHotKey = (editor: any) => {
    console.log("~~~~~~~~ hot key pressed!!!!!!");
  };

  const getSqlParts = (editorState: EditorState, pos: number) => {
    const beforeSql = editorState
      .sliceDoc(0, pos)
      ?.replaceAll('"', "")
      .replaceAll("`", "");
    const afterSql = editorState
      .sliceDoc(pos)
      ?.replaceAll('"', "")
      .replaceAll("`", "");
    return { beforeSql, afterSql };
  };

  const matchCase = (original: string, transformed: string) => {
    const isUpperCase = (str: string) => str === str.toUpperCase();
    const isLowerCase = (str: string) => str === str.toLowerCase();

    const upperCaseCount = original.split("").filter(isUpperCase).length;
    const lowerCaseCount = original.split("").filter(isLowerCase).length;
    return upperCaseCount > lowerCaseCount
      ? transformed.toUpperCase()
      : transformed.toLowerCase();
  };

  const transformWordTable = (word: string, original: string): string => {
    const isAlphanumeric = (str: string) =>
      /^[a-zA-Z_][a-zA-Z0-9_]*$/.test(str);

    return word
      .split(".")
      .map((part) => {
        if (isAlphanumeric(part)) {
          return matchCase(original, part);
        } else {
          let quotedPart = `"${part}"`;
          if (resourceType === "bigquery") {
            quotedPart = `\`${part}\``;
          }
          return matchCase(original, quotedPart);
        }
      })
      .join(".");
  };

  const customSyntaxAutocomplete = async (state: any, pos: any) => {
    const { beforeSql, afterSql } = getSqlParts(state, pos);
    const lastWordCase = beforeSql.trim().split(/\s+/).pop() || "";
    const lastChar = beforeSql.slice(-1);
    if (lastChar === " " || lastChar === "\n") {
      return {
        from: pos,
        options: [],
      };
    }
    const keywords = syntaxObject.keywords
      .filter((key: string) =>
        key.toLowerCase().startsWith(lastWordCase.toLowerCase())
      )
      .map((keyword: any) => ({
        label: keyword,
        type: "keyword",
        detail: "keyword",
        apply: (
          view: EditorView,
          completion: any,
          from: number,
          to: number
        ) => {
          const insertText = `${transformWordTable(keyword, lastWordCase)}`;
          view.dispatch({
            changes: {
              from: from,
              to: to,
              insert: insertText,
            },
          });
        },
      }));

    const functions = syntaxObject.functions
      .filter((func: any) =>
        func.name.toLowerCase().startsWith(lastWordCase.toLowerCase())
      )
      .map((func: any) => ({
        label: func.name,
        type: "function",
        detail: func.description,
        apply: (
          view: EditorView,
          completion: any,
          from: number,
          to: number
        ) => {
          const insertText = `${transformWordTable(func.name, lastWordCase)}`;
          view.dispatch({
            changes: {
              from: from,
              to,
              insert: insertText,
            },
          });
        },
      }));

    const autocompletes = [...keywords, ...functions];

    return {
      from: pos - lastWordCase.length,
      options: autocompletes,
    };
  };

  const setTableCompletion = async (
    beforeSql: string,
    afterSql: string,
    lastWordCase: string
  ): Promise<void> => {
    const ctesSuggestions = await getCTEAutocomplete({
      resourceId: props.node.attrs.resourceId,
      beforeSql,
      afterSql,
    });

    const createCompletion = (
      label: string,
      type: string,
      detail: string
    ): Suggestion => ({
      label,
      type,
      detail,
      apply: (view: EditorView, completion: any, from: number, to: number) => {
        const insertText = ` ${transformWordTable(label, lastWordCase)}`;
        view.dispatch({
          changes: { from, to, insert: insertText },
        });
      },
    });

    const tableCompletionsCte = ctesSuggestions.map((suggestion: string) =>
      createCompletion(suggestion, "CTE", "CTE")
    );

    const tableCompletions = (dbCatalog || []).map((suggestion: string[]) =>
      createCompletion(suggestion.join("."), "table", "table")
    );

    tableAutocomplete.current = [...tableCompletions, ...tableCompletionsCte];
  };

  const setApplyFunctionOnTableCompletion = (
    lastWordCase: string
  ): Suggestion[] =>
    (tableAutocomplete.current || []).map((suggestion: Suggestion) => ({
      ...suggestion,
      apply: (view: EditorView, completion: any, from: number, to: number) => {
        const insertText = ` ${transformWordTable(
          suggestion.label,
          lastWordCase
        )}`;
        view.dispatch({
          changes: { from, to, insert: insertText },
        });
      },
    }));

  const setColumnCompletion = async (
    beforeSql: string,
    afterSql: string
  ): Promise<void> => {
    const columnSuggestions = await getColumnAutocomplete({
      resourceId: props.node.attrs.resourceId,
      beforeSql,
      afterSql,
    });

    const createCompletion = (
      label: string,
      type: string,
      detail: string
    ): Suggestion => ({
      label,
      type,
      detail,
    });

    columnAutocomplete.current = columnSuggestions.map((suggestion: string) =>
      createCompletion(suggestion, "column", "column")
    );
  };

  const setApplyFunctionOnColumnCompletion = (
    beforeSql: string,
    lastWordCase: string
  ): Suggestion[] =>
    (columnAutocomplete.current || []).map((suggestion: Suggestion) => ({
      ...suggestion,
      apply: (view: EditorView, completion: any, from: number, to: number) => {
        view.dispatch({
          changes: {
            from,
            to,
            insert: transformWordTable(suggestion.label, lastWordCase),
          },
        });
      },
    }));

  const customAutocomplete = async (context: CompletionContext) => {
    const { state, pos } = context;
    const { beforeSql, afterSql } = getSqlParts(state, pos);
    const lastWordCase = beforeSql.trim().split(/\s+/).pop() || "";
    const beforeSqlTrimmed = beforeSql.trim().toUpperCase();
    const words = beforeSqlTrimmed.split(/\s+/);
    const lastWord = words.pop() || "";
    const secondLastWord = words.pop() || "";
    const lastChar = beforeSql.slice(-1);

    if (schemas !== null) {
      if (
        (lastWord === "FROM" || lastWord === "JOIN") &&
        !(tableAutocomplete.current && tableAutocomplete.current.length > 0)
      ) {
        await setTableCompletion(beforeSql, afterSql, lastWordCase);
      }

      if (tableAutocomplete.current && tableAutocomplete.current.length > 0) {
        const parsedTableAutocomplete =
          setApplyFunctionOnTableCompletion(lastWordCase);

        if (lastWord === "FROM" || lastWord === "JOIN") {
          return { from: context.pos, options: parsedTableAutocomplete };
        }

        if (
          (secondLastWord === "FROM" || secondLastWord === "JOIN") &&
          !beforeSql.endsWith(" ")
        ) {
          const filteredOptions = parsedTableAutocomplete.filter(
            (suggestion) =>
              suggestion.label
                .toLowerCase()
                .startsWith(lastWord.toLowerCase()) || beforeSql.endsWith(" ")
          );
          return {
            from: context.pos - lastWord.length,
            options: filteredOptions,
          };
        }
      }

      if (
        lastChar === "." &&
        !(columnAutocomplete.current && columnAutocomplete.current.length > 0)
      ) {
        await setColumnCompletion(beforeSql, afterSql);
      }

      if (columnAutocomplete.current && columnAutocomplete.current.length > 0) {
        const parsedColumnAutocomplete = setApplyFunctionOnColumnCompletion(
          beforeSql,
          lastWordCase
        );

        if (lastChar === ".") {
          return { from: context.pos, options: parsedColumnAutocomplete };
        } else if (lastWord.includes(".") && !beforeSql.endsWith(" ")) {
          const wordSplit = lastWord.split(".");
          const lastWordDot = wordSplit.pop() || "";
          const filteredOptions = parsedColumnAutocomplete.filter(
            (suggestion) =>
              suggestion.label
                .toLowerCase()
                .startsWith(lastWordDot.toLowerCase())
          );
          return {
            from: context.pos - lastWordDot.length,
            options: filteredOptions,
          };
        }
      }

      columnAutocomplete.current = [];
      tableAutocomplete.current = [];
    }

    return customSyntaxAutocomplete(state, pos);
  };

  const getTablefromSignedUrl = async (signedUrl: string) => {
    const response = await fetch(signedUrl)
    if (response.ok) {
      const table = await response.json()
      const defs = Object.keys(table.column_types).map((key) => ({
        field: key,
        headerName: key,
        type: [getColumnType(table.column_types[key])],
        cellDataType: getColumnType(table.column_types[key]),
        editable: false,
        valueGetter: (p: any) => {
          if (p.colDef.cellDataType === "date") {
            return new Date(p.data[key]);
          }
          return p.data[key];
        },
        cellClass: "p-0",
      }));
      console.log({ defs, types: table.column_types, })
      setColDefs(defs);
      setRowData(table.data)
    }
    setIsLoading(false)
  }


  useEffect(() => {
    const fetchWorkflowState = async (id: string) => {
      console.log('fetchWorkflowState', id)
      const data = await getWorkflow({ workflow_run_id: id })
      console.log({ data })
      if (data.execute_query.status === 'failed') {
        setError(data.execute_query.error)
        setIsLoading(false)
      }
      if (data.execute_query && data.execute_query.status === 'success') {
        console.log(data.execute_query.signed_url)
        getTablefromSignedUrl(data.execute_query.signed_url)
      }
    }
    console.log('changed workflowId', workflowId)
    if (workflowId) {
      fetchWorkflowState(workflowId)
    }
  }, [workflowId])

  useEffect(() => {
    const fetchQueryBlockResult = async () => {
      const block = await getQueryBlockResult({ blockId: props.node.attrs.blockId })
      if (block && block.results) {
        getTablefromSignedUrl(block.results)
      }
    }
    if (props.node.attrs.blockId && !rowData) {
      fetchQueryBlockResult()
    }
  }, [props.node.attrs.blockId])

  async function runQuery(query: string) {
    setTime(0);
    setIsLoading(true);
    setError(null);
    setRowData(null);
    setColDefs(null);
    let data: any;
    try {
      data = await executeQuery({
        notebook_id: notebookId as any,
        resource_id: props.node.attrs.resourceId,
        block_id: props.node.attrs.blockId,
        sql: query,
      });
      console.log({ data })
    } catch (e: any) {
      console.error({ e })
      setError(e.toString())
    }

    setWorkflowId(data.workflow_run);


  }

  useEffect(() => {
    if (isLoading) {
      timeIntervalRef.current = window.setInterval(() => {
        setTime((prevTime) => prevTime + 0.01);
      }, 10);
    } else {
      if (timeIntervalRef.current) {
        clearInterval(timeIntervalRef.current);
      }
    }
    return () => {
      if (timeIntervalRef.current) {
        clearInterval(timeIntervalRef.current);
      }
    };
  }, [isLoading]);

  useEffect(() => {
    if (resources) {
      props.updateAttributes({
        resourceId: resources[0].id,
      })
    }
  }, [resources]);

  useEffect(() => {
    if (resourceType && resourceType.length > 0) {
      // const jsonSyntaxComplete = require("../../backend/intellisense/syntax/outputs/" +
      //   resourceType +
      //   ".json");
      // setSyntaxObject(jsonSyntaxComplete);
    }
  }, [resourceType]);

  useEffect(() => {
    if (!props.node.attrs.blockId) {
      props.updateAttributes({
        blockId: `${uuidv4()}`,
      });
    }
  }, [props.node.attrs.blockId])


  const getSchema = async (resourceId: string) => {
    const answer = await getSchemaAutocomplete({ resourceId });
    setSchemas(answer);
  };

  // const getDBAutocomplete = async (resourceId: string) => {
  //   const answer = await getDBCatalogAutocomplete({ resourceId });
  //   setDBCatalog(answer);
  // };

  useEffect(() => {
    if (schemas === null) {
      getSchema(props.node.attrs.resourceId);
    }
  }, [props.node.attrs.resourceId, schemas]);

  // useEffect(() => {
  //   if (schemas !== null && dbCatalog === null) {
  //     getDBAutocomplete(props.node.attrs.resourceId);
  //   }
  // }, [props.node.attrs.resourceId, schemas]);

  useHotkeys("meta + enter", () => console.log("hot keys pressed!"));
  useHotkeys("escape", () => console.log("escape!"));

  // const getColumns = (data: any[]): ColumnDef<any>[] => {
  //     if (data.length === 0) {
  //         return []
  //     }

  //     return Object.keys(records[0]).map((key) => ({
  //         accessorKey: key,
  //         header: () => <div className="truncate w-[125px] text-left">{key}</div>,
  //         cell: ({ row }) => {
  //             return <div className="truncate w-[125px] px-1.5 text-left font-medium">{row.getValue(key)}</div>
  //         }
  //     }))
  // }
  const handleChangeSql = (value: string) => {
    props.updateAttributes({
      sql: value,
    });
  }

  const handleChangeTitle = (e: any) => {
    props.updateAttributes({
      title: e.target.value,
    })
  }

  const renderGrid = () => {
    return (
      <div className="flex flex-col h-full flex-grow-1">
        <div className="flex flex-col h-full flex-grow-1">
          <div className="rounded-lg">
            <div className="flex text-muted-foreground font-semibold  text-sm py-1 px-0 justify-between">
              <div className='flex items-center gap-4'>

                <Tabs defaultValue={props.node.attrs.viewType} onValueChange={(viewType: string) => {
                  props.updateAttributes({
                    viewType,
                  })
                }}>
                  <TabsList>
                    <TabsTrigger className="text-xs" value="table">
                      Results
                    </TabsTrigger>
                    <TabsTrigger className="text-xs" value="chart">Chart</TabsTrigger>
                  </TabsList>
                </Tabs>
                <div className="flex items-center gap-1 text-xs">
                  <Clock className="w-4 h-4" />
                  {`Ran in ${time.toFixed(2)}s`}
                </div>
              </div>
              <div className="flex items-center gap-0">
                {false && (
                  <Button
                    className="gap-1 font-semibold"
                    variant="ghost"
                    size="sm"
                    disabled={!rowData}
                  >
                    <Filter className="w-4 h-4" />
                    <div>(Hide) Columns</div>
                  </Button>
                )}
                <Button
                  className="gap-1 font-semibold"
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setFullScreenData({
                      rowData,
                      colDefs,
                    })
                    setIsFullScreen(true)
                  }}
                  disabled={!rowData}
                >
                  {isFullScreen ? (
                    <>
                      <ChevronsDownUp className="w-4 h-4" />
                      Collapse
                    </>
                  ) : (
                    <>
                      <Expand className="w-4 h-4" />
                      FullScreen
                    </>
                  )}
                </Button>
                <Button
                  className="gap-1 font-semibold"
                  variant="ghost"
                  size="sm"
                  onClick={exportCsv}
                  disabled={!rowData}
                >
                  <Download className="w-4 h-4" />
                  Export
                </Button>
              </div>
            </div>
          </div>
          {props.node.attrs.viewType === 'table' && (
            rowData && rowData.length > 0 ? (
              <div className="flex flex-col w-full h-full flex-grow-1">
                <AgGridReact
                  className="ag-theme-custom"
                  ref={gridRef}
                  suppressRowHoverHighlight={true}
                  columnHoverHighlight={true}
                  rowData={rowData}
                  pagination={true}
                  // @ts-ignore
                  columnDefs={colDefs}
                />
              </div>
            ) : (
              <div className="opacity-80 text-muted-foreground w-full border-2 bg-muted/50 flex flex-col h-full rounded-lg justify-center items-center">
                {error && (
                  <div className="p-4 max-w-[500px]">
                    <Alert variant="destructive">
                      <ExclamationTriangleIcon className="h-4 w-4" />
                      <AlertTitle>Query Error</AlertTitle>
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  </div>
                )}
                {isLoading && (
                  <div>
                    <LoadingVinyl />
                  </div>
                )}
                {/* {!isLoading && !error && (
                                <div>
                                    <div className='flex text-md w-full items-center gap-6'>
                                        <div className='gap-2 flex items-center'>
                                            <Play className='w-5 h-5' />
                                            <div>Run query preview</div>
                                        </div>
                                        <div className='flex gap-2'>
                                            <div className='px-1 py-0.5 bg-gray-200 rounded-sm'>⌘</div>
                                            <div className='px-1 py-0.5 bg-gray-200 rounded-sm'>Enter</div>
                                        </div>
                                    </div>
                                </div>
                            )} */}
              </div>
            )
          )}
          {props.node.attrs.viewType === 'chart' && (
            <div className='h-[400px]'>
              <ChartComponent />
            </div>
          )}
        </div>
      </div >
    );
  };

  const onAceCmdEnter = (editor: any) => {
    if (!isLoading) {
      const text = editor.getValue();
      runQuery(text);
    }
  };

  console.log({ resources })

  return (
    <Fragment>
      {false ? (
        <div className="absolute top-0 left-0 bg-muted w-full h-screen z-50">
          {renderGrid()}
        </div>
      ) : (
        <div className="w-full flex-grow flex flex-col flex-1">
          <div className="pb-2 flex space-x-4 w-full items-center justify-between text-muted-foreground opacity-75">
            <input
              onChange={handleChangeTitle}
              className="text text-muted-foreground outline-none focus:ring-0 font-medium flex-grow truncate"
              value={props.node.attrs.title}
            />
            <div className="flex gap-4">
              <div className="flex items-center">
                <Select defaultValue={resources.length > 0 && resources[0].id}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a resource" />
                  </SelectTrigger>
                  <SelectContent>
                    {resources.map((resource) => (
                      <SelectItem key={resource.id} value={resource.id}>{resource.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              {/* <Button variant='ghost' className='text-sm flex items-center gap-2'>
                                <div gclassName='w-4 h-4 rounded-full bg-green-500 border ' />
                                Run #1
                                <ChevronDown className='w-5 h-5' />
                            </Button> */}

              <Button
                disabled={isLoading}
                variant="outline"
                onClick={() => runQuery(props.node.attrs.sql)}
              >
                {isLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Play className="mr-2 w-4 h-4 text-green-500" />
                )}
                Run
              </Button>
            </div>
          </div>
          <Card className="rounded-md bg-muted/50">
            <CardContent className="p-0 z-20">
              <CodeMirror
                basicSetup={{
                  highlightActiveLine: false,
                }}
                extensions={[
                  sql(),
                  EditorView.lineWrapping,
                  autocompletion({
                    override: [customAutocomplete],
                  }),
                ]}
                ref={codeMirrorRef}
                value={props.node.attrs.sql}
                onChange={(value) => handleChangeSql(value)}
                className="text-sm"
                theme={quietlight}
                // @ts-ignore
                options={{
                  keyMap: "sublime",
                  mode: "pgsql",
                  defaultTextHeight: "12px",
                  extraKeys: {
                    "Cmd+Enter": onHotKey,
                  },
                }}
              />
            </CardContent>
          </Card>
          {(isLoading || rowData || error) && (
            <div className="h-[400px] flex flex-col flex-grow-1">
              {renderGrid()}
            </div>
          )}
        </div>
      )
      }

    </Fragment >
  );
}
