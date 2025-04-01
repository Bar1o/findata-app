import React from "react";

import logoCbr from "../assets/logos/cbr.png";
import logoSmLab from "../assets/logos/smartlab.png";
import logoTbank from "../assets/logos/tbank.png";
import logoTrView from "../assets/logos/trview.png";

const logos = [
  { src: logoCbr, alt: "ЦБ РФ" },
  { src: logoTbank, alt: "Т-банк" },
  { src: logoSmLab, alt: "smart-lab.ru" },
  { src: logoTrView, alt: "Trading View" },
];

const AllRights = () => {
  return (
    <div className="">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-row flex-wrap justify-center align-center gap-6">
          {logos.map((logo, index) => (
            <div key={index} className="w-24 h-10 flex items-center justify-center ">
              <img src={logo.src} alt={logo.alt} className="max-w-full max-h-full object-contain" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AllRights;
