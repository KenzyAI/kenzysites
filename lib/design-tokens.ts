export const designTokens = {
  // Colors
  colors: {
    primary: {
      50: 'hsl(220, 70%, 98%)',
      100: 'hsl(220, 70%, 95%)',
      200: 'hsl(220, 70%, 90%)',
      300: 'hsl(220, 70%, 80%)',
      400: 'hsl(220, 70%, 60%)',
      500: 'hsl(220, 70%, 50%)', // Main brand color
      600: 'hsl(220, 70%, 45%)',
      700: 'hsl(220, 70%, 35%)',
      800: 'hsl(220, 70%, 25%)',
      900: 'hsl(220, 70%, 15%)',
    },
    secondary: {
      50: 'hsl(160, 60%, 98%)',
      100: 'hsl(160, 60%, 95%)',
      200: 'hsl(160, 60%, 90%)',
      300: 'hsl(160, 60%, 80%)',
      400: 'hsl(160, 60%, 60%)',
      500: 'hsl(160, 60%, 50%)',
      600: 'hsl(160, 60%, 45%)',
      700: 'hsl(160, 60%, 35%)',
      800: 'hsl(160, 60%, 25%)',
      900: 'hsl(160, 60%, 15%)',
    },
    gray: {
      50: 'hsl(210, 20%, 98%)',
      100: 'hsl(210, 20%, 95%)',
      200: 'hsl(210, 20%, 90%)',
      300: 'hsl(210, 20%, 80%)',
      400: 'hsl(210, 20%, 60%)',
      500: 'hsl(210, 20%, 50%)',
      600: 'hsl(210, 20%, 45%)',
      700: 'hsl(210, 20%, 35%)',
      800: 'hsl(210, 20%, 25%)',
      900: 'hsl(210, 20%, 15%)',
    },
    success: {
      50: 'hsl(142, 76%, 95%)',
      100: 'hsl(142, 76%, 90%)',
      500: 'hsl(142, 76%, 50%)',
      600: 'hsl(142, 76%, 45%)',
      700: 'hsl(142, 76%, 35%)',
    },
    warning: {
      50: 'hsl(45, 86%, 95%)',
      100: 'hsl(45, 86%, 90%)',
      500: 'hsl(45, 86%, 50%)',
      600: 'hsl(45, 86%, 45%)',
      700: 'hsl(45, 86%, 35%)',
    },
    error: {
      50: 'hsl(0, 84%, 95%)',
      100: 'hsl(0, 84%, 90%)',
      500: 'hsl(0, 84%, 60%)',
      600: 'hsl(0, 84%, 55%)',
      700: 'hsl(0, 84%, 45%)',
    },
  },

  // Typography
  typography: {
    fontFamily: {
      sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'Fira Code', 'Monaco', 'Cascadia Code', 'Ubuntu Mono', 'monospace'],
    },
    fontSize: {
      xs: ['0.75rem', { lineHeight: '1rem' }],
      sm: ['0.875rem', { lineHeight: '1.25rem' }],
      base: ['1rem', { lineHeight: '1.5rem' }],
      lg: ['1.125rem', { lineHeight: '1.75rem' }],
      xl: ['1.25rem', { lineHeight: '1.75rem' }],
      '2xl': ['1.5rem', { lineHeight: '2rem' }],
      '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
      '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
      '5xl': ['3rem', { lineHeight: '1' }],
      '6xl': ['3.75rem', { lineHeight: '1' }],
    },
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
    },
  },

  // Spacing
  spacing: {
    px: '1px',
    0: '0',
    0.5: '0.125rem',
    1: '0.25rem',
    1.5: '0.375rem',
    2: '0.5rem',
    2.5: '0.625rem',
    3: '0.75rem',
    3.5: '0.875rem',
    4: '1rem',
    5: '1.25rem',
    6: '1.5rem',
    7: '1.75rem',
    8: '2rem',
    9: '2.25rem',
    10: '2.5rem',
    11: '2.75rem',
    12: '3rem',
    14: '3.5rem',
    16: '4rem',
    20: '5rem',
    24: '6rem',
    28: '7rem',
    32: '8rem',
    36: '9rem',
    40: '10rem',
    44: '11rem',
    48: '12rem',
    52: '13rem',
    56: '14rem',
    60: '15rem',
    64: '16rem',
    72: '18rem',
    80: '20rem',
    96: '24rem',
  },

  // Border Radius
  borderRadius: {
    none: '0px',
    sm: '0.125rem',
    base: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    '2xl': '1rem',
    '3xl': '1.5rem',
    full: '9999px',
  },

  // Shadows
  boxShadow: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    base: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
    none: '0 0 #0000',
  },

  // Animation
  animation: {
    duration: {
      75: '75ms',
      100: '100ms',
      150: '150ms',
      200: '200ms',
      300: '300ms',
      500: '500ms',
      700: '700ms',
      1000: '1000ms',
    },
    easing: {
      linear: 'linear',
      in: 'cubic-bezier(0.4, 0, 1, 1)',
      out: 'cubic-bezier(0, 0, 0.2, 1)',
      'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
    },
  },

  // Z-Index
  zIndex: {
    auto: 'auto',
    0: '0',
    10: '10',
    20: '20',
    30: '30',
    40: '40',
    50: '50',
    modal: '1000',
    popover: '1010',
    overlay: '1020',
    dropdown: '1030',
    tooltip: '1040',
  },
} as const

// Type helpers
export type DesignTokens = typeof designTokens
export type Colors = keyof DesignTokens['colors']
export type ColorShades = keyof DesignTokens['colors']['primary']
export type Spacing = keyof DesignTokens['spacing']
export type BorderRadius = keyof DesignTokens['borderRadius']
