import React from "react";
import { ichimoku } from "../assets/infoData";

const InfoIchimoku = () => {
  return (
    <div className="p-8 bg-white rounded-lg my-4">
      {Object.entries(ichimoku).map(([sectionTitle, details]) => (
        <div key={sectionTitle} className="mb-4">
          <span className="text-xl font-semibold text-gray-800 mb-4 bg-blue-100 rounded-md px-4 py-1 inline-block">{sectionTitle}</span>
          <ul className="ml-4 list-disc text-gray-700">
            {details.map((detail, index) => (
              <li key={index} className="mt-1">
                {detail}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default InfoIchimoku;
