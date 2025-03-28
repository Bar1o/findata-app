import React, { useEffect, useState } from "react";
import { FetchPaperData } from "./FetchData";
import { formatValue, formatDate } from "../assets/formatFuncs";
import { multiplicatorsLabels, metricGroups, groupHeaders } from "../assets/paperData";

const Multiplicators = (props) => {
  const { ticker } = props;
  // Изначально null, чтобы отличать состояние "ещё не загружено"
  const [mainData, setMainData] = useState(null);

  useEffect(() => {
    // При смене тикера очищаем старые данные
    setMainData(null);
    const fetchData = async () => {
      try {
        const paperData = await FetchPaperData("/api/multiplicators_data/", ticker);
        console.log("fetched Multiplicators", paperData);
        setMainData(paperData.multiplicators);
      } catch (error) {
        console.error("can't fetch Multiplicators data:", error);
        setMainData({}); // При ошибке возвращаем пустой объект
      }
    };
    fetchData();
  }, [ticker]);

  // Пока данные не загружены – отображаем индикатор загрузки
  if (mainData === null) {
    return (
      <div className="">
        <div className="font-medium text-center w-full p-1 bg-sky-100 text-sky-700 rounded-t-lg">Финансовые показатели</div>
        <div className="bg-white p-4 rounded-b-lg flex justify-center items-center">
          <span className="text-slate-500">Загрузка...</span>
        </div>
      </div>
    );
  }

  const renderMetricGroup = (group) => {
    if (!mainData) return null;

    // Фильтруем метрики группы, где есть реальные значения
    const metricsInGroup = metricGroups[group].filter(
      (key) => mainData[key] && mainData[key].value && mainData[key].value !== "0" && mainData[key].value !== "0.00"
    );

    if (metricsInGroup.length === 0) return null;
    return (
      <div className="" key={group}>
        <div className="text-sm w-full text-center p-0.5 bg-sky-50 text-gray-800">{groupHeaders[group]}</div>
        <div className="bg-white p-4 rounded-b-lg">
          <ul className="space-y-1">
            {metricsInGroup.map((key) => {
              const metric = mainData[key];
              let displayValue;
              if (key === "ex_dividend_date") {
                displayValue = formatDate(metric.value);
              } else if (["average_daily_volume_last_10_days", "average_daily_volume_last_4_weeks"].includes(key)) {
                displayValue = `${formatValue(metric.value)}${metric.unit ? " " + metric.unit : ""}`;
              } else {
                displayValue = `${metric.value}${metric.unit ? " " + metric.unit : ""}`;
              }
              return (
                <li key={key} className="text-sm">
                  <span className="font-semibold py-0.5 px-1">{multiplicatorsLabels[key] || key}:</span> {displayValue}
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
