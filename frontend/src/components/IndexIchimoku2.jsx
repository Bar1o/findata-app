import React, { useEffect, useState, useRef } from "react";
import { createChart } from "lightweight-charts";
import { FetchDataByPeriod, IchimokuData } from "./FetchData";

const IndexIchimoku2 = ({ figi, data }) => {
  const chartContainerRef = useRef(null);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  const chartOptions = {
    layout: {
      textColor: "black",
      background: { type: "solid", color: "white" },
    },
    height: 400,
    timeScale: {
      timeVisible: true, // Enables time labels on the x-axis
      secondsVisible: false, // Hides seconds in the labels
      barSpacing: 30, // Adjust spacing to prevent label overlap
      minBarSpacing: 10,
      rightOffset: 10,
      barSpacingIncrement: 5, // Smooth resizing
    },
    series: {
      type: "Candlestick",
      data: chartData,
      spanGaps: false,
    },
  };

  ///////////////////////////////////////////////////////////////////////////////////////////

  useEffect(() => {
    const fetchData = async () => {
      if (!data || data.length === 0) {
        const defaultPeriod = "D";
        try {
          const rawData = await FetchDataByPeriod({ figi, period: defaultPeriod });
          const transformedData = IchimokuData(rawData);
          setChartData(transformedData);
        } catch (error) {
          console.error(`Error fetching data for period "${defaultPeriod}":`, error);
        } finally {
          setLoading(false);
        }
      } else {
        setChartData(data);
        setLoading(false);
      }
    };
    fetchData();
  }, [data, figi]);

  ///////////////////////////////////////////////////////////////////////////////////////////

  useEffect(() => {
    const handleResize = () => {
      chart.applyOptions({ width: chartContainerRef.current.clientWidth });
    };

    const chart = createChart(chartContainerRef.current, chartOptions);
    chart.timeScale().fitContent();

    // upColor: "#26a69a",
    // downColor: "#ef5350",

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderVisible: false,
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
    });
    candlestickSeries.setData(chartData);

    // Lines for indexes
    const plotIndexes = (color, dataKey) => {
      const lineSeries = chart.addLineSeries({ color });
      lineSeries.setData(
        data
          .filter((item) => item[dataKey] !== null)
          .map((item) => ({
            time: item.time,
            value: item[dataKey],
          }))
      );
      return lineSeries;
    };

    plotIndexes("#FF1931", "tenkanSen");
    plotIndexes("#2962FF", "kijunSen");
    plotIndexes("#FFEC28", "senkouSpanA");
    plotIndexes("#800080", "senkouSpanB");
    plotIndexes("#008001", "chikouSpan");

    ///////////////////////////////////////////////////////////////////////////////////////////

    // CloudArea

    const colorsSet = {
      yellow: "#FFEC28",
      orange: "#FFA500",
      teal: "#26A6996C",
      tealLight: "#21A49700",
      orangeRed: "#EF535040",
      orangeRedLight: "#EF535000",
      green: "#00645047",
      purple: "#800080",
    };

    const maxSenkouSpanB = Math.max(
      ...chartData.map((item) => {
        const val = parseFloat(item.senkouSpanB);
        return Number.isFinite(val) ? val : 0;
      })
    );
    console.log("maxSenkouSpanB:", maxSenkouSpanB);

    if (maxSenkouSpanB !== -Infinity) {
      const cloudArea = chart.addBaselineSeries({
        baseValue: {
          type: "price",
          price: maxSenkouSpanB,
        },
        topLineColor: colorsSet.purple,
        topFillColor1: colorsSet.orangeRed,
        topFillColor2: colorsSet.orangeRedLight,
        bottomLineColor: colorsSet.yellow,
        bottomFillColor1: colorsSet.orangeRedLight,
        bottomFillColor2: colorsSet.orangeRed,
        lineVisible: false,
      });

      cloudArea.setData(
        chartData
          .filter((item) => item.senkouSpanA !== null && item.senkouSpanB !== null)
          .map((item) => ({
            time: item.time,
            value: item.senkouSpanA < item.senkouSpanB ? item.senkouSpanA : item.senkouSpanB,
          }))
      );
    }

    ///////////////////////////////////////////////////////////////////////////////////////////

    const buySignals = [];
    const sellSignals = [];

    for (let i = 1; i < chartData.length; ++i) {
      if (chartData[i].tenkanSen > chartData[i].kijunSen && chartData[i - 1].tenkanSen <= chartData[i - 1].kijunSen) {
        buySignals.push({ time: chartData[i].time, value: chartData[i].min });
      }
      if (chartData[i].tenkanSen < chartData[i].kijunSen && chartData[i - 1].tenkanSen >= chartData[i - 1].kijunSen) {
        sellSignals.push({ time: chartData[i].time, value: chartData[i].max });
      }
    }

    let markers = [];

    buySignals.forEach((signal) => {
      markers.push({
        time: signal.time,
        position: "belowBar",
        color: "green",
        shape: "arrowUp",
        size: 2,
        text: "Buy",
      });
    });

    sellSignals.forEach((signal) => {
      markers.push({
        time: signal.time,
        position: "aboveBar",
        color: "red",
        shape: "arrowDown",
        size: 2,
        text: "Sell",
      });
    });

    markers.sort((a, b) => a.time - b.time);

    candlestickSeries.setMarkers(markers);
    ///////////////////////////////////////////////////////////////////////////////////////////

    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [chartData]);

  return (
    <div>
      <h2>Ichimoku Index for {figi}</h2>
      <div>{loading && <p>Loading...</p>}</div>
      <div ref={chartContainerRef} />
    </div>
  );
};

export default IndexIchimoku2;
