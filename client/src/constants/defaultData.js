export const defaultResult = {
  summary: {
    finalScore: 71.8,
    verdict: "AI 생성 의심",
    confidence: 0.902,
    description:
      "이 프로토타입 결과는 5가지 설명 가능한 요소를 결합하여 표시하며, 추후 백엔드 분석 결과로 대체될 수 있습니다.",
  },
  factors: [
    {
      title: "출처 검증",
      subtitle: "기원 및 이력",
      score: 74,
      accent: "#006a60",
      progressLabel: "신뢰 지수",
      progressValue: "검증 낮음",
      metrics: [
        { label: "자격 증명 상태", value: "검증안됨" },
        { label: "수정 기록", value: "누락됨" },
      ],
      description:
        "현재 프로토타입 워크플로우에서 서명된 콘텐츠 자격 증명이나 검증 가능한 생성 경로가 확인되지 않았습니다.",
    },
    {
      title: "메타데이터 분석",
      subtitle: "EXIF 및 헤더",
      score: 48,
      accent: "#ffb780",
      progressLabel: "헤더 무결성",
      progressValue: "의심스러움",
      metrics: [
        { label: "카메라 제조사", value: "제한됨 / 제거됨" },
        { label: "소프트웨어 태그", value: "검토 필요" },
      ],
      description:
        "메타데이터는 독립적인 신호로 취급되므로 헤더 일관성과 소프트웨어 흔적을 따로 검토할 수 있습니다.",
    },
    {
      title: "외부 검색 검증",
      subtitle: "교차 출처 검색",
      score: 69,
      accent: "#006a60",
      progressLabel: "크로스 웹 일치",
      progressValue: "약한 일치",
      metrics: [
        { label: "시각적 일치", value: "낮음 / 알 수 없음" },
        { label: "출처 추적", value: "미확인" },
      ],
      description:
        "외부 검색은 신뢰할 수 있는 이전 등장 기록이나 안정적인 출처 추적을 찾을 수 있는지 확인하는 데 도움을 줍니다.",
    },
    {
      title: "시각적 이상 분석",
      subtitle: "사람 확인 가능 오류",
      score: 81,
      accent: "#ba1a1a",
      progressLabel: "오류 밀도",
      progressValue: "높음",
      metrics: [
        { label: "경계 일관성", value: "불일치" },
        { label: "조명 패턴", value: "주의 대상" },
      ],
      description:
        "이 요소는 가장자리 왜곡, 조명 불일치, 불규칙한 세부 묘사와 같은 시각적인 단서를 찾아 냅니다.",
    },
    {
      title: "포렌식 패턴 분석",
      subtitle: "노이즈 및 압축 단서",
      score: 66,
      accent: "#264653",
      progressLabel: "저수준 신호",
      progressValue: "감지됨",
      metrics: [
        { label: "노이즈 패턴", value: "불규칙함" },
        { label: "압축 흔적", value: "존재함" },
      ],
      description:
        "포렌식 패턴 분석은 압축, 노이즈 및 픽셀 수준의 불규칙성과 같은 저수준 증거에 중점을 둡니다.",
    },
  ],
  notes: {
    heroTitle: "구조화된 프로토타입 출력",
    heroText:
      "결과 객체로부터 랜더링되어, 나중에 동일한 UI를 유지하면서 실제 API 응답으로 대체할 수 있습니다.",
    sideTitle: "작업 상태",
    sideItems: [
      { label: "업로드 상태", value: "준비 완료" },
      { label: "결과 출처", value: "테스트 데이터" },
      { label: "요소 수", value: "5 가지 요소" },
      { label: "API 연동", value: "대기 중" },
    ],
  },
};

export const defaultFile = {
  name: "업로드된 이미지 없음",
  type: "알 수 없음",
  size: "알 수 없음",
};
