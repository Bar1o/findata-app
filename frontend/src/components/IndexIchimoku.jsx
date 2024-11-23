import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ResponsiveContainer,
  Area,
  Scatter,
} from "recharts";

const IndexIchimoku = (props) => {
  const { figi } = props;
  const [candles, setCandles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCandles = async () => {
      setLoading(true);
      setError(null);
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

        setCandles(data.data);
      } catch (err) {
        console.error(err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchCandles();
  }, [figi]);

  if (loading) {
    return <div>Loading...</div>;
  }
  if (error) {
    return <div>Error: {error}</div>;
  }

  const formattedData = candles.map((candle) => ({
    ...candle,
    Time: new Date(candle.Time).toLocaleString(),
    Tenkan_sen: candle["Tenkan-sen"],
    Kijun_sen: candle["Kijun-sen"],
    Senkou_Span_A: candle["Senkou Span A"],
    Senkou_Span_B: candle["Senkou Span B"],
    Chikou_Span: candle["Chikou Span"],
    // Additional fields for candlestick emulation
    Max: candle["Max"],
    Min: candle["Min"],
    Open: candle["Open"],
    Close: candle["Close"],
  }));
  console.log("Formatted Data for Recharts:", formattedData);

  return (
    <div>
      <h2>Ichimoku Index for {figi}</h2>
      <ResponsiveContainer width="100%" height={500}>
        <LineChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="Time" tick={{ fontSize: 12 }} />
          <YAxis domain={["auto", "auto"]} />
          <Tooltip />
          <Legend verticalAlign="top" height={36} />

          <Line
            type="monotone"
            dataKey="Tenkan-sen"
            stroke="#8884d8"
            dot={false}
            name="Tenkan-sen"
          />
          <Line
            type="monotone"
            dataKey="Kijun-sen"
            stroke="#82ca9d"
            dot={false}
            name="Kijun-sen"
          />
          <Line
            type="monotone"
            dataKey="Senkou Span A"
            stroke="#ffc658"
            dot={false}
            name="Senkou Span A"
          />
          <Line
            type="monotone"
            dataKey="Senkou Span B"
            stroke="#ff7300"
            dot={false}
            name="Senkou Span B"
          />
          <Line
            type="monotone"
            dataKey="Chikou Span"
            stroke="#0000ff"
            dot={false}
            name="Chikou Span"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default IndexIchimoku;
