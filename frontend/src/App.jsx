import { useState } from "react";
import HomePage from "./components/HomePage";
import Header from "./components/Header";
import { Button } from "@gravity-ui/uikit";

import CompaniesPage from "./components/CompaniesPage";
import GdpData from "./components/GdpData";
import GdpSectors from "./components/GdpSectors";
import InflData from "./components/InflData";

function App() {
  const [onCompPage, setOnCompPage] = useState(true);
  const [showInflation, setShowInflation] = useState(false);

  return (
    <div className="flex flex-col p-4 max-w-[1200px] mx-auto w-full">
      <section className="min-h-screen flex flex-col">
        <Header onToggleInflation={() => setShowInflation((prev) => !prev)} />

        {showInflation && <InflData />}

        <div className="flex gap-4 mb-4 justify-center">
          <Button size="m" onClick={() => setOnCompPage(true)}>
            Компании
          </Button>
          <Button size="m" onClick={() => setOnCompPage(false)}>
            ВВП
          </Button>
        </div>

        {onCompPage ? (
          <CompaniesPage />
        ) : (
          <>
            <GdpSectors />
            <GdpData />
          </>
        )}
      </section>
      <div className="flex items-center justify-center gap-4">
        <p className="font-light text-grey-400 text-sm">
          Credits on <span className="text-blue-400">@vabarnis</span>
        </p>
      </div>
      <footer></footer>
    </div>
  );
}

export default App;
