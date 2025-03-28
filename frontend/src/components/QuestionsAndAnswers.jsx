import React from "react";
import { sharePriceEvaluation, fundAndTech, macro } from "../assets/infoData";
import CustomLabel from "./CustomLabel";

const QuestionSection = ({ title, data }) => {
  return (
    <div className="mb-8">
      <div className="mb-2">
        <span className="text-xl font-semibold text-gray-800 mb-4 bg-blue-100 rounded-md px-4">{title}</span>
      </div>
      <CustomLabel theme="clear" className="bg-slate-100 flex flex-column flex-wrap">
        {Object.entries(data).map(([question, answers], index) => (
          <div key={index} className="mb-6">
            <span className="text-lg font-medium text-gray-900">{question}</span>
            <ul className="ml-4 list-disc text-gray-700">
              {answers.map((answer, i) => (
                <li key={i} className="mt-1">
                  {answer}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </CustomLabel>
    </div>
  );
};

const QuestionsAndAnswers = () => {
  return (
    <div className="p-8 bg-white shadow rounded-lg my-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Вопросы и ответы</h2>
      <QuestionSection title="Варианты оценки стоимости акций" data={sharePriceEvaluation} />
      <QuestionSection title="Фундаментальный и технический анализ" data={fundAndTech} />
      <QuestionSection title="Макроэкономическая перспектива" data={macro} />
    </div>
  );
};

export default QuestionsAndAnswers;
