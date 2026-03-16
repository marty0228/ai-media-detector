import React from "react";
import { COLORS } from "../../constants/colors";
import { MaterialIcon } from "../common/MaterialIcon";

export function Footer() {
  return (
    <footer
      className="mt-24 px-8 py-16"
      style={{ backgroundColor: COLORS.surfaceContainerLow }}
    >
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-10">
        <div className="flex flex-col items-center md:items-start gap-4">
          <div className="flex items-center gap-2">
            <MaterialIcon style={{ color: COLORS.primary }}>
              security
            </MaterialIcon>
            <span
              className="font-bold text-lg uppercase"
              style={{
                color: COLORS.primary,
                fontFamily: "Manrope, sans-serif",
                letterSpacing: "-0.03em",
              }}
            >
              AI Authenticator
            </span>
          </div>
          <p
            className="text-sm text-center md:text-left max-w-sm"
            style={{ color: COLORS.onSurfaceVariant }}
          >
            © 2024 AI Authenticator. Analysis is probabilistic and for
            informational purposes only.
          </p>
        </div>
        <nav
          className="flex flex-wrap justify-center gap-8 text-sm font-bold uppercase"
          style={{ color: COLORS.onSurfaceVariant, letterSpacing: "0.18em" }}
        >
          <a href="#" className="transition-colors hover:opacity-80">
            Terms of Service
          </a>
          <a href="#" className="transition-colors hover:opacity-80">
            Privacy Policy
          </a>
          <a href="#" className="transition-colors hover:opacity-80">
            Contact Support
          </a>
        </nav>
      </div>
    </footer>
  );
}
