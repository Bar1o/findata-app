import React, { useState } from "react";
import CustomLabel from "./CustomLabel";
import { Switch } from "@gravity-ui/uikit";

const AllTickers = ({ tickerList, onSelectTicker, isPaused }) => {
  // Дублируем список для бесшовного эффекта
  const repeatedTickers = [...tickerList, ...tickerList];

  return (
    <div className="mb-2">
      <div className="overflow-hidden pb-2">
        <div
          className="items-center whitespace-nowrap inline-block bg-gradient-to-r from-blue-500 via-blue-300 to-blue-500"
          style={{
            animation: isPaused ? "none" : "marquee 30s linear infinite",
          }}
        >
          {repeatedTickers.map((ticker, index) => (
            <React.Fragment key={`${ticker}-${index}`}>
              <span className="cursor-pointer text-white text-lg select-none px-3" onClick={() => onSelectTicker && onSelectTicker(ticker)}>
                {ticker}
              </span>
              {index < repeatedTickers.length - 1 && <span className="text-white mx-2 select-none">•</span>}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AllTickers;
