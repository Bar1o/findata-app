import React, { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@gravity-ui/uikit";

const CompaniesPage = (props) => {
  const companies = ["SBER", "GAZP", "HEAD", "OZON", "PIKK"];
  const [activeComp, setActiveComp] = useState("SBER");

  function handleClickedComp(comp) {
    setActiveComp(comp);
  }

  return (
    <>
      <div className="text-sm justify-center flex flex-row gap-4 sm:gap-4 md:gap-5 ">
        {companies.map((comp) => (
          <Button
            key={comp}
            selected={activeComp === comp}
            // view="outlined-info"
            size="l"
            width="small"
            onClick={() => handleClickedComp(comp)}
          >
            {comp}
          </Button>
        ))}
      </div>
    </>
  );
};

export default CompaniesPage;
