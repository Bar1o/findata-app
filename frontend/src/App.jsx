import { useState } from "react";
import HomePage from "./components/HomePage";
import Header from "./components/Header";
import { Button } from "@gravity-ui/uikit";
import CompaniesPage from "./components/CompaniesPage";
import GdpData from "./components/GdpData";
import GdpSectors from "./components/GdpSectors";
import InflData from "./components/InflData";
import QuestionsAndAnswers from "./components/QuestionsAndAnswers";
import AllRights from "./components/AllRights";
import KeyRateData from "./components/KeyRateData";

function App() {
  const availableTickers = [
    "SBER",
    "VTBR",
    "MGNT",
    "SMLT",
    "SVCB",
    "OKEY",
    "CBOM",
    "TATN",
    "ASTR",
    "YDEX",
    "OZON",
    "LENT",
    "GAZP",
    "HEAD",
    "PIKK",
    "X5",
    "LSRG",
    "MSTT",
    "ROSN",
    "LKOH",
    "NVTK",
    "T",
  ];

  const [currentTicker, setCurrentTicker] = useState("SBER");
  const [onCompPage, setOnCompPage] = useState(true);
  const [showInflation, setShowInflation] = useState(false);
  const [isTickerPaused, setIsTickerPaused] = useState(false);

  const handleSearch = () => {
    const input = prompt("Введите тикер:");
    if (!input) return;
    const normalized = input.trim().toUpperCase();
    if (availableTickers.includes(normalized)) {
      setCurrentTicker(normalized);
    } else {
      alert("Неверный тикер");
    }
  };

  const toggleTicker = () => {
    setIsTickerPaused((prev) => !prev);
  };

  return (
    <div className="flex flex-col p-4 max-w-[1200px] mx-auto w-full">
      <section className="min-h-screen flex flex-col">
        <Header
          onToggleInflation={() => setShowInflation((prev) => !prev)}
          onSearch={handleSearch}
          isTickerPaused={isTickerPaused}
          onToggleTicker={toggleTicker}
          isCompaniesPage={onCompPage}
        />

        {showInflation && (
          <div>
            <InflData />
            <KeyRateData />
          </div>
        )}

        <div className="flex gap-4 mb-4 justify-center">
          <Button size="m" selected={onCompPage === true} onClick={() => setOnCompPage(true)}>
            Компании
          </Button>
          <Button size="m" selected={onCompPage === false} onClick={() => setOnCompPage(false)}>
            ВВП
          </Button>
        </div>

        {onCompPage ? (
          <CompaniesPage ticker={currentTicker} availableTickers={availableTickers} isTickerPaused={isTickerPaused} />
        ) : (
          <>
            <GdpSectors />
            <GdpData />
            <QuestionsAndAnswers />
          </>
        )}
      </section>
      <AllRights />
      <div className="flex items-center justify-center gap-4">
        <p className="font-light text-grey-400 text-sm">
          Credits on <span className="text-blue-400">@vabarnis</span>, 2025
        </p>
      </div>
      <footer></footer>
    </div>
  );
}

export default App;
