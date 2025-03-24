import React, { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@gravity-ui/uikit";
import PaperMainData from "./PaperMainData";
import DividendsData from "./DividendsData";
import Multiplicators from "./Multiplicators";
import Sectors from "./Sectors";
import PeriodButtons from "./PeriodButtons";
import IndexIchimoku2 from "./IndexIchimoku2";

const CompaniesPage = (props) => {
  const companies = ["SBER", "GAZP", "HEAD", "OZON", "PIKK"];
  const [activeComp, setActiveComp] = useState("SBER");

  const [chartData, setChartData] = useState([]);
  const [currentTicker, setCurrentTicker] = useState("SBER");

  const handleTickerChange = (newTicker) => {
    setCurrentTicker(newTicker);
  };

  function handleClickedComp(comp) {
    setActiveComp(comp);
  }

  return (
    <>
      <div className="text-sm justify-center flex flex-row gap-4 sm:gap-4 md:gap-5 ">
        {companies.map((comp) => (
          <Button
            key={comp}
            selected={activeComp === comp}
            // view="outlined-info"
            size="m"
            width="small"
            onClick={() => handleClickedComp(comp)}
          >
            {comp}
          </Button>
        ))}
      </div>

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
    </>
  );
};

export default CompaniesPage;
