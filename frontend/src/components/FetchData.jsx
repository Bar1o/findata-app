import React from "react";
import { useState } from "react";

export const FetchDataByPeriod = async ({ ticker, period }) => {
  // period is D, W, M, Y
  try {
    const response = await fetch(`/api/index_ichimoku/${ticker}/${period}`);
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

export const FetchKeyRate = async (period) => {
  try {
    const response = await fetch(`/api/key_rate/${period}`);
    if (!response.ok) {
      throw new Error(`Error fetching data: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    console.log("key rate", data);
    return data;
  } catch (err) {
    console.error(err);
    throw err;
  }
};

export const FetchPaperData = async (path, ticker) => {
  try {
    const response = await fetch(`${path}${ticker}`);
    console.log(`${path}${ticker}`);
    if (!response.ok) {
      throw new Error(`Error fetching data: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    console.log("main data", data);
    return data;
  } catch (err) {
    console.error(err);
    throw err;
  }
};

export const FetchData = async (path) => {
  try {
    const response = await fetch(`${path}`);
    console.log(`${path}`);
    if (!response.ok) {
      throw new Error(`Error fetching data: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    console.log("the data fetched", data);
    return data;
  } catch (err) {
    console.error(err);
    throw err;
  }
};
