import React, { useEffect, useState, useRef } from "react";
import { createChart } from "lightweight-charts";
import { FetchDataByPeriod, IchimokuData } from "./FetchData";

const IndexIchimoku2 = ({ ticker, period, showLines }) => {
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
      timeVisible: true,
      secondsVisible: false,
      barSpacing: 30,
      minBarSpacing: 10,
      rightOffset: 10,
      barSpacingIncrement: 5,
    },
  };

  // Fetch data when ticker or period changes
  useEffect(() => {
    const fetchData = async () => {
      try {
        const rawData = await FetchDataByPeriod({ ticker, period });
        const ichimokuData = IchimokuData(rawData);
        setChartData(ichimokuData);
      } catch (error) {
        console.error(`Error fetching data for period "${period}":`, error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [ticker, period]);

  // Draw chart whenever chartData or showLines changes
  useEffect(() => {
    if (!chartContainerRef.current) return;
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

    if (showLines) {
      // Helper function for index lines
      const plotIndexes = (color, dataKey) => {
        const lineSeries = chart.addLineSeries({ color });
        lineSeries.setData(
          chartData
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

      // Пример отрисовки облака и маркеров (с сохранением предыдущей логики)
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

      // Markers for buy and sell signals
      const buySignals = [];
      const sellSignals = [];
      for (let i = 1; i < chartData.length; i++) {
        if (chartData[i].tenkanSen > chartData[i].kijunSen && chartData[i - 1].tenkanSen <= chartData[i - 1].kijunSen) {
          buySignals.push({ time: chartData[i].time, value: chartData[i].min });
        }
        if (chartData[i].tenkanSen < chartData[i].kijunSen && chartData[i - 1].tenkanSen >= chartData[i - 1].kijunSen) {
          sellSignals.push({ time: chartData[i].time, value: chartData[i].max });
        }
      }
      console.log("Buy signals:", buySignals);
      console.log("Sell signals:", sellSignals);

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
    }

    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [chartData, showLines]);

  return (
    <div>
      <h2 className="text-xl font-medium text-gray-800 mb-4">Индекс Ишимоку для {ticker}</h2>
      <div>{loading && <p>Загрузка...</p>}</div>
      <div ref={chartContainerRef} style={{ position: "relative" }} />
    </div>
  );
};

export default IndexIchimoku2;
