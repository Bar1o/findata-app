import React from "react";
import PropTypes from "prop-types";
import { Button } from "@gravity-ui/uikit";

const PeriodButtons = ({ period, setPeriod, periods }) => {
  return (
    <div className="text-sm flex flex-row gap-2 p-2 sm:gap-4 md:gap-5">
      {periods.map((p) => (
        <Button key={p} selected={period === p} size="l" width="small" onClick={() => setPeriod(p)}>
          {p}
        </Button>
      ))}
    </div>
  );
};

PeriodButtons.propTypes = {
  period: PropTypes.string.isRequired,
  setPeriod: PropTypes.func.isRequired,
  periods: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default PeriodButtons;
