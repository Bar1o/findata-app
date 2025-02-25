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
      <div className="w-full text-center p-1 bg-sky-100 text-sky-700 rounded-t-lg">Дивиденды</div>
      <div className="bg-white p-2 rounded-b-lg">
        {mainData && (
          <ul>
            {Object.keys(mainData)
              .filter((key) => mainData[key])
              .map((key) => {
                let displayValue = formatValue(mainData[key]);
                if (key === "regularity") {
                  displayValue = regilarityMapping[mainData[key]] || mainData[key];
                } else if (["payment_date", "declared_date", "last_buy_date", "record_date", "created_at"].includes(key)) {
                  displayValue = formatDate(mainData[key]);
                }
                return (
                  <li key={key}>
                    <strong>{divsLabels[key] || key}:</strong> {displayValue}
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
