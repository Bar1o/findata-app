import React, { useEffect, useState } from "react";
import { FetchPaperData } from "./FetchData";
import { formatValue, formatDate } from "../assets/formatFuncs";
import { divsLabels, regilarityMapping } from "../assets/paperData";

const DividendsData = (props) => {
  const { figi } = props;
  const [mainData, setMainData] = useState("");
  useEffect(() => {
    const fetchData = async () => {
      try {
        const paperData = await FetchPaperData("/api/dividend_data/", figi);
        console.log("fetched DividendsData", paperData);
        setMainData(paperData.dividends);
      } catch (error) {
        console.error("can't fetch dividends data:", error);
      }
    };
    fetchData();
  }, [figi]);

  return (
    <div className="flex-col">
      <div className="font-medium w-full text-center p-1 bg-sky-100 text-sky-700 rounded-t-lg">Дивиденды</div>
      <div className="text-sm bg-white p-4 rounded-b-lg">
        {mainData && (
          <ul className="space-y-1">
            {Object.keys(mainData)
              .filter((key) => {
                return (
                  // если у элементов пустые значения
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
                  // Обрабатываем регулярность выплат с учетом мэппинга
                  displayValue = regilarityMapping[mainData[key].value] || mainData[key].value;
                } else if (
                  ["payment_date", "declared_date", "last_buy_date", "record_date", "created_at", "ex_dividend_date"].includes(key)
                ) {
                  displayValue = formatDate(mainData[key].value);
                } else {
                  // значение с единицей измерения, если она есть
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
        )}
      </div>
    </div>
  );
};

export default DividendsData;
