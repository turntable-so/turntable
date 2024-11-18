import React, { memo, useContext } from "react";
import { LineageViewContext } from "../../app/contexts/LineageView";

const ErrorIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    strokeWidth="1.5"
    stroke="currentColor"
    className="w-6 h-6"
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
    />
  </svg>
);

function ErrorNode() {
  const { error } = useContext(LineageViewContext);

  return (
    <div className="opacity-50 cursor-pointer h-[250px] border-2 border-slate-400 p-1 shadow-lg text-[10px] bg-neutral-100 w-64 text-slate-700 rounded-md flex justify-center">
      <div className="flex justify-center items-center">
        <div className="mr-1">
          <ErrorIcon />
        </div>
        <p className="font-semibold">{error || "something went wrong"}</p>
      </div>
    </div>
  );
}

export default memo(ErrorNode);
