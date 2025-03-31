import React, { useEffect, useState, useRef } from "react";
import { createChart } from "lightweight-charts";
import { FetchKeyRate } from "./FetchData";
import PeriodButtons from "./PeriodButtons";

const KeyRateData = () => {
  const availablePeriods = ["M6", "Y", "Y5", "Y10", "Y15"];
  const [period, setPeriod] = useState("Y5");
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const res = await FetchKeyRate(period);
        const dataArray = Array.isArray(res.keyRate) ? res.keyRate : [res.keyRate];
        const transformed = dataArray.map((item) => {
          const dt = new Date(item.date);
          const year = dt.getFullYear();
          const month = String(dt.getMonth() + 1).padStart(2, "0");
          const day = String(dt.getDate()).padStart(2, "0");
          return { time: `${year}-${month}-${day}`, value: item.rate };
        });
        // данные надо сортировать по возрастанию времени
        transformed.sort((a, b) => new Date(a.time) - new Date(b.time));
        setChartData(transformed);
      } catch (error) {
        console.error(`Ошибка получения keyRate для периода ${period}:`, error);
        setChartData([]);
      }
      setLoading(false);
    };
    fetchData();
  }, [period]);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Удаляем предыдущий экземпляр графика, если он существует
    if (chartRef.current) {
      try {
        chartRef.current.remove();
      } catch (error) {
        if (!error.message.includes("Object is disposed")) {
          console.error("Ошибка при удалении предыдущего графика:", error);
        }
      }
      chartRef.current = null;
    }

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: {
        backgroundColor: "#ffffff",
        textColor: "#000000",
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
      rightPriceScale: {
        borderVisible: false,
      },
      watermark: {
        visible: false,
      },
    });
    chartRef.current = chart;

    const lineSeries = chart.addLineSeries({
      color: "#2962FF",
      lineWidth: 2,
    });

    if (chartData.length > 0) {
      lineSeries.setData(chartData);
      chart.timeScale().fitContent();
    }

    const handleResize = () => {
      chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      chart.timeScale().fitContent();
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      try {
        chart.remove();
      } catch (error) {
        if (!error.message.includes("Object is disposed")) {
          console.error("Ошибка при удалении графика при размонтировании:", error);
        }
      }
    };
  }, [chartData, period]);

  return (
    <div className="w-full">
      <h2 className="font-bold text-xl mb-4 mt-2">График ключевой ставки</h2>
      <div ref={chartContainerRef} className="relative border border-gray-300 mb-5" />
      <PeriodButtons period={period} setPeriod={setPeriod} periods={availablePeriods} />
    </div>
  );
};

export default KeyRateData;
