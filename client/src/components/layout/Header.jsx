import React, { useEffect, useState } from "react";
import LogoSymbol from "../../assets/Logo.svg";

export function Header({
  isDarkMode,
  onToggleDarkMode,
  onLogoClick,
  showNav = true,
  forceSolid = false,
}) {
  const [isScrolled, setIsScrolled] = useState(false);
  const [hoveredItem, setHoveredItem] = useState(null);
  const [isLogoHovered, setIsLogoHovered] = useState(false);
  const [isToggleHovered, setIsToggleHovered] = useState(false);

  useEffect(() => {
    if (forceSolid) return;

    const handleScroll = () => {
      setIsScrolled(window.scrollY > 0);
    };

    handleScroll();
    window.addEventListener("scroll", handleScroll);

    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, [forceSolid]);

  const effectiveScrolled = forceSolid ? true : isScrolled;

  const mainColor = "#0c303c";
  const whiteHoverColor = "#d9d9d9";
  const solidHoverColor = "#4f6b75";
  const toggleHoverGreen = "#28a745";

  const getTextColor = (key) => {
    const baseColor = effectiveScrolled
      ? isDarkMode
        ? "#ffffff"
        : mainColor
      : "#ffffff";

    if (hoveredItem !== key && !(key === "logo" && isLogoHovered)) {
      return baseColor;
    }

    if (!effectiveScrolled) {
      return whiteHoverColor;
    }

    if (isDarkMode) {
      return whiteHoverColor;
    }

    return solidHoverColor;
  };

  const headerBackground = effectiveScrolled
    ? isDarkMode
      ? "rgba(0,0,0,0.92)"
      : "rgba(255,255,255,0.96)"
    : "transparent";

  const borderColor = effectiveScrolled
    ? isDarkMode
      ? "1px solid rgba(255,255,255,0.10)"
      : "1px solid rgba(12,48,60,0.08)"
    : "1px solid rgba(255,255,255,0.18)";

  const logoFilter = (() => {
    if (!(isLogoHovered || hoveredItem === "logo")) {
      return effectiveScrolled
        ? isDarkMode
          ? "brightness(0) invert(1)"
          : "brightness(0) saturate(100%) invert(14%) sepia(26%) saturate(920%) hue-rotate(150deg) brightness(94%) contrast(95%)"
        : "brightness(0) invert(1)";
    }

    if (!effectiveScrolled || isDarkMode) {
      return "brightness(0) saturate(0%) invert(85%)";
    }

    return "brightness(0) saturate(100%) invert(38%) sepia(12%) saturate(612%) hue-rotate(150deg) brightness(94%) contrast(86%)";
  })();

  const scrollToSection = (id) => {
    const section = document.getElementById(id);
    if (!section) return;

    section.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  };

  const navButtonStyle = (key) => ({
    color: getTextColor(key),
    transition: "color 0.2s ease, opacity 0.2s ease",
  });

  return (
    <header
      className="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
      style={{
        backgroundColor: headerBackground,
        backdropFilter: effectiveScrolled ? "blur(10px)" : "none",
        WebkitBackdropFilter: effectiveScrolled ? "blur(10px)" : "none",
        borderBottom: borderColor,
        boxShadow: effectiveScrolled
          ? isDarkMode
            ? "0 4px 20px rgba(0,0,0,0.35)"
            : "0 4px 20px rgba(12,48,60,0.06)"
          : "none",
      }}
    >
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        <button
          type="button"
          onClick={onLogoClick}
          onMouseEnter={() => {
            setIsLogoHovered(true);
            setHoveredItem("logo");
          }}
          onMouseLeave={() => {
            setIsLogoHovered(false);
            setHoveredItem(null);
          }}
          className="flex items-center gap-2.5 bg-transparent border-0 p-0 cursor-pointer"
          aria-label="업로드 페이지로 이동"
          title="업로드 페이지로 이동"
        >
          <img
            src={LogoSymbol}
            alt="RealOrAI 로고"
            className="w-6 h-6 object-contain"
            style={{
              filter: logoFilter,
              transition: "filter 0.2s ease",
            }}
          />

          <span
            className="font-extrabold text-[1.35rem] leading-none tracking-[-0.02em]"
            style={{
              color: getTextColor("logo"),
              fontFamily: "Manrope, sans-serif",
              transition: "color 0.2s ease",
            }}
          >
            RealOrAI
          </span>
        </button>

        <div className="flex items-center ml-auto gap-8">
          {showNav && (
            <nav className="hidden md:flex items-center gap-8">
              <button
                type="button"
                onClick={() => scrollToSection("image-analysis")}
                onMouseEnter={() => setHoveredItem("image-analysis")}
                onMouseLeave={() => setHoveredItem(null)}
                className="font-semibold text-base bg-transparent border-0 p-0 cursor-pointer"
                style={navButtonStyle("image-analysis")}
              >
                이미지 분석
              </button>

              <button
                type="button"
                onClick={() => scrollToSection("analysis-elements")}
                onMouseEnter={() => setHoveredItem("analysis-elements")}
                onMouseLeave={() => setHoveredItem(null)}
                className="font-semibold text-base bg-transparent border-0 p-0 cursor-pointer"
                style={navButtonStyle("analysis-elements")}
              >
                분석 요소
              </button>
            </nav>
          )}

          <button
            type="button"
            onClick={onToggleDarkMode}
            onMouseEnter={() => setIsToggleHovered(true)}
            onMouseLeave={() => setIsToggleHovered(false)}
            className="relative w-[52px] h-[30px] rounded-full transition-all duration-300 border-0 cursor-pointer"
            style={{
              backgroundColor: isDarkMode
                ? isToggleHovered
                  ? "#555555"
                  : "#111111"
                : isToggleHovered
                  ? toggleHoverGreen
                  : "#34c759",
              boxShadow: isDarkMode
                ? "inset 0 0 0 1px rgba(255,255,255,0.12)"
                : "inset 0 0 0 1px rgba(0,0,0,0.06)",
            }}
            aria-label="배경 모드 전환"
            title="배경 모드 전환"
          >
            <span
              className="absolute top-[3px] left-[3px] w-[24px] h-[24px] rounded-full transition-all duration-300"
              style={{
                backgroundColor: "#ffffff",
                transform: isDarkMode ? "translateX(22px)" : "translateX(0)",
                boxShadow: "0 1px 4px rgba(0,0,0,0.25)",
              }}
            />
          </button>
        </div>
      </div>
    </header>
  );
}
