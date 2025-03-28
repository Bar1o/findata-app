import { useState } from "react";
import HomePage from "./components/HomePage";
import Header from "./components/Header";
import { Button } from "@gravity-ui/uikit";
import CompaniesPage from "./components/CompaniesPage";
import GdpData from "./components/GdpData";
import GdpSectors from "./components/GdpSectors";
import InflData from "./components/InflData";
import QuestionsAndAnswers from "./components/QuestionsAndAnswers";

function App() {
  // Список доступных тикеров (можно вынести отдельно или получать с сервера)
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

  // Обработчик поиска
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

  return (
    <div className="flex flex-col p-4 max-w-[1200px] mx-auto w-full">
      <section className="min-h-screen flex flex-col">
        <Header onToggleInflation={() => setShowInflation((prev) => !prev)} onSearch={handleSearch} />

        {showInflation && <InflData />}

        <div className="flex gap-4 mb-4 justify-center">
          <Button size="m" onClick={() => setOnCompPage(true)}>
            Компании
          </Button>
          <Button size="m" onClick={() => setOnCompPage(false)}>
            ВВП
          </Button>
        </div>

        {onCompPage ? (
          <CompaniesPage ticker={currentTicker} />
        ) : (
          <>
            <GdpSectors />
            <GdpData />
            <QuestionsAndAnswers />
          </>
        )}
      </section>
      <div className="flex items-center justify-center gap-4">
        <p className="font-light text-grey-400 text-sm">
          Credits on <span className="text-blue-400">@vabarnis</span>
        </p>
      </div>
      <footer></footer>
    </div>
  );
}

export default App;
