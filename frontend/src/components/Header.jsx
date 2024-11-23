import React from "react";

export default function Header() {
  return (
    <header className="flex items-center justify-between gap-4 p-2">
      <h1 className="font-medium">
        Fin<span className="text-blue-500 bold">Data</span>
      </h1>
      <button className="flex items-center gap-2">
        <p>Search</p>
        <i class="fa-solid fa-magnifying-glass"></i>
      </button>
    </header>
  );
}
