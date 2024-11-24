import React, { useEffect, useRef, useState } from "react";
import { createChart } from "lightweight-charts";
import { Button } from "@gravity-ui/uikit";
import { FetchDataByPeriod, TransformData } from "./FetchData";

const PeriodButtons = ({ figi, chartType }) => {
  function handleClickedPeriod(period) {
    console.log("Data for period", period);
    const rawData = FetchDataByPeriod({ figi, period });
    const data = TransformData(rawData);
  }
  return (
    <div className="text-sm flex-1 p-2 flex flex-row gap-2 sm:gap-4 md:gap-5 ">
      <Button view="outlined-info" size="l" width="small" onClick={() => handleClickedPeriod("D")}>
        D
      </Button>
      <Button view="outlined-info" size="l" width="small" onClick={() => handleClickedPeriod("W")}>
        W
      </Button>
      <Button view="outlined-info" size="l" width="small" onClick={() => handleClickedPeriod("M")}>
        M
      </Button>
      <Button view="outlined-info" size="l" width="small" onClick={() => handleClickedPeriod("Y")}>
        Y
      </Button>
    </div>
  );
};

PeriodButtons.propTypes = {
  figi: PropTypes.string.isRequired,
  chartType: PropTypes.func.isRequired,
};

export default PeriodButtons;
