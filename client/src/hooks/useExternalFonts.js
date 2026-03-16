import { useEffect } from "react";

export function useExternalFonts() {
  useEffect(() => {
    const head = document.head;
    const manropeInter = document.createElement("link");
    manropeInter.rel = "stylesheet";
    manropeInter.href =
      "https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap";

    const materialSymbols = document.createElement("link");
    materialSymbols.rel = "stylesheet";
    materialSymbols.href =
      "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0";

    head.appendChild(manropeInter);
    head.appendChild(materialSymbols);

    return () => {
      head.removeChild(manropeInter);
      head.removeChild(materialSymbols);
    };
  }, []);
}
