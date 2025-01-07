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

    // // Add whitespace data from 20:00 to 23:00 and from 00:00 to 03:00
    // const dataWithWhitespace = [];
    // let prevHour = -1;
    // uniqueTransformed.forEach((item) => {
    //   dataWithWhitespace.push(item);
    //   const date = new Date(item.time * 1000);
    //   const hour = date.getHours();

    //   if (hour === 20) {
    //     for (let h = 21; h <= 23; ++h) {
    //       const whitespaceDate = new Date(date);
    //       whitespaceDate.setHours(h, 0, 0, 0);
    //       const whitespaceTime = Math.floor(whitespaceDate.getTime() / 1000);
    //       dataWithWhitespace.push({ time: whitespaceTime });
    //     }
    //     for (let h = 0; h <= 3; ++h) {
    //       const whitespaceDate = new Date(date);
    //       whitespaceDate.setDate(whitespaceDate.getDate() + 1);
    //       whitespaceDate.setHours(h, 0, 0, 0);
    //       const whitespaceTime = Math.floor(whitespaceDate.getTime() / 1000);
    //       dataWithWhitespace.push({ time: whitespaceTime });
    //     }
    //   }
    // });
    // console.log("Transformed Data After Adding Whitespace:", dataWithWhitespace);
    // const dataWithWhitespaceFiltered = dataWithWhitespace.filter(
    //   (item, index, self) => index === self.findIndex((t) => t.time === item.time)
    // );
    // return dataWithWhitespaceFiltered;
  } catch (err) {
    console.error("Data fetching error:", err);
  }
};
