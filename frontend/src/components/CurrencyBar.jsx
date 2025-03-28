import React, { useState, useEffect } from "react";
import { Label } from "@gravity-ui/uikit";
import { FetchData } from "./FetchData";
import { formatValueFixed } from "../assets/formatFuncs";

export const Currency = ({ label, value }) => {
  return (
    <Label title="курс ЦБ" className="px-1 py-2 rounded-lg cursor-pointer" theme="info" size="xs" value={formatValueFixed(value, 2)}>
      {label}/RUB
    </Label>
  );
};

const CurrencyBar = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const currencyData = await FetchData("/api/currency/");
        console.log("fetched Currency", currencyData);
        setData(currencyData);
      } catch (error) {
        console.error("can't fetch currency data:", error);
      }
    };
    fetchData();
  }, []);

  if (!data) return <div>Загрузка...</div>;

  return (
    <div className="flex flex-row gap-2 flex-wrap">
      {Object.entries(data).map(([currency, value]) => (
        <Currency key={currency} label={currency} value={value} />
      ))}
    </div>
  );
};

export default CurrencyBar;
