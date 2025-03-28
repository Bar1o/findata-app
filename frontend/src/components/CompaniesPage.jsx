import React, { useEffect, useState } from "react";
import { Button } from "@gravity-ui/uikit";
import PaperMainData from "./PaperMainData";
import DividendsData from "./DividendsData";
import Multiplicators from "./Multiplicators";
import Sectors from "./Sectors";
import PeriodButtons from "./PeriodButtons";
import IndexIchimoku2 from "./IndexIchimoku2";
import SharePrice from "./SharePrice";

const CompaniesPage = ({ ticker }) => {
  const companies = ["SBER", "GAZP", "HEAD", "OZON", "PIKK"];
  // Используем единое состояние для выбранного тикера
  const [activeComp, setActiveComp] = useState(ticker);

  // При изменении тикера (например, через поиск) синхронизируем
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

      <IndexIchimoku2 ticker={activeComp} data={[]} />
      <PeriodButtons ticker={activeComp} setChartData={() => {}} />

      <div className="flex flex-col md:flex-row gap-2 md:gap-4 w-full mb-2 md:mb-4">
        <div className="flex flex-col gap-3 w-full md:w-1/3">
          <PaperMainData ticker={activeComp} />
          <Sectors ticker={activeComp} onTickerSelect={setActiveComp} />
        </div>
        <div className="w-full md:w-1/3">
          <SharePrice ticker={activeComp} />
          <DividendsData figi={activeComp} />
        </div>
        <div className="w-full md:w-1/3">
          <Multiplicators ticker={activeComp} />
        </div>
      </div>
    </>
  );
};

export default CompaniesPage;
