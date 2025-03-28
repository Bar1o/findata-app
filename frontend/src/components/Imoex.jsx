import React, { useState, useEffect } from "react";
import { formatValueFixed, formatValue } from "../assets/formatFuncs";

import CustomLabel from "./CustomLabel";

const Imoex = () => {
  const [quote, setQuote] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("/api/imoex_change/");
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const data = await response.json();
        setQuote(data);
      } catch (error) {
        console.error("Error fetching IMOEX quote:", error);
      }
    };

    const interval = 5000; // polling interval
    fetchData();
    const intervalId = setInterval(fetchData, interval);
    return () => clearInterval(intervalId);
  }, []);

  const getDeltaClass = (delta) => {
    if (delta > 0) return "text-green-600";
    if (delta < 0) return "text-red-500";
    return "text-gray-800";
  };

  return (
    <div>
      <CustomLabel theme="clear" className="border-red-300">
        <span>IMOEX : {quote ? `${formatValueFixed(quote.price, 2)}` : "Loading..."}</span>
        {quote && (
          <span className={`ml-2 text-sm ${getDeltaClass(quote.abs_change)}`}>
            <div className="flex gap-2">
              <span>Δ {formatValueFixed(quote.abs_change, 2)}</span>
              <span>{formatValue(quote.percent_change, 2)}%</span>
            </div>
          </span>
        )}
      </CustomLabel>
    </div>
  );
};

export default Imoex;
