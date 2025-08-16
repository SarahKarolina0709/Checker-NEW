/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // =================================================================
      // Typography System Extension - Translation Quality GUI
      // =================================================================
      
      fontFamily: {
        'sans': ['Segoe UI', 'system-ui', '-apple-system', 'sans-serif'],
      },
      
      // Exakte Schriftgrößen aus der GUI
      fontSize: {
        // Base sizes (desktop)
        'ty-caption': ['0.75rem', { lineHeight: '1.4' }],      // 12px
        'ty-body': ['0.875rem', { lineHeight: '1.4' }],        // 14px
        'ty-subheading': ['1.125rem', { lineHeight: '1.2' }],  // 18px
        'ty-heading': ['1.375rem', { lineHeight: '1.2' }],     // 22px
        'ty-title': ['1.625rem', { lineHeight: '1.2' }],       // 26px
        
        // Responsive variants
        'ty-caption-sm': ['0.6875rem', { lineHeight: '1.4' }], // 11px (mobile)
        'ty-body-sm': ['0.8125rem', { lineHeight: '1.4' }],    // 13px (mobile)
        'ty-subheading-sm': ['1.0625rem', { lineHeight: '1.2' }], // 17px (mobile)
        'ty-heading-sm': ['1.3125rem', { lineHeight: '1.2' }], // 21px (mobile)
        'ty-title-sm': ['1.5625rem', { lineHeight: '1.2' }],   // 25px (mobile)
        
        'ty-caption-lg': ['0.8125rem', { lineHeight: '1.4' }], // 13px (desktop lg)
        'ty-body-lg': ['0.9375rem', { lineHeight: '1.4' }],    // 15px (desktop lg)
        'ty-subheading-lg': ['1.1875rem', { lineHeight: '1.2' }], // 19px (desktop lg)
        'ty-heading-lg': ['1.4375rem', { lineHeight: '1.2' }], // 23px (desktop lg)
        'ty-title-lg': ['1.6875rem', { lineHeight: '1.2' }],   // 27px (desktop lg)
      },
      
      fontWeight: {
        'ty-normal': '400',
        'ty-bold': '700',
      },
      
      // Colors aus der Translation Quality GUI
      colors: {
        'ty-primary': '#1F4E79',
        'ty-primary-hover': '#1A3F65',
        'ty-secondary': '#6C757D',
        'ty-secondary-hover': '#5A6169',
        'ty-text': '#374151',      // gray-700
        'ty-text-light': '#6B7280', // gray-500
        'ty-text-lighter': '#9CA3AF', // gray-400
        'ty-surface': '#FFFFFF',
        'ty-surface-border': '#E5E7EB',
        'ty-success': '#2E8B57',
        'ty-warning': '#F2994A',
        'ty-error': '#DC2626',
      }
    },
  },
  plugins: [
    // =================================================================
    // Custom Typography Plugin
    // =================================================================
    function({ addUtilities, theme }) {
      const newUtilities = {
        // Typography Classes
        '.ty-caption': {
          fontSize: theme('fontSize.ty-caption[0]'),
          lineHeight: theme('fontSize.ty-caption[1].lineHeight'),
          fontWeight: theme('fontWeight.ty-normal'),
          fontFamily: theme('fontFamily.sans'),
        },
        '.ty-body': {
          fontSize: theme('fontSize.ty-body[0]'),
          lineHeight: theme('fontSize.ty-body[1].lineHeight'),
          fontWeight: theme('fontWeight.ty-normal'),
          fontFamily: theme('fontFamily.sans'),
        },
        '.ty-body-bold': {
          fontSize: theme('fontSize.ty-body[0]'),
          lineHeight: theme('fontSize.ty-body[1].lineHeight'),
          fontWeight: theme('fontWeight.ty-bold'),
          fontFamily: theme('fontFamily.sans'),
        },
        '.ty-subheading': {
          fontSize: theme('fontSize.ty-subheading[0]'),
          lineHeight: theme('fontSize.ty-subheading[1].lineHeight'),
          fontWeight: theme('fontWeight.ty-bold'),
          fontFamily: theme('fontFamily.sans'),
        },
        '.ty-heading': {
          fontSize: theme('fontSize.ty-heading[0]'),
          lineHeight: theme('fontSize.ty-heading[1].lineHeight'),
          fontWeight: theme('fontWeight.ty-bold'),
          fontFamily: theme('fontFamily.sans'),
        },
        '.ty-title': {
          fontSize: theme('fontSize.ty-title[0]'),
          lineHeight: theme('fontSize.ty-title[1].lineHeight'),
          fontWeight: theme('fontWeight.ty-bold'),
          fontFamily: theme('fontFamily.sans'),
        },
        
        // Responsive Typography Classes
        '@screen sm': {
          '.ty-caption': {
            fontSize: theme('fontSize.ty-caption-sm[0]'),
            lineHeight: theme('fontSize.ty-caption-sm[1].lineHeight'),
          },
          '.ty-body, .ty-body-bold': {
            fontSize: theme('fontSize.ty-body-sm[0]'),
            lineHeight: theme('fontSize.ty-body-sm[1].lineHeight'),
          },
          '.ty-subheading': {
            fontSize: theme('fontSize.ty-subheading-sm[0]'),
            lineHeight: theme('fontSize.ty-subheading-sm[1].lineHeight'),
          },
          '.ty-heading': {
            fontSize: theme('fontSize.ty-heading-sm[0]'),
            lineHeight: theme('fontSize.ty-heading-sm[1].lineHeight'),
          },
          '.ty-title': {
            fontSize: theme('fontSize.ty-title-sm[0]'),
            lineHeight: theme('fontSize.ty-title-sm[1].lineHeight'),
          },
        },
        
        '@screen lg': {
          '.ty-caption': {
            fontSize: theme('fontSize.ty-caption-lg[0]'),
            lineHeight: theme('fontSize.ty-caption-lg[1].lineHeight'),
          },
          '.ty-body, .ty-body-bold': {
            fontSize: theme('fontSize.ty-body-lg[0]'),
            lineHeight: theme('fontSize.ty-body-lg[1].lineHeight'),
          },
          '.ty-subheading': {
            fontSize: theme('fontSize.ty-subheading-lg[0]'),
            lineHeight: theme('fontSize.ty-subheading-lg[1].lineHeight'),
          },
          '.ty-heading': {
            fontSize: theme('fontSize.ty-heading-lg[0]'),
            lineHeight: theme('fontSize.ty-heading-lg[1].lineHeight'),
          },
          '.ty-title': {
            fontSize: theme('fontSize.ty-title-lg[0]'),
            lineHeight: theme('fontSize.ty-title-lg[1].lineHeight'),
          },
        },
      };

      addUtilities(newUtilities);
    },
    
    // =================================================================
    // Component-specific Utility Plugin
    // =================================================================
    function({ addUtilities, theme }) {
      const componentUtilities = {
        // Button Components
        '.btn-base': {
          fontSize: theme('fontSize.ty-body[0]'),
          lineHeight: theme('fontSize.ty-body[1].lineHeight'),
          fontWeight: theme('fontWeight.ty-bold'),
          fontFamily: theme('fontFamily.sans'),
          padding: '0.75rem 1.5rem',
          borderRadius: '0.375rem',
          border: 'none',
          cursor: 'pointer',
          transition: 'all 0.15s ease-in-out',
        },
        
        '.btn-primary': {
          backgroundColor: theme('colors.ty-primary'),
          color: theme('colors.ty-surface'),
          '&:hover': {
            backgroundColor: theme('colors.ty-primary-hover'),
          },
        },
        
        '.btn-secondary': {
          backgroundColor: theme('colors.ty-secondary'),
          color: theme('colors.ty-surface'),
          '&:hover': {
            backgroundColor: theme('colors.ty-secondary-hover'),
          },
        },
        
        // Card Components
        '.card-base': {
          backgroundColor: theme('colors.ty-surface'),
          borderRadius: '0.5rem',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          border: `1px solid ${theme('colors.ty-surface-border')}`,
          padding: '1.5rem',
        },
        
        '.card-header': {
          fontSize: theme('fontSize.ty-subheading[0]'),
          lineHeight: theme('fontSize.ty-subheading[1].lineHeight'),
          fontWeight: theme('fontWeight.ty-bold'),
          fontFamily: theme('fontFamily.sans'),
          color: theme('colors.ty-text'),
          marginBottom: '1rem',
          paddingBottom: '0.5rem',
          borderBottom: `1px solid ${theme('colors.ty-surface-border')}`,
        },
        
        // Form Components
        '.form-label': {
          fontSize: theme('fontSize.ty-body[0]'),
          lineHeight: theme('fontSize.ty-body[1].lineHeight'),
          fontWeight: theme('fontWeight.ty-normal'),
          fontFamily: theme('fontFamily.sans'),
          color: theme('colors.ty-text'),
          display: 'block',
          marginBottom: '0.25rem',
        },
        
        '.form-label-required': {
          fontSize: theme('fontSize.ty-body[0]'),
          lineHeight: theme('fontSize.ty-body[1].lineHeight'),
          fontWeight: theme('fontWeight.ty-bold'),
          fontFamily: theme('fontFamily.sans'),
          color: theme('colors.ty-text'),
          display: 'block',
          marginBottom: '0.25rem',
        },
        
        '.form-input': {
          fontSize: theme('fontSize.ty-body[0]'),
          lineHeight: theme('fontSize.ty-body[1].lineHeight'),
          fontWeight: theme('fontWeight.ty-normal'),
          fontFamily: theme('fontFamily.sans'),
          padding: '0.5rem 0.75rem',
          border: `1px solid ${theme('colors.ty-surface-border')}`,
          borderRadius: '0.25rem',
          backgroundColor: theme('colors.ty-surface'),
          '&:focus': {
            outline: 'none',
            borderColor: theme('colors.ty-primary'),
            boxShadow: `0 0 0 2px ${theme('colors.ty-primary')}33`,
          },
        },
        
        // Status Components
        '.status-text': {
          fontSize: theme('fontSize.ty-caption[0]'),
          lineHeight: theme('fontSize.ty-caption[1].lineHeight'),
          fontWeight: theme('fontWeight.ty-normal'),
          fontFamily: theme('fontFamily.sans'),
          color: theme('colors.ty-text-light'),
        },
        
        '.meta-text': {
          fontSize: theme('fontSize.ty-caption[0]'),
          lineHeight: theme('fontSize.ty-caption[1].lineHeight'),
          fontWeight: theme('fontWeight.ty-normal'),
          fontFamily: theme('fontFamily.sans'),
          color: theme('colors.ty-text-lighter'),
        },
      };

      addUtilities(componentUtilities);
    },
  ],
};
