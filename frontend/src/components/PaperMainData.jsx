import React, { useEffect, useState } from "react";
import { Button } from "@gravity-ui/uikit";
import { Label } from "@gravity-ui/uikit";
import { FetchPaperData } from "./FetchData";

const PaperMainData = (props) => {
  const { ticker } = props;
  const [mainData, setMainData] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const paperData = await FetchPaperData("/api/paper_main_data/", ticker);
        console.log("fetched PaperMainData", paperData);
        setMainData(paperData.mainData);
      } catch (error) {
        console.error("can't fetch main paper data:", error);
      }
    };
    fetchData();
  }, [ticker]);
  return (
    <div>
      <Label theme="info" size="m">
        Данные о бумаге
      </Label>
    </div>
  );
};

export default PaperMainData;
