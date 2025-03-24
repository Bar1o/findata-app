import { React, useState, useEffect } from "react";
import { FetchData } from "./FetchData";

const InflationTable = ({ data = [] }) => {
  const sortedData = [...data].sort((a, b) => new Date(b.date) - new Date(a.date));

  return (
    <div className="text-sm p-1">
      <div className="bg-white overflow-hidden rounded-lg">
        <table className="w-full border-collapse">
          <thead className="bg-sky-100 text-sky-700">
            <tr>
              <th className="font-semibold p-2 text-center">Дата</th>
              <th className="font-semibold p-2 text-center">Ключевая ставка, % годовых</th>
              <th className="font-semibold p-2 text-center">Инфляция, % г/г</th>
              <th className="font-semibold p-2 text-center">Цель по инфляции, %</th>
            </tr>
          </thead>
          <tbody>
            {sortedData.map((item, index) => (
              <tr key={index}>
                <td className="p-2 text-center">{item.date}</td>
                <td className="p-2 text-center">{Number(item.keyRate).toFixed(2)}</td>
                <td className="p-2 text-center">{Number(item.infl).toFixed(2)}</td>
                <td className="p-2 text-center">{Number(item.targetInfl).toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const InflData = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const paperData = await FetchData("/api/inflation_table/");
        console.log("fetched inflation data", paperData);
        setData(paperData);
      } catch (error) {
        console.error("can't fetch inflation data:", error);
      }
    };
    fetchData();
  }, []);

  if (!data) {
    return <p>Загрузка данных...</p>;
  }

  return (
    <div>
      <h2>Ключевая ставка Банка России и инфляция</h2>
      <InflationTable data={data.inflTable || []} />
      <div className="w-full text-right text-sm text-gray-400 pb-1">Ставка ЦБ указана на последний день месяца</div>
    </div>
  );
};

export default InflData;
