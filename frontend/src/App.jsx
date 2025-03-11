import { useState } from "react";
import HomePage from "./components/HomePage";
import Header from "./components/Header";

import CompaniesPage from "./components/CompaniesPage";

function App() {
  // TODO: далее фиги на каждой странице свой
  // const [onCompPage, setOnCompPage] = useState(true);

  return (
    <div className="flex flex-col p-4 max-w-[1200px] mx-auto w-full">
      <section className="min-h-screen flex flex-col">
        <Header />

        {/* <button onClick={() => setOnCompPage(true)}>{onCompPage ? <HomePage /> : ""}</button> */}
        <CompaniesPage />
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
