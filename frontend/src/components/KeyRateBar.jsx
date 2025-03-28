import React, { useState, useEffect } from "react";
import { Label } from "@gravity-ui/uikit";
import { FetchKeyRate } from "./FetchData";

const KeyRateBar = ({ onToggleInflation }) => {
  const defaultPeriod = "D";
  const [kr, setKr] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const keyRate = await FetchKeyRate(defaultPeriod);
        console.log("fetched kr", keyRate);
        setKr(keyRate.keyRate.rate);
      } catch (error) {
        console.error(`Error fetching data for keyRate for "${defaultPeriod}":`, error);
      }
    };
    fetchData();
  }, []);

  return (
    <Label
      onClick={onToggleInflation}
      className="px-1 py-2 rounded-lg cursor-pointer"
      theme="normal"
      size="xs"
      value={kr ? `${kr}%` : "Loading..."}
    >
      Ставка ЦБ
    </Label>
  );
};

export default KeyRateBar;
