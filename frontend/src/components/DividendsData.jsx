import React, { useEffect, useState } from "react";
import { FetchPaperData } from "./FetchData";
import { formatValue, formatDate } from "../assets/formatFuncs";
import { divsLabels, regilarityMapping } from "../assets/paperData";

const DividendsData = (props) => {
  const { ticker } = props;
  const [mainData, setMainData] = useState(null);

  useEffect(() => {
    setMainData(null);
    const fetchData = async () => {
      try {
        const paperData = await FetchPaperData("/api/dividend_data/", ticker);
        console.log("fetched DividendsData", paperData);
        setMainData(paperData.dividends);
      } catch (error) {
        console.error("can't fetch dividends data:", error);
      }
    };
    fetchData();
  }, [ticker]);

  // Пока данные не загружены – показываем индикатор загрузки
  if (mainData === null) {
    return (
      <div className="flex-col">
        <div className="font-medium w-full text-center p-1 bg-sky-100 text-sky-700 rounded-t-lg">Дивиденды</div>
        <div className="text-sm bg-white p-4 rounded-b-lg flex justify-center items-center">
          <span className="text-slate-500">Загрузка...</span>
        </div>
      </div>
    );
  }

  // Если данные пусты – ничего не отображаем
  if (!mainData || Object.keys(mainData).length === 0) return null;

  return (
    <div className="flex-col">
      <div className="font-medium w-full text-center p-1 bg-sky-100 text-sky-700 rounded-t-lg">Дивиденды</div>
      <div className="text-sm bg-white p-4 rounded-b-lg">
        <ul className="space-y-1">
          {Object.keys(mainData)
            .filter((key) => {
              return (
                mainData[key] &&
                mainData[key].value &&
                mainData[key].value !== "" &&
                mainData[key].value !== "0" &&
                mainData[key].value !== "0.00" &&
                mainData[key].value !== "0.0"
              );
            })
            .map((key) => {
              let displayValue;

              if (key === "regularity") {
                displayValue = regilarityMapping[mainData[key].value] || mainData[key].value;
              } else if (
                ["payment_date", "declared_date", "last_buy_date", "record_date", "created_at", "ex_dividend_date"].includes(key)
              ) {
                displayValue = formatDate(mainData[key].value);
              } else {
                displayValue = mainData[key].value;
                if (mainData[key].unit) {
                  displayValue += ` ${mainData[key].unit}`;
                }
              }
              return (
                <li key={key}>
                  <span className="font-semibold py-0.5 px-1 mr-1">{divsLabels[key] || key}:</span>
                  {displayValue}
                </li>
              );
            })}
        </ul>
      </div>
    </div>
  );
};

export default DividendsData;
