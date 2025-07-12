# Customer Section Components Documentation

This directory contains various implementations of the Customer Section component used in the Checker application.

## Overview

The Customer Section is a critical part of the welcome screen, responsible for customer selection, project management, and providing context for workflow operations. Different variants have been developed to address specific requirements and use cases.

## Current Production Version

**CustomerSectionV2** (`welcome_screen_components/customer_section_v2.py`)

This is the current production version used in the main application. It features:

- Enhanced project selection with dropdown
- New project creation dialog
- Recent projects list with quick access
- Improved UI with scrollable content
- Intelligent customer recognition

## Alternative Implementations

### Base Customer Section (`customer_section.py`)

A simpler implementation with basic customer selection functionality. Used primarily for testing or as a fallback.

### Complete Customer Section (`customer_section_complete.py`)

Enhanced version with project selection capabilities, serving as a transitional implementation between the basic version and V2.

### Calendar Integration (`customer_section_with_calendar.py`)

Specialized version that integrates calendar functionality for scheduling and date-based operations. Used in specific workflows that require date selection.

## Usage Guidelines

- For new development, always use `CustomerSectionV2`
- The other variants are maintained for compatibility with test scripts and specialized workflows
- When making changes, ensure compatibility with the main application and test suite

## Integration

The customer section components are integrated into the welcome screen and interact with:

- KundenManager for customer/project data
- WorkflowRouter for workflow operations
- UITheme for consistent styling
- Logger for error reporting

## Technical Notes

All customer section variants extend `ctk.CTkFrame` and implement the `SectionHeaderMixin` for consistent header styling. They maintain a similar API to ensure interchangeability in different contexts, but with varying levels of functionality.
