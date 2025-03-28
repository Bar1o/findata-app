import React from "react";
import KeyRateBar from "./KeyRateBar";
import CurrencyBar from "./CurrencyBar";
import Imoex from "./Imoex";
import { Switch } from "@gravity-ui/uikit";

export default function Header({ onToggleInflation, onSearch, isTickerPaused, onToggleTicker }) {
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
      <Switch onChange={onToggleTicker}>{isTickerPaused ? "Запустить строку" : "Остановить строку"}</Switch>

      <div className="flex items-center gap-4">
        <button className="flex items-center gap-2" onClick={onSearch}>
          <p>Поиск</p>
          <i className="fa-solid fa-magnifying-glass"></i>
        </button>
      </div>
    </header>
  );
}
