import React, { useState } from "react";
import { COLORS } from "../../constants/colors";
import { MaterialIcon } from "../common/MaterialIcon";

const footerContents = {
  terms: {
    title: "이용 약관",
    content: `
제1조 목적
본 약관은 AI 판독기 서비스의 이용 조건과 절차, 이용자와 서비스 제공자 간의 권리·의무 및 책임 사항을 규정하는 것을 목적으로 합니다.

제2조 서비스의 내용
AI 판독기는 사용자가 업로드한 이미지 또는 메타데이터를 분석하여 AI 생성 가능성, 조작 가능성, 참고용 판독 결과를 제공합니다.

제3조 분석 결과의 성격
본 서비스의 분석 결과는 확률 기반 참고 자료이며, 법적 판단이나 최종 사실 판정을 보장하지 않습니다.
사용자는 분석 결과를 참고 목적으로만 활용해야 하며, 결과 해석 및 사용에 따른 책임은 사용자에게 있습니다.

제4조 이용자의 의무
이용자는 타인의 권리를 침해하는 이미지, 불법 자료, 개인정보가 포함된 자료를 무단으로 업로드해서는 안 됩니다.
또한 서비스의 정상적인 운영을 방해하거나 분석 시스템을 악용하는 행위를 해서는 안 됩니다.

제5조 서비스 제한
서비스 제공자는 시스템 점검, 기술적 문제, 부적절한 이용 행위가 있는 경우 서비스 이용을 일시적으로 제한할 수 있습니다.

제6조 책임의 제한
AI 판독기는 분석 결과의 정확성을 높이기 위해 노력하지만, 모든 이미지에 대해 완전한 판별을 보장하지 않습니다.
서비스 제공자는 사용자가 분석 결과를 근거로 내린 판단이나 그로 인해 발생한 손해에 대해 책임을 지지 않습니다.

제7조 약관의 변경
본 약관은 서비스 개선 또는 관련 법령 변경에 따라 수정될 수 있으며, 변경 사항은 서비스 화면을 통해 안내합니다.
    `,
  },

  privacy: {
    title: "개인정보 처리방침",
    content: `
1. 개인정보 처리 목적
AI 판독기는 이미지 분석 서비스 제공, 분석 결과 생성, 서비스 품질 개선을 위해 필요한 범위 내에서 개인정보를 처리할 수 있습니다.

2. 수집하는 정보
서비스 이용 과정에서 사용자가 업로드한 이미지 파일, 이미지 메타데이터, 분석 요청 시간, 분석 결과 정보가 처리될 수 있습니다.
단, 본 서비스는 주민등록번호, 계좌번호, 비밀번호와 같은 민감한 개인정보 제공을 요구하지 않습니다.

3. 이미지 및 메타데이터 처리
업로드된 이미지는 AI 생성 여부 및 조작 가능성 분석을 위해 사용됩니다.
이미지에 포함된 EXIF, 촬영 기기 정보, 생성 프로그램 정보, 파일 크기, 해상도 등의 메타데이터가 분석에 활용될 수 있습니다.

4. 개인정보 보유 및 이용 기간
분석을 위해 업로드된 파일과 분석 결과는 서비스 제공 목적 달성 후 지체 없이 삭제하는 것을 원칙으로 합니다.
다만 오류 확인, 서비스 개선, 부정 이용 방지를 위해 필요한 경우 제한된 기간 동안 보관될 수 있습니다.

5. 개인정보의 제3자 제공
AI 판독기는 이용자의 개인정보를 외부에 판매하거나 임의로 제공하지 않습니다.
다만 법령에 따른 요청이 있거나 사용자의 동의가 있는 경우에는 예외적으로 제공될 수 있습니다.

6. 개인정보의 안전성 확보 조치
서비스 제공자는 개인정보가 무단 접근, 유출, 변조, 훼손되지 않도록 접근 제한, 보안 관리, 파일 관리 등의 조치를 수행합니다.

7. 이용자의 권리
이용자는 자신의 개인정보에 대해 열람, 정정, 삭제, 처리 정지를 요청할 수 있습니다.
관련 요청은 서비스 내 고객 지원 경로를 통해 접수할 수 있습니다.

8. 개인정보 보호 책임
개인정보 처리와 관련한 문의는 고객 지원을 통해 접수할 수 있으며, 서비스 제공자는 접수된 문의를 확인 후 처리합니다.

9. 처리방침 변경
본 개인정보 처리방침은 서비스 운영 방식 또는 관련 법령 변경에 따라 수정될 수 있습니다.
    `,
  },

  support: {
    title: "고객 지원",
    content: `
AI 판독기 이용 중 문제가 발생한 경우 아래 내용을 확인해 주세요.

1. 분석 결과가 이상한 경우
AI 판독 결과는 확률 기반 결과이므로 실제 이미지와 다르게 판단될 수 있습니다.
특히 카카오톡 전송, 캡처 이미지, 편집 이미지처럼 메타데이터가 변경된 경우 결과가 달라질 수 있습니다.

2. 이미지 업로드가 되지 않는 경우
파일 형식이 JPG, PNG, WEBP 등 지원 형식인지 확인해 주세요.
파일 용량이 너무 큰 경우 업로드가 제한될 수 있습니다.

3. 분석 결과의 의미
AI 가능성이 높게 표시되었다고 해서 반드시 AI 이미지라는 뜻은 아닙니다.
반대로 AI 가능성이 낮게 표시되어도 실제 촬영 이미지임을 보장하는 것은 아닙니다.

4. 문의 방법
서비스 오류, 분석 결과 문의, 개인정보 관련 문의는 관리자에게 문의해 주세요.

이메일 : owen030506@gmail.com
운영 시간 : 평일 09:00 ~ 18:00
    `,
  },
};

export function Footer({ isDarkMode = false }) {
  const [modalType, setModalType] = useState(null);

  const closeModal = () => {
    setModalType(null);
  };

  const modalData = modalType ? footerContents[modalType] : null;
  const modalSurfaceColor = isDarkMode ? "#000000" : "#ffffff";
  const modalTitleColor = isDarkMode ? "#ffffff" : COLORS.primary;
  const modalTextColor = isDarkMode
    ? "rgba(255,255,255,0.78)"
    : COLORS.onSurfaceVariant;
  const modalBorderColor = isDarkMode
    ? "rgba(255,255,255,0.14)"
    : "rgba(193,199,203,0.32)";

  return (
    <>
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
                className="font-bold text-lg tracking-tight"
                style={{
                  color: COLORS.primary,
                  fontFamily: "Manrope, sans-serif",
                  letterSpacing: "-0.03em",
                }}
              >
                AI 판독기
              </span>
            </div>

            <p
              className="text-sm text-center md:text-left max-w-sm"
              style={{ color: COLORS.onSurfaceVariant }}
            >
              © 2026 AI 판독기. 본 분석 결과는 확률에 기반하며 참고용으로만
              제공됩니다.
            </p>
          </div>

          <nav
            className="flex flex-wrap justify-center gap-8 text-sm font-bold"
            style={{ color: COLORS.onSurfaceVariant, letterSpacing: "0.1em" }}
          >
            <button
              type="button"
              onClick={() => setModalType("terms")}
              className="transition-colors hover:opacity-80"
            >
              이용 약관
            </button>

            <button
              type="button"
              onClick={() => setModalType("privacy")}
              className="transition-colors hover:opacity-80"
            >
              개인정보 처리방침
            </button>

            <button
              type="button"
              onClick={() => setModalType("support")}
              className="transition-colors hover:opacity-80"
            >
              고객 지원
            </button>
          </nav>
        </div>
      </footer>

      {modalData && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center px-4"
          style={{ backgroundColor: "rgba(0, 0, 0, 0.45)" }}
          onClick={closeModal}
        >
          <div
            className="w-full max-w-2xl max-h-[80vh] overflow-y-auto rounded-2xl p-8 shadow-xl"
            style={{
              backgroundColor: modalSurfaceColor,
              border: `1px solid ${modalBorderColor}`,
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-6">
              <h2
                className="text-xl font-bold"
                style={{ color: modalTitleColor }}
              >
                {modalData.title}
              </h2>

              <button
                type="button"
                onClick={closeModal}
                className="text-2xl font-bold hover:opacity-70"
                style={{ color: modalTextColor }}
              >
                ×
              </button>
            </div>

            <div
              className="whitespace-pre-line text-sm leading-7"
              style={{ color: modalTextColor }}
            >
              {modalData.content}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
