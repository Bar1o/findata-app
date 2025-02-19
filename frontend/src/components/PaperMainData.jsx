import React, { useEffect, useState } from "react";
import { FetchPaperData } from "./FetchData";
import { paperMainLabels, issueKindMapping } from "../assets/paperData";

const PaperMainData = (props) => {
  const { ticker } = props;
  const [mainData, setMainData] = useState("");

  const formatValue = (value) => {
    if (typeof value === "number") {
      return new Intl.NumberFormat("ru-RU").format(value);
    }
    return value;
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();
    return `${day}.${month}.${year}`;
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const paperData = await FetchPaperData("/api/paper_main_data/", ticker);
        console.log("fetched PaperMainData", paperData);
        setMainData(paperData.mainData);
      } catch (error) {
        console.error("can't fetch main paper data:", error);
      }
    };
    fetchData();
  }, [ticker]);

  return (
    <div className="flex-col hover:bg-sky-500 ">
      <div className="w-full text-center p-1 bg-sky-100 text-sky-700 rounded-t-lg">Данные о бумаге</div>
      <div className="bg-white p-2 rounded-b-lg">
        {mainData && (
          <ul>
            {Object.keys(mainData)
              .filter((key) => mainData[key])
              .map((key) => {
                let displayValue = formatValue(mainData[key]);
                if (key === "issue_kind") {
                  displayValue = issueKindMapping[mainData[key]] || mainData[key];
                } else if (["placement_date", "ipo_date", "registry_date"].includes(key)) {
                  displayValue = formatDate(mainData[key]);
                }
                return (
                  <li key={key}>
                    <strong>{paperMainLabels[key] || key}:</strong> {displayValue}
                  </li>
                );
              })}
          </ul>
        )}
      </div>
    </div>
  );
};

export default PaperMainData;
