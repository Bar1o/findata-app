import React, { useState, useEffect } from "react";
import CustomLabel from "./CustomLabel";
import { FetchData } from "./FetchData";
import { formatValueFixed } from "../assets/formatFuncs";

export const Currency = ({ label, value }) => {
  return (
    <CustomLabel theme="clear" className="border-stone-300">
      {label}/RUB: {value !== undefined ? formatValueFixed(value, 2) : "Загрузка..."}
    </CustomLabel>
  );
};

const CurrencyBar = () => {
  const [data, setData] = useState(null);

  const defaultCurrencies = ["USD", "EUR", "CNY"];

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

  // Если данные имеются, используем их ключи, иначе список по умолчанию
  const currencyKeys = data ? Object.keys(data) : defaultCurrencies;

  return (
    <div className="flex flex-row gap-2">
      {currencyKeys.map((currency) => (
        <div key={currency}>
          <Currency label={currency} value={data ? data[currency] : undefined} />
        </div>
      ))}
    </div>
  );
};

export default CurrencyBar;
