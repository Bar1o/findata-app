import { useState } from "react";
import HomePage from "./components/HomePage";
import Header from "./components/Header";
import IndexIchimoku from "./components/IndexIchimoku";
import PeriodButtons from "./components/PeriodButtons";

function App() {
  return (
    <div className="flex flex-col p-4 max-w-[1200px] mx-auto w-full">
      <section className="min-h-screen flex flex-col">
        <Header />
        {/* <HomePage /> */}
        {/* <IndexIchimoku figi="BBG004730N88" /> */}

        <PeriodButtons figi="BBG004730N88" />
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
