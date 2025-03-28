import React, { useEffect, useState } from "react";
import { Button } from "@gravity-ui/uikit";
import PaperMainData from "./PaperMainData";
import DividendsData from "./DividendsData";
import Multiplicators from "./Multiplicators";
import Sectors from "./Sectors";
import PeriodButtons from "./PeriodButtons";
import IndexIchimoku2 from "./IndexIchimoku2";
import SharePrice from "./SharePrice";
import CustomLabel from "./CustomLabel";
import AllTickers from "./AllTickers";

const CompaniesPage = ({ ticker, availableTickers, isTickerPaused }) => {
  const companies = ["SBER", "GAZP", "HEAD", "OZON", "PIKK"];
  const [activeComp, setActiveComp] = useState(ticker);
  const [period, setPeriod] = useState("W");
  const [showLines, setShowLines] = useState(true);

  useEffect(() => {
    setActiveComp(ticker);
  }, [ticker]);

  const handleClickedComp = (comp) => {
    setActiveComp(comp);
  };

  return (
    <>
      <AllTickers tickerList={availableTickers} onSelectTicker={setActiveComp} isPaused={isTickerPaused} />

      <IndexIchimoku2 ticker={activeComp} period={period} showLines={showLines} />

      <div className="flex flex-row justify-between items-center p-2 sm:gap-4 md:gap-5">
        <PeriodButtons period={period} setPeriod={setPeriod} />
        <CustomLabel onClick={() => setShowLines(!showLines)} className="cursor-pointer">
          {showLines ? "Убрать маркеры" : "Показать маркеры"}
        </CustomLabel>
      </div>

      <div className="flex flex-col md:flex-row gap-2 md:gap-4 w-full mb-2 md:mb-4">
        <div className="flex flex-col gap-3 w-full md:w-1/3">
          <PaperMainData ticker={activeComp} />
          <Sectors ticker={activeComp} onTickerSelect={setActiveComp} />
        </div>
        <div className="w-full md:w-1/3">
          <SharePrice ticker={activeComp} />
          <DividendsData ticker={activeComp} />
        </div>
        <div className="w-full md:w-1/3">
          <Multiplicators ticker={activeComp} />
        </div>
      </div>
    </>
  );
};

export default CompaniesPage;
