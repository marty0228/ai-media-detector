import React from 'react';
import { COLORS } from '../constants';
import MaterialIcon from './MaterialIcon';

// 앱 하단 푸터 컴포넌트
export default function Footer() {
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
            informational purposes only. {/* 분석은 확률적이며 참고용입니다. */}
          </p>
        </div>
        <nav
          className="flex flex-wrap justify-center gap-8 text-sm font-bold uppercase"
          style={{ color: COLORS.onSurfaceVariant, letterSpacing: "0.18em" }}
        >
          <a href="#" className="transition-colors hover:opacity-80">
            Terms of Service {/* 서비스 약관 */}
          </a>
          <a href="#" className="transition-colors hover:opacity-80">
            Privacy Policy {/* 개인정보 처리방침 */}
          </a>
          <a href="#" className="transition-colors hover:opacity-80">
            Contact Support {/* 고객 지원 */}
          </a>
        </nav>
      </div>
    </footer>
  );
}
