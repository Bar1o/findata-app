import React, { useEffect, useState } from "react";
import PaperMainData from "./PaperMainData";
import DividendsData from "./DividendsData";
import Multiplicators from "./Multiplicators";
import Sectors from "./Sectors";
import PeriodButtons from "./PeriodButtons";
import IndexIchimoku from "./IndexIchimoku";
import SharePrice from "./SharePrice";
import CustomLabel from "./CustomLabel";
import AllTickers from "./AllTickers";
import PeData from "./PeData";
import { Switch } from "@gravity-ui/uikit";
import InfoIchimoku from "./InfoIchimoku"; // импорт новой компоненты

const CompaniesPage = ({ ticker, availableTickers, isTickerPaused }) => {
  const companies = ["SBER", "GAZP", "HEAD", "OZON", "PIKK"];
  const [activeComp, setActiveComp] = useState(ticker);
  const [period, setPeriod] = useState("W");
  const [showLines, setShowLines] = useState(true);
  const [showIchimokuInfo, setShowIchimokuInfo] = useState(false); // состояние для показа описания

  useEffect(() => {
    setActiveComp(ticker);
  }, [ticker]);

  const handleClickedComp = (comp) => {
    setActiveComp(comp);
  };

  return (
    <>
      <AllTickers tickerList={availableTickers} onSelectTicker={setActiveComp} isPaused={isTickerPaused} />

      <IndexIchimoku ticker={activeComp} period={period} showLines={showLines} />

      <div className="flex flex-row flex-wrap justify-between items-center p-2 sm:gap-4 md:gap-5">
        <PeriodButtons period={period} setPeriod={setPeriod} />
        <div className="flex flex-row gap-2">
          <CustomLabel onClick={() => setShowIchimokuInfo((prev) => !prev)} className="cursor-pointer">
            Описание
          </CustomLabel>
          <div>
            <Switch onChange={() => setShowLines(!showLines)} className="cursor-pointer">
              Без маркеров
            </Switch>
          </div>
        </div>
      </div>

      {showIchimokuInfo && <InfoIchimoku />}

      <div className="flex flex-col md:flex-row gap-2 md:gap-4 w-full mb-2 md:mb-4">
        <div className="flex flex-col gap-3 w-full md:w-1/3">
          <PaperMainData ticker={activeComp} />
          <Sectors ticker={activeComp} onTickerSelect={setActiveComp} />
        </div>
        <div className="w-full md:w-1/3">
          <SharePrice ticker={activeComp} />
          <DividendsData ticker={activeComp} />
          <PeData ticker={activeComp} />
        </div>
        <div className="w-full md:w-1/3">
          <Multiplicators ticker={activeComp} />
        </div>
      </div>
    </>
  );
};

export default CompaniesPage;
