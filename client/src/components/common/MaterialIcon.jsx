import React from "react";

export function MaterialIcon({ children, className = "", style = {} }) {
  return (
    <span
      className={`material-symbols-outlined ${className}`.trim()}
      style={style}
    >
      {children}
    </span>
  );
}
