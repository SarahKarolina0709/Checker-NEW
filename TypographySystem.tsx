// =============================================================================
// REACT TYPOGRAPHY SYSTEM COMPONENTS
// =============================================================================
// Basiert auf der Translation Quality GUI Typography-Hierarchie

import React from 'react';
import './design-tokens.css';

// =============================================================================
// Typography Components
// =============================================================================

export const Typography = {
  Title: ({ children, className = '', ...props }) => (
    <h1 className={`ty-title ${className}`} {...props}>
      {children}
    </h1>
  ),

  Heading: ({ children, className = '', ...props }) => (
    <h2 className={`ty-heading ${className}`} {...props}>
      {children}
    </h2>
  ),

  Subheading: ({ children, className = '', ...props }) => (
    <h3 className={`ty-subheading ${className}`} {...props}>
      {children}
    </h3>
  ),

  Body: ({ children, className = '', bold = false, ...props }) => (
    <p className={`${bold ? 'ty-body-bold' : 'ty-body'} ${className}`} {...props}>
      {children}
    </p>
  ),

  Caption: ({ children, className = '', ...props }) => (
    <span className={`ty-caption ${className}`} {...props}>
      {children}
    </span>
  ),
};

// =============================================================================
// Component-Specific Typography Components
// =============================================================================

export const Button = ({ 
  children, 
  variant = 'primary', 
  className = '', 
  ...props 
}) => {
  const baseClasses = 'btn px-6 py-3 rounded-md border-none cursor-pointer';
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700',
    warning: 'bg-orange-500 text-white hover:bg-orange-600',
  };

  return (
    <button 
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

export const Card = ({ title, children, className = '', ...props }) => (
  <div className={`bg-white p-6 rounded-lg shadow-sm border ${className}`} {...props}>
    {title && (
      <div className="card-header mb-4 pb-2 border-b border-gray-200">
        {title}
      </div>
    )}
    {children}
  </div>
);

export const FormField = ({ 
  label, 
  required = false, 
  children, 
  helpText,
  className = '',
  ...props 
}) => (
  <div className={`mb-4 ${className}`} {...props}>
    <label className={required ? 'form-label--required' : 'form-label'}>
      {label}
      {required && <span className="text-red-500 ml-1">*</span>}
    </label>
    <div className="mt-1">
      {children}
    </div>
    {helpText && (
      <Typography.Caption className="meta-text text-gray-500 mt-1">
        {helpText}
      </Typography.Caption>
    )}
  </div>
);

// =============================================================================
// Usage Examples Component
// =============================================================================

export const TypographyShowcase = () => {
  return (
    <div className="max-w-4xl mx-auto p-8 space-y-8">
      {/* Page Header */}
      <div className="text-center">
        <Typography.Title className="text-gray-800 mb-4">
          Translation Quality GUI - Typography System
        </Typography.Title>
        <Typography.Body className="text-gray-600">
          Demonstration der React-Components basierend auf dem Design-Token-System
        </Typography.Body>
      </div>

      {/* Hierarchy Demo */}
      <Card title="Typography Hierarchy">
        <div className="space-y-4 border-l-4 border-blue-600 pl-6">
          <Typography.Title className="text-gray-800">
            1. Title (26px) - Page Level Headers
          </Typography.Title>
          <Typography.Heading className="text-gray-800">
            2. Heading (22px) - Section Headers
          </Typography.Heading>
          <Typography.Subheading className="text-gray-800">
            3. Subheading (18px) - Card Headers
          </Typography.Subheading>
          <Typography.Body bold className="text-gray-800">
            4. Body Bold (14px) - Emphasized Content
          </Typography.Body>
          <Typography.Body className="text-gray-800">
            5. Body (14px) - Regular Content
          </Typography.Body>
          <Typography.Caption className="text-gray-600">
            6. Caption (12px) - Meta Information
          </Typography.Caption>
        </div>
      </Card>

      {/* Interactive Elements */}
      <Card title="Interactive Elements">
        <div className="space-y-4">
          <div className="flex gap-4 flex-wrap">
            <Button variant="primary">Primary Action</Button>
            <Button variant="secondary">Secondary Action</Button>
            <Button variant="warning">Warning Action</Button>
          </div>
          
          <Typography.Caption className="text-gray-500">
            Alle Buttons verwenden ty-body-bold (14px bold) für konsistente Typografie
          </Typography.Caption>
        </div>
      </Card>

      {/* Form Elements */}
      <Card title="Form Elements">
        <div className="space-y-6">
          <FormField 
            label="Customer Name" 
            required
            helpText="Enter the customer name for the translation project"
          >
            <input
              type="text"
              className="ty-body w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Standard input uses ty-body (14px normal)"
            />
          </FormField>

          <FormField 
            label="Project Description"
            helpText="Optional description for internal reference"
          >
            <textarea
              className="ty-body w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="Textarea also uses ty-body for consistency"
            />
          </FormField>
        </div>
      </Card>

      {/* Content Sections */}
      <Card title="Content Layout Example">
        <div className="space-y-4">
          <Typography.Subheading className="text-gray-800">
            Translation Quality Analysis
          </Typography.Subheading>
          
          <Typography.Body className="text-gray-700">
            Die Qualitätsanalyse verwendet ein standardisiertes Bewertungssystem
            zur objektiven Beurteilung von Übersetzungsleistungen. Jeder Text wird
            nach festgelegten Kriterien bewertet.
          </Typography.Body>

          <div className="bg-gray-50 p-4 rounded-md">
            <Typography.Body bold className="text-gray-800 mb-2">
              Wichtige Metriken:
            </Typography.Body>
            <ul className="space-y-1">
              <li className="ty-body text-gray-700">• Sprachliche Genauigkeit</li>
              <li className="ty-body text-gray-700">• Terminologische Konsistenz</li>
              <li className="ty-body text-gray-700">• Stilistische Angemessenheit</li>
            </ul>
          </div>

          <Typography.Caption className="text-gray-500">
            Bewertungssystem basiert auf ISO 17100 Standards für Übersetzungsdienstleistungen
          </Typography.Caption>
        </div>
      </Card>

      {/* CSS Variables Reference */}
      <Card title="CSS Variables Integration">
        <div className="space-y-4">
          <Typography.Body className="text-gray-700">
            Das System kann auch direkt über CSS-Variablen verwendet werden:
          </Typography.Body>
          
          <pre className="bg-gray-100 p-4 rounded-md text-sm overflow-x-auto">
{`// React Inline Styles mit CSS Variables
const customTitle = {
  fontSize: 'var(--ty-title-size)',
  fontWeight: 'var(--ty-title-weight)',
  lineHeight: 'var(--ty-title-line-height)',
  fontFamily: 'var(--ty-title-family)'
};

// Styled Components Integration
const StyledTitle = styled.h1\`
  font-size: var(--ty-title-size);
  font-weight: var(--ty-title-weight);
  line-height: var(--ty-title-line-height);
\`;`}
          </pre>
        </div>
      </Card>
    </div>
  );
};

// =============================================================================
// TypeScript Interface Definitions
// =============================================================================

export interface TypographyProps {
  children: React.ReactNode;
  className?: string;
}

export interface BodyProps extends TypographyProps {
  bold?: boolean;
}

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'warning';
  children: React.ReactNode;
}

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: React.ReactNode;
  children: React.ReactNode;
}

export interface FormFieldProps extends React.HTMLAttributes<HTMLDivElement> {
  label: string;
  required?: boolean;
  helpText?: string;
  children: React.ReactNode;
}

// =============================================================================
// Export Default
// =============================================================================

export default TypographyShowcase;
