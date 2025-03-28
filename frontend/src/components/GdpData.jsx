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

    // Добавление легенды внизу графика
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
        {Object.values(seriesConfig).map((item, index) => (
          <div key={index} style={{ display: "flex", alignItems: "center" }}>
            <span
              style={{
                display: "inline-block",
                marginRight: "4px",
                width: "10px",
                height: "3px",
                backgroundColor: item.color,
                verticalAlign: "middle",
                borderTop: item.priceScaleId === "left" ? `1px dashed ${item.color}` : "none",
              }}
            ></span>
            <span style={{ color: item.color }}>{item.label}</span>
          </div>
        ))}
      </div>
    );

    const legendDiv = document.createElement("div");
    chartContainerRef.current.appendChild(legendDiv);
    import("react-dom").then((ReactDOM) => {
      ReactDOM.render(<Legend />, legendDiv);
    });

    const handleResize = () => {
      newChart.applyOptions({ width: chartContainerRef.current.clientWidth });
      newChart.timeScale().fitContent();
    };
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      if (chartContainerRef.current && chartContainerRef.current.contains(legendDiv)) {
        import("react-dom").then((ReactDOM) => {
          ReactDOM.unmountComponentAtNode(legendDiv);
        });
        chartContainerRef.current.removeChild(legendDiv);
      }
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
