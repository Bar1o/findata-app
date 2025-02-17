import { useState } from "react";
import HomePage from "./components/HomePage";
import Header from "./components/Header";
import IndexIchimoku from "./components/IndexIchimoku";
import PeriodButtons from "./components/PeriodButtons";
import IndexIchimoku2 from "./components/IndexIchimoku2";
import CompaniesPage from "./components/CompaniesPage";
import { use } from "react";

function App() {
  // TODO: далее фиги на каждой странице свой
  // const [onCompPage, setOnCompPage] = useState(true);
  const [chartData, setChartData] = useState([]);
  const figi = "BBG004730N88";

  return (
    <div className="flex flex-col p-4 max-w-[1200px] mx-auto w-full">
      <section className="min-h-screen flex flex-col">
        <Header />

        {/* <button onClick={() => setOnCompPage(true)}>{onCompPage ? <HomePage /> : ""}</button> */}
        <CompaniesPage />
        <IndexIchimoku2 figi={figi} data={chartData} />
        <PeriodButtons figi={figi} setChartData={setChartData} />
        {/* <IndexIchimoku figi={figi} /> */}
      </section>
      <div className="flex items-center justify-center gap-4">
        <p className="font-light text-grey-400 text-sm">
          Credits on <span className="text-blue-400">@vabarnis</span>
          {/* add a link here */}
        </p>
      </div>
      <footer></footer>
    </div>
  );
}

export default App;
