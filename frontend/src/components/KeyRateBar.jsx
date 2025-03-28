import React, { useState, useEffect } from "react";
import CustomLabel from "./CustomLabel";
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
    <div>
      <CustomLabel theme="clear" onClick={onToggleInflation}>
        <span>Ставка ЦБ :</span>
        <span className="ml-1">{kr ? `${kr}%` : "Loading..."}</span>
      </CustomLabel>
    </div>
  );
};

export default KeyRateBar;
