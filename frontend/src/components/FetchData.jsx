import React from "react";
import { useState } from "react";

export const FetchDataByPeriod = async ({ figi, period }) => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "";
  // period is D, W, M, Y
  try {
    // const response = await fetch(`http://localhost:3300/index_ichimoku/${figi}/${period}`);
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

export const TransformData = (rawData) => {
  try {
    if (!rawData || !rawData.data) {
      return;
    }
    console.log("Raw data: ", rawData);

    let transformed = rawData.data.map((item) => ({
      time: Math.floor(new Date(item.time + "Z").getTime() / 1000),
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
    transformed.sort((a, b) => a.time - b.time);
    console.log("Transformed data: ", transformed);

    const uniqueTransformed = transformed.filter((item, index, self) => index === self.findIndex((t) => t.time === item.time));

    console.log("Transformed Data After Removing Duplicates:", uniqueTransformed);
    return uniqueTransformed;
  } catch (err) {
    console.error("Data fetching error:", err);
  }
};
