import React, { useCallback, useEffect, useRef, useState } from "react";
import { createChart } from "lightweight-charts";
import PropTypes, { number } from "prop-types";
import { Button } from "@gravity-ui/uikit";
import { FetchDataByPeriod, TransformData } from "./FetchData";

const PeriodButtons = ({ figi, setChartData }) => {
  const periods = ["D", "3D", "W", "M", "3M", "Y"];

  const [activePeriod, setActivePeriod] = useState("D");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const handleClickedPeriod = useCallback(
    async (period) => {
      setActivePeriod(period);
      setLoading(true);
      setError(null);

      try {
        const rawData = await FetchDataByPeriod({ figi, period });
        const transformedData = TransformData(rawData);
        setChartData(transformedData);
      } catch (err) {
        console.error(`Error fetching data for period "${period}":`, err);
        setError("Failed to fetch data. Please try again.");
        setChartData([]); // Optionally clear existing chart data on error
      } finally {
        setLoading(false);
      }
    },
    [figi, loading, setChartData]
  );

  return (
    <div className="text-sm flex flex-row gap-2 sm:gap-4 md:gap-5 ">
      {periods.map((period) => (
        <Button
          key={period}
          selected={activePeriod === period}
          // view="outlined-info"
          size="l"
          width="small"
          onClick={() => handleClickedPeriod(period)}
        >
          {period}
        </Button>
      ))}
    </div>
  );
};

PeriodButtons.propTypes = {
  figi: PropTypes.string.isRequired,
  setChartData: PropTypes.func.isRequired,
};

export default PeriodButtons;
