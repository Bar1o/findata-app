import React, { useEffect, useState } from "react";
import { FetchPaperData } from "./FetchData";
import { paperMainLabels, issueKindMapping } from "../assets/paperData";
import { formatValue, formatDate } from "../assets/formatFuncs";

const PaperMainData = ({ ticker }) => {
  const [mainData, setMainData] = useState(null); // Данные ещё не загружены

  useEffect(() => {
    // Сбрасываем данные при изменении тикера
    setMainData(null);
    const fetchData = async () => {
      try {
        const paperData = await FetchPaperData("/api/paper_main_data/", ticker);
        console.log("fetched PaperMainData", paperData);
        setMainData(paperData.mainData);
      } catch (error) {
        console.error("Can't fetch main paper data:", error);
        setMainData({}); // Можно оставить null, если данные не пришли
      }
    };
    fetchData();
  }, [ticker]);

  // Если данных ещё нет – показываем индикатор загрузки
  if (mainData === null) {
    return (
      <div className="flex-col">
        <div className="font-medium w-full text-center p-1 bg-sky-100 text-sky-700 rounded-t-lg">Данные о бумаге</div>
        <div className="text-sm bg-white p-4 rounded-b-lg flex justify-center items-center">
          <span className="text-slate-500">Загрузка...</span>
        </div>
      </div>
    );
  }

  // Если данные пусты – не отображаем компонент
  if (!mainData || Object.keys(mainData).length === 0) return null;

  // Список ключей для обработки дат
  const dateKeys = ["placement_date", "ipo_date", "registry_date"];

  // Фильтруем ключи, чтобы для дат, если формат равен "01.01.1970" — не отображать
  const keysToDisplay = Object.keys(mainData).filter((key) => {
    if (dateKeys.includes(key)) {
      // Если значение существует — форматируем его и сравниваем с "01.01.1970"
      return mainData[key] && formatDate(mainData[key]) !== "01.01.1970";
    }
    return mainData[key];
  });

  return (
    <div className="flex-col">
      <div className="font-medium w-full text-center p-1 bg-sky-100 text-sky-700 rounded-t-lg">Данные о бумаге</div>
      <div className="text-sm bg-white p-4 rounded-b-lg">
        <ul className="space-y-1">
          {keysToDisplay.map((key) => {
            let displayValue = formatValue(mainData[key]);
            if (key === "issue_kind") {
              displayValue = issueKindMapping[mainData[key]] || mainData[key];
            } else if (dateKeys.includes(key)) {
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
      </div>
    </div>
  );
};

export default PaperMainData;
