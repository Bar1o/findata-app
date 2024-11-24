import React, { useEffect, useState, useRef } from "react";
import { createChart } from "lightweight-charts";

const DataForChart = async ({ figi }) => {
  try {
    const response = await fetch(`http://localhost:8000/index_ichimoku/${figi}`);
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

const IndexIchimoku = (props) => {
  const { figi } = props;

  const chartContainerRef = useRef(null);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
      try {
        const rawData = await DataForChart({ figi });
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

        setChartData(uniqueTransformed);
      } catch (err) {
        console.error("Data fetching error:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [figi]);

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
    const tenkanSenLineSeries = chart.addLineSeries({ color: "#FF1931" });
    tenkanSenLineSeries.setData(
      chartData
        .filter((item) => item.tenkanSen !== null)
        .map((item) => ({
          time: item.time,
          value: item.tenkanSen,
        }))
    );

    const kijunSenLineSeries = chart.addLineSeries({ color: "#2962FF" });
    kijunSenLineSeries.setData(
      chartData
        .filter((item) => item.kijunSen !== null)
        .map((item) => ({
          time: item.time,
          value: item.kijunSen,
        }))
    );

    const senkouSpanALineSeries = chart.addLineSeries({ color: "#FFEC28" });
    senkouSpanALineSeries.setData(
      chartData
        .filter((item) => item.senkouSpanA !== null)
        .map((item) => ({
          time: item.time,
          value: item.senkouSpanA,
        }))
    );

    const senkouSpanBLineSeries = chart.addLineSeries({ color: "#800080" });
    senkouSpanBLineSeries.setData(
      chartData
        .filter((item) => item.senkouSpanB !== null)
        .map((item) => ({
          time: item.time,
          value: item.senkouSpanB,
        }))
    );

    const chikouSpanLineSeries = chart.addLineSeries({ color: "#008001" }); // green
    chikouSpanLineSeries.setData(
      chartData
        .filter((item) => item.chikouSpan !== null)
        .map((item) => ({
          time: item.time,
          value: item.chikouSpan,
        }))
    );

    // const areaSeries = chart.addAreaSeries({
    //   lineColor: "#FFEC28",
    //   topColor: "rgba(255,257,255,0)",
    //   bottomColor: "rgba(0,100,80,0.2)",
    //   invertFilledArea: true,
    // });
    // areaSeries.setData(
    //   chartData
    //     .filter(
    //       (item) => item.senkouSpanA !== null && item.senkouSpanB !== null
    //     )
    //     .map((item) => ({
    //       time: item.time,
    //       value: item.senkouSpanA < item.senkouSpanB ? item.senkouSpanA : 0,
    //     }))
    // );

    ///////////////////////////////////////////////////////////////////////////////////////////

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

    const maxSenkouSpanB = Math.max(...chartData.map((item) => item.senkouSpanB));
    console.log("maxSenkouSpanB:", maxSenkouSpanB);

    if (maxSenkouSpanB !== -Infinity) {
      const baselineSeries = chart.addBaselineSeries({
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

      baselineSeries.setData(
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
        shape: "arrowforUp",
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
  }, [chartOptions, chartData]);

  return (
    <div>
      <h2>Ichimoku Index for {figi}</h2>
      <div>{loading && <p>Loading...</p>}</div>
      <div ref={chartContainerRef} />
    </div>
  );
};

export default IndexIchimoku;
