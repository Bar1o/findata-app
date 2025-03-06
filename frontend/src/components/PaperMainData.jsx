import React, { useEffect, useState } from "react";
import { FetchPaperData } from "./FetchData";
import { paperMainLabels, issueKindMapping } from "../assets/paperData";
import { formatValue, formatDate } from "../assets/formatFuncs";

const PaperMainData = (props) => {
  const { ticker } = props;
  const [mainData, setMainData] = useState("");

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
    <div className="flex-col">
      <div className="font-medium w-full text-center p-1 bg-sky-100 text-sky-700 rounded-t-lg">Данные о бумаге</div>
      <div className="text-sm bg-white p-4 rounded-b-lg">
        {mainData && (
          <ul className="space-y-1">
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
                    <span className="font-semibold py-0.5 px-1 mr-1">{paperMainLabels[key] || key}:</span>
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

export default PaperMainData;
