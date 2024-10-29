import React, { memo } from "react";

function LoadingNode({ id, data }: any) {
  return (
    <div className="opacity-50 px-2 animate-pulse cursor-pointer h-[250px] border-2 border-slate-400 p-1 font-mono shadow-lg text-[10px] bg-neutral-100 w-64 text-black rounded-md">
      <div className="animate-pulse p-2 mx mt-4 h-[24px] w-[100%] rounded-sm bg-slate-300" />
      <div className="mt-8">
        <div className="animate-pulse mt-4 h-[14px] w-[100%] rounded-sm bg-slate-300" />
        <div className="animate-pulse mt-4 h-[14px] w-[100%] rounded-sm bg-slate-300" />
        <div className="animate-pulse mt-4 h-[14px] w-[100%] rounded-sm bg-slate-300" />
        <div className="animate-pulse mt-4 h-[14px] w-[100%] rounded-sm bg-slate-300" />
        <div className="animate-pulse mt-4 h-[14px] w-[100%] rounded-sm bg-slate-300" />
      </div>
    </div>
  );
}

export default memo(LoadingNode);
