import React from "react";
import { useState } from "react";

export const FetchDataByPeriod = async ({ figi, period }) => {
  // period is D, W, M, Y
  try {
    const response = await fetch(`/api/index_ichimoku/${figi}/${period}`);
    if (!response.ok) {
      throw new Error(`Error fetching data: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    console.log(data);
    return data;
  } catch (err) {
    console.error(err);
    throw err;
  }
};

export const IchimokuData = (rawData) => {
  try {
    if (!rawData || !rawData.data) {
      return;
    }
    console.log("Raw data: ", rawData.data);

    let transformedData = rawData.data.map((item) => ({
      time: item.time,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
      tenkanSen: item.tenkanSen,
      kijunSen: item.kijunSen,
      chikouSpan: item.chikouSpan,
      senkouSpanA: item.senkouSpanA,
      senkouSpanB: item.senkouSpanB,
    }));
    transformedData.sort((a, b) => a.time - b.time);
    console.log("Transformed data: ", transformedData);

    const uniqueTransformedData = transformedData.filter((item, index, self) => index === self.findIndex((t) => t.time === item.time));
    return uniqueTransformedData;
  } catch (err) {
    console.error("Data fetching error:", err);
  }
};
