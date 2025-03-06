import React, { useEffect, useState } from "react";
import { FetchPaperData } from "./FetchData";
import { sectorsLabels, companyNames } from "../assets/paperData";

const Sectors = (props) => {
  const { ticker, onTickerSelect } = props;
  const [mainData, setMainData] = useState(null);
  const [currentSector, setCurrentSector] = useState(null);
  const [sectorTickers, setSectorTickers] = useState([]);

  const handleTickerClick = (selectedTicker) => {
    // вызывает функцию из родительского компонента
    if (onTickerSelect) {
      onTickerSelect(selectedTicker);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const sectorsData = await FetchPaperData("/api/sectors/", "");
        console.log("fetched Sectors", sectorsData);
        setMainData(sectorsData.sectors);

        // сектор текущего тикера
        if (sectorsData.sectors) {
          for (const [sector, tickers] of Object.entries(sectorsData.sectors)) {
            if (tickers.includes(ticker)) {
              setCurrentSector(sector);
              // без текущего тикера
              setSectorTickers(tickers.filter((t) => t !== ticker));
              break;
            }
          }
        }
      } catch (error) {
        console.error("can't fetch Sectors data:", error);
      }
    };
    fetchData();
  }, [ticker]);

  if (!mainData || !currentSector) {
    return null;
  }

  return (
    <div className="flex-col">
      <div className="font-medium w-full text-center p-1 bg-sky-100 text-sky-700 rounded-t-lg">Сектор</div>
      <div className="text-sm w-full text-center p-0.5 bg-sky-50 text-gray-800">{sectorsLabels[currentSector] || currentSector}</div>
      <div className="text-sm bg-white p-4 rounded-b-lg">
        <div>
          <ul className="space-y-2">
            {sectorTickers.map((tickerItem) => (
              <li key={tickerItem} className="flex items-center">
                <button
                  onClick={() => handleTickerClick(tickerItem)}
                  className="bg-sky-50 hover:bg-sky-100 text-sky-700 text-xs font-medium py-0.5 px-2 rounded mr-2"
                >
                  {tickerItem}
                </button>
                <span className="text-gray-700">{companyNames[tickerItem] || ""}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Sectors;
