import React, { useState, useEffect } from "react";
import CustomLabel from "./CustomLabel";
import { FetchData } from "./FetchData";
import { formatValueFixed } from "../assets/formatFuncs";

export const Currency = ({ label, value }) => {
  return (
    <CustomLabel theme="clear" className="border-stone-300">
      {label}/RUB: {formatValueFixed(value, 2)}
    </CustomLabel>
  );
};

const CurrencyBar = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchDataFn = async () => {
      try {
        const currencyData = await FetchData("/api/currency/");
        console.log("fetched Currency", currencyData);
        setData(currencyData);
      } catch (error) {
        console.error("can't fetch currency data:", error);
      }
    };
    fetchDataFn();
  }, []);

  if (!data) return <div>Загрузка...</div>;

  return (
    <div className="flex flex-row gap-2">
      {Object.entries(data).map(([currency, value]) => (
        <div key={currency}>
          <Currency key={currency} label={currency} value={value} />
        </div>
      ))}
    </div>
  );
};

export default CurrencyBar;
