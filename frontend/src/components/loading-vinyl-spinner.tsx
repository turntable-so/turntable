import React, { useRef, useState } from "react";

import "./loading-spinner.css";

export interface LoadingSpinnerProps {
  size?: number;
}

export default function LoadingVinyl({ size }: LoadingSpinnerProps) {
  size = size || 32;
  const [isDragging, setIsDragging] = useState(false);
  const [rotation, setRotation] = useState(0);
  const lastAngleRef = useRef<number | null>(null);

  const handleMouseDown = (e: any) => {
    try {
      setIsDragging(true);
      const rect = e.currentTarget.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const angle =
        Math.atan2(e.clientY - centerY, e.clientX - centerX) * (180 / Math.PI);
      lastAngleRef.current = angle;
    } catch (e) {}
  };

  const handleMouseMove = (e: any) => {
    if (!isDragging) return;

    try {
      const rect = e.currentTarget.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const angle =
        Math.atan2(e.clientY - centerY, e.clientX - centerX) * (180 / Math.PI);
      const deltaAngle = angle - (lastAngleRef.current || 0);

      setRotation((prevRotation) => prevRotation + deltaAngle);
      lastAngleRef.current = angle;
    } catch (e) {}
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const style = {
    width: `${size}px`,
    height: `${size}px`,
    transform: `rotate(${rotation}deg)`,
  };

  return (
    <div
      className="vinyl-container"
      style={style}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      <div className={`vinyl ${isDragging ? "paused" : ""}`}>
        <div
          className={`reflection reflection-top ${isDragging ? "paused" : ""}`}
        ></div>
        <div
          className={`reflection reflection-bottom ${
            isDragging ? "paused" : ""
          }`}
        ></div>
        <div className="groove"></div>
        <div className="label">
          <div className="groove"></div>
          <div className="inner-label"></div>
        </div>
        <div className="hole"></div>
      </div>
    </div>
  );
}
