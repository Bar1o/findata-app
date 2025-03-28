import React, { useState, useEffect } from "react";
import { formatValueFixed, formatValue } from "../assets/formatFuncs";
import CustomLabel from "./CustomLabel";

// Поясняющий контейнер (можно оставить CustomLabel, который просто задает отступы и скругление, без логики цвета)
// const CustomLabel = ({ children, ...props }) => {
//   const baseClass = `w-full justify-center bg-gray-200/50 inline-flex items-center px-2 py-1 rounded-lg text-sm font-medium `;
//   return (
//     <div className={baseClass} {...props}>
//       {children}
//     </div>
//   );
// };

const SharePrice = ({ ticker }) => {
  const [quote, setQuote] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/share_price/${ticker}`);
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const data = await response.json();
        setQuote(data);
      } catch (error) {
        console.error("Error fetching share price:", error);
      }
    };

    fetchData();
    const intervalId = setInterval(fetchData, 5000);
    return () => clearInterval(intervalId);
  }, [ticker]);

  // Определяем класс для изменения котировки по знаку
  const getDeltaClass = (delta) => {
    if (delta > 0) return "text-green-600";
    if (delta < 0) return "text-red-500";
    return "text-gray-800";
  };

  return (
    <div className="pb-3">
      <CustomLabel className="w-full justify-center font-medium bg-slate-100 border border-slate-300">
        <span>
          {ticker} : {quote ? `${formatValueFixed(quote.price, 2)} ₽` : "Loading..."}
        </span>
        {quote && (
          <span className={`ml-2 px-2 py-1 rounded-full text-sm font-medium ${getDeltaClass(quote.abs_change)}`}>
            <div className="flex gap-2">
              <span>Δ {formatValueFixed(quote.abs_change, 2)}</span>
              <span> {formatValue(quote.percent_change, 2)}%</span>
            </div>
          </span>
        )}
      </CustomLabel>
    </div>
  );
};

export default SharePrice;
