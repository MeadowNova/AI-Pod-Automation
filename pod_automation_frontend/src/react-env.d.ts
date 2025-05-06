/// <reference types="react" />
/// <reference types="react-dom" />

declare namespace React {
  interface ElementAttributesProperty {
    props: {};
  }
  
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}

declare module 'react/jsx-runtime' {
  export default any;
  export const jsx: any;
  export const jsxs: any;
}

declare module '@heroicons/react/24/outline' {
  export const ArrowTrendingUpIcon: React.ElementType;
  export const BanknotesIcon: React.ElementType;
  export const DocumentDuplicateIcon: React.ElementType;
  export const CpuChipIcon: React.ElementType;
  export const CheckCircleIcon: React.ElementType;
  export const SparklesIcon: React.ElementType;
}
