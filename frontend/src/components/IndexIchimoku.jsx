import React, { useEffect, useState, useRef } from "react";
import { createChart } from "lightweight-charts";

const DataForChart = async ({ figi }) => {
  try {
    const response = await fetch(
      `http://localhost:8000/index_ichimoku/${figi}`
    );
    if (!response.ok) {
      throw new Error(
        `Error fetching data: ${response.status} ${response.statusText}`
      );
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
  };

  // const chartData = [
  //   { open: 10, high: 10.63, low: 9.49, close: 9.55, time: 1642427876 },
  //   { open: 9.55, high: 10.3, low: 9.42, close: 9.94, time: 1642514276 },
  //   { open: 9.94, high: 10.17, low: 9.92, close: 9.78, time: 1642600676 },
  //   { open: 9.78, high: 10.59, low: 9.18, close: 9.51, time: 1642687076 },
  //   { open: 9.51, high: 10.46, low: 9.1, close: 10.17, time: 1642773476 },
  //   { open: 10.17, high: 10.96, low: 10.16, close: 10.47, time: 1642859876 },
  //   { open: 10.47, high: 11.39, low: 10.4, close: 10.81, time: 1642946276 },
  //   { open: 10.81, high: 11.6, low: 10.3, close: 10.75, time: 1643032676 },
  //   { open: 10.75, high: 11.6, low: 10.49, close: 10.93, time: 1643119076 },
  //   { open: 10.93, high: 11.53, low: 10.76, close: 10.96, time: 1643205476 },
  // ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const rawData = await DataForChart({ figi });
        if (!rawData || !rawData.data) {
          return;
        }
        console.log("Raw data: ", rawData);

        let transformed = rawData.data.map((item) => ({
          time: Math.floor(new Date(item.time).getTime() / 1000), // Convert to UNIX timestamp in seconds
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
        }));
        transformed.sort((a, b) => a.time - b.time);
        console.log("Transformed data: ", transformed);

        const uniqueTransformed = transformed.filter(
          (item, index, self) =>
            index === self.findIndex((t) => t.time === item.time)
        );

        console.log(
          "Transformed Data After Removing Duplicates:",
          uniqueTransformed
        );

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

  useEffect(() => {
    const handleResize = () => {
      chart.applyOptions({ width: chartContainerRef.current.clientWidth });
    };

    const chart = createChart(chartContainerRef.current, chartOptions);
    chart.timeScale().fitContent();

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderVisible: false,
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
    });
    candlestickSeries.setData(chartData);

    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [chartOptions, chartData]);

  return (
    <div>
      <h2>Ichimoku Index for {figi}</h2>
      <div ref={chartContainerRef} />
    </div>
  );
};

export default IndexIchimoku;
