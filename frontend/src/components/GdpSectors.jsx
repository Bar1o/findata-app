import React, { useEffect, useRef, useState } from "react";
import { createChart } from "lightweight-charts";
import { FetchData } from "./FetchData";

const GdpSectors = () => {
  const chartContainerRef = useRef(null);
  const [data, setData] = useState(null);

  // Конфигурация для всех секторов
  const sectorsConfig = {
    oil: {
      label: "Нефтегаз",
      color: "black",
      priceScaleId: "left",
    },
    build: {
      label: "Строительство",
      color: "#FF8A0C",
      priceScaleId: "left",
    },
    banks: {
      label: "Банки",
      color: "limegreen",
      priceScaleId: "left",
    },
    retail: {
      label: "Ретейл",
      color: "#1876D2",
      priceScaleId: "left",
    },
    tech: {
      label: "Технологии",
      color: "#FF73DE",
      priceScaleId: "left",
    },
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Ожидается, что API вернет данные в формате:
        // {
        //    "oil": [{ "year": 2013, "value": ...}, ...],
        //    "build": [{ "year": 2013, "value": ...}, ...],
        //    "banks": [{ "year": 2013, "value": ...}, ...],
        //    "retail": [{ "year": 2013, "value": ...}, ...],
        //    "tech": [{ "year": 2013, "value": ...}, ...],
        // }
        const sectorsData = await FetchData("/api/gdp_sectors/");
        console.log("fetched GdpSectors", sectorsData);
        setData(sectorsData);
      } catch (error) {
        console.error("can't fetch gdp sectors data:", error);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    if (!data || !chartContainerRef.current) return;

    console.log("Building sectors chart with data:", data);

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
      // Общая левая ось для всех секторов
      leftPriceScale: {
        visible: true,
        borderVisible: true,
        borderColor: "#ccc",
      },
    });

    // Создаем серию для каждого сектора
    Object.keys(sectorsConfig).forEach((sectorKey) => {
      const seriesOptions = {
        color: sectorsConfig[sectorKey].color,
        lineWidth: 2,
        priceScaleId: sectorsConfig[sectorKey].priceScaleId,
        lastValueVisible: true,
        crosshairMarkerVisible: true,
        crosshairMarkerRadius: 6,
        lineStyle: 0,
        pointMarkersVisible: true,
        pointMarkersRadius: 5,
      };

      const sectorSeries = newChart.addLineSeries(seriesOptions);

      // Преобразуем год в формат "YYYY-01-01"
      const sectorData = data[sectorKey].map((item) => ({
        time: `${item.year}-01-01`,
        value: item.value,
      }));

      console.log(`${sectorKey} data:`, sectorData);
      sectorSeries.setData(sectorData);
    });

    newChart.priceScale("left").applyOptions({
      autoScale: true,
      scaleMargins: { top: 0.1, bottom: 0.1 },
      priceFormat: {
        type: "custom",
        formatter: (price) => price.toLocaleString("ru-RU"),
      },
    });

    newChart.timeScale().fitContent();

    // Компонент легенды, позиционируемый по центру вверху графика
    const Legend = () => (
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "10px",
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
        {Object.values(sectorsConfig).map((item, index) => (
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

    // Добавляем легенду через React Portal
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
      <h2 className="text-xl font-bold text-gray-800 mb-4">Динамика отраслей ВВП (в % к предыдущему году)</h2>
      {!data ? <p>Загрузка данных...</p> : <div ref={chartContainerRef} style={{ position: "relative", width: "100%" }} />}
    </div>
  );
};

export default GdpSectors;
