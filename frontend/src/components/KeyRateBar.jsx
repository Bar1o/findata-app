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
    <div className="w-full gap-2 flex flex-row">
      <Label
        onClick={onToggleInflation}
        className="p-3 rounded-lg cursor-pointer"
        theme="normal"
        size="xs"
        value={kr ? `${kr}%` : "Loading..."}
      >
        Ставка ЦБ
      </Label>

      {/* <Label className="p-3 rounded-lg" theme="success" size="xs" value={"112 RUB"}>
        EUR
      </Label> */}
    </div>
  );
};

export default KeyRateBar;
