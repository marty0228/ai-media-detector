import React from 'react';

// 구글 머티리얼 심볼 아이콘 컴포넌트
export default function MaterialIcon({ children, className = "", style = {} }) {
  return (
    <span
      className={`material-symbols-outlined ${className}`.trim()}
      style={style}
    >
      {children}
    </span>
  );
}
