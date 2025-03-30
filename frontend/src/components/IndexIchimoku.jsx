import React, { useEffect, useState, useRef } from "react";
import { createChart } from "lightweight-charts";
import { FetchDataByPeriod, IchimokuData } from "./FetchData";

const IndexIchimoku = ({ ticker, period, showLines }) => {
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

  const indicatorMapping = {
    tenkanSen: { color: "black", priceScaleId: "left" },
    kijunSen: { color: "#FF8A0C", priceScaleId: "left" },
    senkouSpanA: { color: "limegreen", priceScaleId: "left" },
    senkouSpanB: { color: "#1876D2", priceScaleId: "left" },
    chikouSpan: { color: "#FF73DE", priceScaleId: "left" },
  };

  const indicatorNames = {
    tenkanSen: "Tenkan-sen",
    kijunSen: "Kijun-sen",
    senkouSpanA: "Senkou Span A",
    senkouSpanB: "Senkou Span B",
    chikouSpan: "Chikou Span",
  };

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

    let legendDiv;
    if (showLines) {
      const plotIndexes = (color, dataKey) => {
        const lineSeries = chart.addLineSeries({ color, lineWidth: 2 });
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

      Object.keys(indicatorMapping).forEach((indicatorKey) => {
        plotIndexes(indicatorMapping[indicatorKey].color, indicatorKey);
      });

      // Пример отрисовки облака и маркеров (оставляем логику без изменений)
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

      const Legend = () => (
        <div
          style={{
            position: "absolute",
            left: "50%",
            bottom: "10px",
            transform: "translateX(-50%)",
            zIndex: 2,
            fontSize: "12px",
            fontFamily: "sans-serif",
            lineHeight: "18px",
            fontWeight: "bold",
            backgroundColor: "rgba(255, 255, 255, 0.8)",
            padding: "8px",
            borderRadius: "4px",
            border: "1px solid #d1d4dc",
            display: "flex",
            gap: "15px",
          }}
        >
          {Object.keys(indicatorMapping).map((indicatorKey, index) => (
            <div key={index} style={{ display: "flex", alignItems: "center" }}>
              <span
                style={{
                  display: "inline-block",
                  marginRight: "4px",
                  width: "10px",
                  height: "3px",
                  backgroundColor: indicatorMapping[indicatorKey].color,
                  verticalAlign: "middle",
                  borderTop: `1px dashed ${indicatorMapping[indicatorKey].color}`,
                }}
              ></span>
              <span style={{ color: indicatorMapping[indicatorKey].color }}>{indicatorNames[indicatorKey]}</span>
            </div>
          ))}
        </div>
      );

      legendDiv = document.createElement("div");
      chartContainerRef.current.appendChild(legendDiv);
      import("react-dom").then((ReactDOM) => {
        ReactDOM.render(<Legend />, legendDiv);
      });
    }

    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      if (legendDiv && chartContainerRef.current && chartContainerRef.current.contains(legendDiv)) {
        import("react-dom").then((ReactDOM) => {
          ReactDOM.unmountComponentAtNode(legendDiv);
        });
        chartContainerRef.current.removeChild(legendDiv);
      }
      chart.remove();
    };
  }, [chartData, showLines]);

  return (
    <div>
      <h2 className="text-xl font-medium text-gray-800 mb-4">Индикатор Ишимоку для {ticker}</h2>
      <div>{loading && <p>Загрузка...</p>}</div>
      <div ref={chartContainerRef} style={{ position: "relative" }} />
    </div>
  );
};

export default IndexIchimoku;
