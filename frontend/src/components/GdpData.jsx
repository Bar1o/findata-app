import React, { useEffect, useRef, useState } from "react";
import { createChart } from "lightweight-charts";
import { FetchData } from "./FetchData";

const GdpData = () => {
  const chartContainerRef = useRef(null);
  const [data, setData] = useState(null);

  const seriesConfig = {
    gdp: {
      label: "ВВП, млрд руб",
      color: "#1976d2",
      priceScaleId: "left",
    },
    imoex: {
      label: "IMOEX, пункты",
      color: "black",
      priceScaleId: "right",
    },
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const paperData = await FetchData("/api/gdp/");
        setData(paperData);
      } catch (error) {
        console.error("can't fetch gdp imoex data:", error);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    if (!data || !chartContainerRef.current) return;
    const newChart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: {
        backgroundColor: "#ffffff",
        textColor: "#000000",
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
        barSpacing: 50,
      },
      grid: {
        vertLines: { color: "#e1e3e6" },
        horzLines: { color: "#e1e3e6" },
      },
      rightPriceScale: {
        visible: true,
        borderVisible: true,
        borderColor: seriesConfig.imoex.color,
      },
      leftPriceScale: {
        visible: true,
        borderVisible: true,
        borderColor: seriesConfig.gdp.color,
      },
    });

    const gdpSeries = newChart.addLineSeries({
      color: seriesConfig.gdp.color,
      lineWidth: 2,
      priceScaleId: seriesConfig.gdp.priceScaleId,
      lastValueVisible: true,
    });

    const imoexSeries = newChart.addLineSeries({
      color: seriesConfig.imoex.color,
      lineWidth: 2,
      priceScaleId: seriesConfig.imoex.priceScaleId,
      lastValueVisible: true,
    });

    const gdpData = data.gdp.map((item) => ({
      time: `${item.year}-01-01`,
      value: item.value,
    }));
    const imoexData = data.imoex.map((item) => ({
      time: `${item.year}-01-01`,
      value: item.close,
    }));

    gdpSeries.setData(gdpData);
    imoexSeries.setData(imoexData);
    newChart.timeScale().fitContent();

    const handleResize = () => {
      newChart.applyOptions({ width: chartContainerRef.current.clientWidth });
      newChart.timeScale().fitContent();
    };
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      newChart.remove();
    };
  }, [data]);

  return (
    <div style={{ position: "relative" }}>
      <h2 className="text-xl font-bold text-gray-800 my-4">Сравнение ВВП и индекса Мосбиржи</h2>
      {!data ? <p>Загрузка данных...</p> : <div ref={chartContainerRef} className="relative w-full" />}
    </div>
  );
};

export default GdpData;
