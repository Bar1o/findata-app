import { useState } from "react";
import HomePage from "./components/HomePage";
import Header from "./components/Header";
import PeriodButtons from "./components/PeriodButtons";
import IndexIchimoku2 from "./components/IndexIchimoku2";
import CompaniesPage from "./components/CompaniesPage";
import PaperMainData from "./components/PaperMainData";
import DividendsData from "./components/DividendsData";
import Multiplicators from "./components/Multiplicators";
import Sectors from "./components/Sectors";

function App() {
  // TODO: далее фиги на каждой странице свой
  // const [onCompPage, setOnCompPage] = useState(true);
  const [chartData, setChartData] = useState([]);
  const [currentTicker, setCurrentTicker] = useState("SBER");
  const figi = "BBG004730N88";

  const handleTickerChange = (newTicker) => {
    setCurrentTicker(newTicker);
  };

  return (
    <div className="flex flex-col p-4 max-w-[1200px] mx-auto w-full">
      <section className="min-h-screen flex flex-col">
        <Header />

        {/* <button onClick={() => setOnCompPage(true)}>{onCompPage ? <HomePage /> : ""}</button> */}
        <CompaniesPage />
        <IndexIchimoku2 ticker={currentTicker} data={chartData} />
        <PeriodButtons ticker={currentTicker} setChartData={setChartData} />

        {/* Стек вертикально на мобильных, горизонтально на планшетах и выше */}
        <div className="flex flex-col md:flex-row gap-2 md:gap-4 w-full mb-2 md:mb-4">
          <div className="flex flex-col gap-3 w-full md:w-1/3 mb-2 md:mb-0">
            <PaperMainData ticker={currentTicker} />
            <Sectors ticker={currentTicker} onTickerSelect={handleTickerChange} />
          </div>
          <div className="w-full md:w-1/3 mb-2 md:mb-0">
            <DividendsData figi={currentTicker} />
          </div>
          <div className="w-full md:w-1/3">
            <Multiplicators ticker={currentTicker} />
          </div>
        </div>

        {/* Вторая группа компонентов */}
        <div className="flex flex-row mx-auto gap-4 pt-2 w-full justify-between">
          <PaperMainData ticker={currentTicker} />
          <PaperMainData ticker={currentTicker} />
        </div>
        {/* <div className="flex flex-col md:flex-row gap-2 md:gap-4 w-full">
          <div className="w-full md:w-1/2 mb-2 md:mb-0">
            <PaperMainData ticker={currentTicker} />
          </div>
          <div className="w-full md:w-1/2">
            <PaperMainData ticker={currentTicker} />
          </div>
        </div> */}
      </section>
      <div className="flex items-center justify-center gap-4">
        <p className="font-light text-grey-400 text-sm">
          Credits on <span className="text-blue-400">@vabarnis</span>
          {/* add a link here */}
        </p>
      </div>
      <footer></footer>
    </div>
  );
}

export default App;
