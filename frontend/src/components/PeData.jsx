import React, { useEffect, useState } from "react";
import { FetchPaperData } from "./FetchData";

const PeData = ({ ticker }) => {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const paperData = await FetchPaperData("/api/pe/", ticker);
        setData(paperData);
      } catch (error) {
        console.error("Can't fetch p/e data:", error);
      }
    };
    fetchData();
  }, [ticker]);

  const getChangeColor = (value) => {
    if (value > 0) return "text-green-600";
    if (value < 0) return "text-red-600";
    return "text-gray-800";
  };

  if (!data) {
    return <div className="text-center">Загрузка...</div>;
  }

  const years = data.ticker.year;

  return (
    <div className="w-full pt-3">
      <div className="overflow-x-auto rounded-lg">
        <table className="min-w-full bg-white">
          <thead className="bg-sky-100 text-sky-700">
            <tr>
              <th className="px-4 py-2 text-left text-sm font-semibold ">Год</th>
              <th className="px-4 py-2 text-left text-sm font-semibold ">P/E компании</th>
              <th className="px-4 py-2 text-left text-sm font-semibold ">Изменение за год</th>
              <th className="px-4 py-2 text-left text-sm font-semibold ">P/E сектора</th>
              <th className="px-4 py-2 text-left text-sm font-semibold ">Изменение сектора</th>
            </tr>
          </thead>
          <tbody>
            {years.map((year, i) => (
              <tr key={year} className="border-t border-gray-200 hover:bg-gray-50">
                <td className="px-4 py-2 text-gray-800">{year}</td>
                <td className="px-4 py-2 text-gray-800">{data.ticker.p_e[i]}</td>
                <td className={`px-4 py-2 font-medium ${getChangeColor(data.ticker.year_change[i])}`}>
                  {data.ticker.year_change[i] > 0 ? "+" : ""}
                  {data.ticker.year_change[i]}
                </td>
                <td className="px-4 py-2 text-gray-800">{data.mean.p_e[i]}</td>
                <td className={`px-4 py-2 font-medium ${getChangeColor(data.mean.year_change[i])}`}>
                  {data.mean.year_change[i] > 0 ? "+" : ""}
                  {data.mean.year_change[i]}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PeData;
