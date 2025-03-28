// filepath: [CompaniesPage.jsx](http://_vscodecontentref_/0)
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

const CompaniesPage = ({ ticker }) => {
  const companies = ["SBER", "GAZP", "HEAD", "OZON", "PIKK"];
  const [activeComp, setActiveComp] = useState(ticker);
  const [period, setPeriod] = useState("W"); // состояние периода
  const [showLines, setShowLines] = useState(true); // состояние для показа линий

  useEffect(() => {
    setActiveComp(ticker);
  }, [ticker]);

  const handleClickedComp = (comp) => {
    setActiveComp(comp);
  };

  return (
    <>
      <div className="text-sm flex flex-row gap-4">
        {companies.map((comp) => (
          <Button key={comp} selected={activeComp === comp} size="m" width="small" onClick={() => handleClickedComp(comp)}>
            {comp}
          </Button>
        ))}
      </div>

      {/* Передаём выбранный период и состояние showLines в IndexIchimoku2 */}
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
