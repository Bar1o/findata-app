import React, { useEffect, useState } from "react";
import { FetchPaperData } from "./FetchData";
import { formatValue, formatDate } from "../assets/formatFuncs";
import { multiplicatorsLabels, metricGroups, groupHeaders } from "../assets/paperData";

const Multiplicators = (props) => {
  const { ticker } = props;
  const [mainData, setMainData] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const paperData = await FetchPaperData("/api/multiplicators_data/", ticker);
        console.log("fetched Multiplicators", paperData);
        setMainData(paperData.multiplicators);
      } catch (error) {
        console.error("can't fetch Multiplicators data:", error);
      }
    };
    fetchData();
  }, [ticker]);

  const renderMetricGroup = (group) => {
    if (!mainData) return null;

    // Filter metrics that belong to this group and have data
    const metricsInGroup = metricGroups[group].filter(
      (key) => mainData[key] && mainData[key].value && mainData[key].value !== "0" && mainData[key].value !== "0.00"
    );

    if (metricsInGroup.length === 0) return null;
    return (
      <div className="" key={group}>
        <div className="text-sm w-full text-center p-0.5 bg-sky-50 text-gray-800">{groupHeaders[group]}</div>
        <div className="bg-white p-4 rounded-b-lg">
          <ul className="">
            {metricsInGroup.map((key) => {
              const metric = mainData[key];
              let displayValue;

              if (key === "ex_dividend_date") {
                displayValue = formatDate(metric.value);
              } else {
                displayValue = `${metric.value}${metric.unit ? " " + metric.unit : ""}`;
              }

              return (
                <li key={key} className="text-sm">
                  <span className="font-semibold">{multiplicatorsLabels[key] || key}:</span> {displayValue}
                </li>
              );
            })}
          </ul>
        </div>
      </div>
    );
  };
  return (
    <div className="">
      <div className="font-medium text-center w-full p-1 bg-sky-100 text-sky-700 rounded-t-lg">Финансовые показатели</div>

      {Object.keys(metricGroups).map((group) => renderMetricGroup(group))}
    </div>
  );
};

export default Multiplicators;
