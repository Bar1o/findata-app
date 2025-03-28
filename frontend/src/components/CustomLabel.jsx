import React from "react";

const CustomLabel = ({ children, theme, className = "", ...props }) => {
  const baseClass = "text-slate-600 inline-flex items-center text-sm";
  const themeClass =
    theme === "clear"
      ? "border border-slate-300 rounded-md px-3 py-1" // для темы clear: обводка, скругление и отступы
      : "bg-slate-200 rounded-sm px-3 py-1";
  return (
    <div className={`${baseClass} ${themeClass} ${className}`} {...props}>
      {children}
    </div>
  );
};

export default CustomLabel;
