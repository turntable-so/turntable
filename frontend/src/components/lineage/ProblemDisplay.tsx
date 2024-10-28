// @ts-nocheck
import React, { useState } from "react";

const ProblemIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    strokeWidth={1.5}
    stroke="currentColor"
    className="w-6 h-6"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
    />
  </svg>
);

const CloseIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    strokeWidth={1.5}
    stroke="currentColor"
    className="w-5 h-5"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M6 18L18 6M6 6l12 12"
    />
  </svg>
);

export default function ProblemDisplay({ problem }) {
  const [collapsed, setCollapsed] = useState<boolean>(true);
  if (!collapsed) {
    return (
      <div className="w-64 bg-zinc-200 rounded-lg text-gray-500 p-2 text-xs">
        <div className="flex justify-between items-center">
          <div className="text-sm font-bold">{problem.title}</div>
          <div
            onClick={() => setCollapsed(true)}
            className="hover:gray-700 cursor-pointer"
          >
            <CloseIcon />
          </div>
        </div>
        <div className="py-2">{problem.msg}</div>
      </div>
    );
  }
  return (
    <div
      onClick={() => setCollapsed(false)}
      className="hover:amber-400 cursor-pointer rounded-md flex justify-center items-center text-white bg-amber-300 p-1"
    >
      <ProblemIcon />
    </div>
  );
}
