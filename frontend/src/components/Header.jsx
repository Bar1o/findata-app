import React from "react";
import KeyRateBar from "./KeyRateBar";
import CurrencyBar from "./CurrencyBar";
import Imoex from "./Imoex";

export default function Header({ onToggleInflation }) {
  return (
    <header className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-2">
      <h1 className="font-medium">
        Fin<span className="text-blue-500 bold">Data</span>
      </h1>
      <div className="flex flex-wrap gap-2">
        <KeyRateBar onToggleInflation={onToggleInflation} />
        <CurrencyBar />
        <Imoex />
      </div>
      <button className="flex items-center gap-2">
        <p>Поиск</p>
        <i className="fa-solid fa-magnifying-glass"></i>
      </button>
    </header>
  );
}
