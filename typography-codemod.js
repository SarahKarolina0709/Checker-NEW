#!/usr/bin/env node

/**
 * =============================================================================
 * TYPOGRAPHY CODEMOD - Translation Quality GUI Migration
 * =============================================================================
 * 
 * Automated refactoring von veralteten Typography-Varianten zu dem neuen
 * vereinheitlichten System basierend auf:
 * caption 12px/normal, body 14px/normal, body_bold 14px/bold, 
 * subheading 18px/bold, heading 22px/bold, title 26px/bold
 */

const fs = require('fs');
const path = require('path');

// =============================================================================
// MAPPING CONFIGURATION
// =============================================================================

const TYPOGRAPHY_MAPPING = {
  // Button Typography -> body_bold
  'button_lg': 'body_bold',
  'button_md': 'body_bold', 
  'button': 'body_bold',
  'button_sm': 'body_bold',
  
  // Heading Hierarchy Simplification
  'heading_lg': 'heading',
  'heading_md': 'subheading',
  'heading_sm': 'subheading',
  
  // Body Text Consolidation
  'body_sm': 'body',
  'body_lg': 'body_bold',
  'body_md': 'body',
  
  // Label Consolidation
  'label_bold': 'body_bold',
  'label': 'body',
  'label_sm': 'caption',
  'label_lg': 'body_bold',
  
  // Caption Variants
  'caption_sm': 'caption',
  'caption_lg': 'caption',
  'small': 'caption',
  'small_normal': 'caption',
  
  // Title Variants
  'title_lg': 'title',
  'title_md': 'title',
  'display': 'title',
  'display_lg': 'title',
  
  // Misc Variants
  'menu': 'caption',
  'status': 'caption',
  'metric_value': 'heading',
  'code': 'body',
};

// =============================================================================
// REGEX PATTERNS
// =============================================================================

const PATTERNS = {
  // Python get_typography() Aufrufe
  pythonGetTypography: /get_typography\(['"]([^'"]+)['"]\)/g,
  
  // JavaScript/TypeScript font-size Eigenschaften  
  jsFontSize: /fontSize:\s*['"]([^'"]+)['"]/g,
  
  // CSS Klassen
  cssClasses: /\.ty-([a-zA-Z_-]+)/g,
  
  // HTML Klassen
  htmlClasses: /class(?:Name)?=['"]([^'"]*\bty-[a-zA-Z_-]+[^'"]*)['"]/g,
  
  // React Props
  reactProps: /typography=['"]([^'"]+)['"]/g,
  
  // Tailwind Utilities
  tailwindClasses: /(?:text-|font-)?ty-([a-zA-Z_-]+)/g,
};

// =============================================================================
// FILE PROCESSING
// =============================================================================

class TypographyCodemod {
  constructor(options = {}) {
    this.dryRun = options.dryRun || false;
    this.verbose = options.verbose || false;
    this.fileExtensions = options.fileExtensions || ['.py', '.js', '.jsx', '.ts', '.tsx', '.css', '.html'];
    this.changes = [];
    this.stats = {
      filesProcessed: 0,
      changesFound: 0,
      filesModified: 0,
    };
  }

  // Hauptverarbeitung
  async processDirectory(dirPath) {
    const files = this.getAllFiles(dirPath);
    
    for (const filePath of files) {
      await this.processFile(filePath);
    }
    
    return this.generateReport();
  }

  // Einzelne Datei verarbeiten
  async processFile(filePath) {
    const ext = path.extname(filePath);
    if (!this.fileExtensions.includes(ext)) {
      return;
    }

    this.stats.filesProcessed++;
    
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const newContent = this.transformContent(content, filePath);
      
      if (content !== newContent) {
        this.stats.filesModified++;
        
        if (!this.dryRun) {
          fs.writeFileSync(filePath, newContent, 'utf8');
        }
        
        if (this.verbose) {
          console.log(`✅ Modified: ${filePath}`);
        }
      }
    } catch (error) {
      console.error(`❌ Error processing ${filePath}:`, error.message);
    }
  }

  // Content Transformation
  transformContent(content, filePath) {
    let transformed = content;
    const ext = path.extname(filePath);
    
    // Python-spezifische Transformationen
    if (ext === '.py') {
      transformed = this.transformPython(transformed, filePath);
    }
    
    // JavaScript/TypeScript Transformationen
    if (['.js', '.jsx', '.ts', '.tsx'].includes(ext)) {
      transformed = this.transformJavaScript(transformed, filePath);
    }
    
    // CSS Transformationen
    if (ext === '.css') {
      transformed = this.transformCSS(transformed, filePath);
    }
    
    // HTML Transformationen
    if (ext === '.html') {
      transformed = this.transformHTML(transformed, filePath);
    }
    
    return transformed;
  }

  // Python get_typography() Transformationen
  transformPython(content, filePath) {
    return content.replace(PATTERNS.pythonGetTypography, (match, typographyName) => {
      const newName = TYPOGRAPHY_MAPPING[typographyName];
      if (newName && newName !== typographyName) {
        this.addChange(filePath, 'Python get_typography()', typographyName, newName, match);
        this.stats.changesFound++;
        return `get_typography('${newName}')`;
      }
      return match;
    });
  }

  // JavaScript/TypeScript Transformationen
  transformJavaScript(content, filePath) {
    let transformed = content;
    
    // fontSize Properties
    transformed = transformed.replace(PATTERNS.jsFontSize, (match, typographyName) => {
      const newName = TYPOGRAPHY_MAPPING[typographyName];
      if (newName && newName !== typographyName) {
        this.addChange(filePath, 'JS fontSize', typographyName, newName, match);
        this.stats.changesFound++;
        return `fontSize: '${newName}'`;
      }
      return match;
    });
    
    // React typography Props
    transformed = transformed.replace(PATTERNS.reactProps, (match, typographyName) => {
      const newName = TYPOGRAPHY_MAPPING[typographyName];
      if (newName && newName !== typographyName) {
        this.addChange(filePath, 'React typography prop', typographyName, newName, match);
        this.stats.changesFound++;
        return `typography="${newName}"`;
      }
      return match;
    });
    
    return transformed;
  }

  // CSS Transformationen
  transformCSS(content, filePath) {
    return content.replace(PATTERNS.cssClasses, (match, typographyName) => {
      const newName = TYPOGRAPHY_MAPPING[typographyName];
      if (newName && newName !== typographyName) {
        this.addChange(filePath, 'CSS class', typographyName, newName, match);
        this.stats.changesFound++;
        return `.ty-${newName}`;
      }
      return match;
    });
  }

  // HTML Transformationen
  transformHTML(content, filePath) {
    return content.replace(PATTERNS.htmlClasses, (match, classNames) => {
      let hasChanges = false;
      const newClassNames = classNames.replace(/\bty-([a-zA-Z_-]+)\b/g, (classMatch, typographyName) => {
        const newName = TYPOGRAPHY_MAPPING[typographyName];
        if (newName && newName !== typographyName) {
          this.addChange(filePath, 'HTML class', typographyName, newName, classMatch);
          this.stats.changesFound++;
          hasChanges = true;
          return `ty-${newName}`;
        }
        return classMatch;
      });
      
      return hasChanges ? match.replace(classNames, newClassNames) : match;
    });
  }

  // Change Tracking
  addChange(filePath, context, oldValue, newValue, fullMatch) {
    this.changes.push({
      file: filePath,
      context,
      old: oldValue,
      new: newValue,
      match: fullMatch,
      timestamp: new Date().toISOString(),
    });
  }

  // Alle Dateien aus Verzeichnis holen
  getAllFiles(dirPath) {
    const files = [];
    
    function scanDirectory(currentPath) {
      const items = fs.readdirSync(currentPath);
      
      for (const item of items) {
        const fullPath = path.join(currentPath, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          // Skip node_modules, .git, etc.
          if (!['node_modules', '.git', '.vscode', '__pycache__', 'dist', 'build'].includes(item)) {
            scanDirectory(fullPath);
          }
        } else {
          files.push(fullPath);
        }
      }
    }
    
    scanDirectory(dirPath);
    return files;
  }

  // Report generieren
  generateReport() {
    const report = {
      summary: {
        ...this.stats,
        mode: this.dryRun ? 'DRY RUN' : 'LIVE RUN',
        timestamp: new Date().toISOString(),
      },
      changes: this.changes,
      mapping: TYPOGRAPHY_MAPPING,
    };

    return report;
  }
}

// =============================================================================
// CLI INTERFACE
// =============================================================================

function printUsage() {
  console.log(`
📝 Typography Codemod - Translation Quality GUI

Usage:
  node typography-codemod.js <directory> [options]

Options:
  --dry-run          Run without making changes (default: false)
  --verbose          Show detailed output (default: false)
  --ext=.py,.js      File extensions to process (default: .py,.js,.jsx,.ts,.tsx,.css,.html)

Examples:
  node typography-codemod.js ./src --dry-run
  node typography-codemod.js ./src --verbose
  node typography-codemod.js ./src --ext=.py,.js
  
Mappings:
${Object.entries(TYPOGRAPHY_MAPPING).map(([old, new_]) => `  ${old} → ${new_}`).join('\n')}
`);
}

function printReport(report) {
  const { summary, changes } = report;
  
  console.log(`
🎯 Typography Codemod Report
${'='.repeat(50)}

📊 Summary:
  Mode: ${summary.mode}
  Files Processed: ${summary.filesProcessed}
  Files Modified: ${summary.filesModified}
  Changes Found: ${summary.changesFound}
  Timestamp: ${summary.timestamp}

📝 Changes by File:
`);

  const changesByFile = changes.reduce((acc, change) => {
    if (!acc[change.file]) {
      acc[change.file] = [];
    }
    acc[change.file].push(change);
    return acc;
  }, {});

  Object.entries(changesByFile).forEach(([filePath, fileChanges]) => {
    console.log(`\n  📄 ${path.basename(filePath)}`);
    fileChanges.forEach(change => {
      console.log(`    ${change.context}: ${change.old} → ${change.new}`);
    });
  });

  if (changes.length === 0) {
    console.log('  ✅ No changes needed - all typography is already up to date!');
  }

  console.log(`\n${'='.repeat(50)}`);
}

// =============================================================================
// MAIN EXECUTION
// =============================================================================

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    printUsage();
    return;
  }

  const directory = args[0];
  const options = {
    dryRun: args.includes('--dry-run'),
    verbose: args.includes('--verbose'),
  };

  // File extensions parsing
  const extArg = args.find(arg => arg.startsWith('--ext='));
  if (extArg) {
    options.fileExtensions = extArg.split('=')[1].split(',');
  }

  if (!fs.existsSync(directory)) {
    console.error(`❌ Directory does not exist: ${directory}`);
    process.exit(1);
  }

  console.log(`🚀 Starting Typography Codemod...`);
  console.log(`📁 Directory: ${directory}`);
  console.log(`🎯 Mode: ${options.dryRun ? 'DRY RUN' : 'LIVE RUN'}`);
  console.log(`📝 Extensions: ${options.fileExtensions?.join(', ') || 'default'}`);
  console.log('');

  try {
    const codemod = new TypographyCodemod(options);
    const report = await codemod.processDirectory(directory);
    
    printReport(report);
    
    // Save detailed report
    const reportPath = `typography-codemod-report-${Date.now()}.json`;
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`\n📋 Detailed report saved: ${reportPath}`);
    
  } catch (error) {
    console.error(`❌ Error during codemod execution:`, error.message);
    process.exit(1);
  }
}

// Nur ausführen wenn direkt aufgerufen
if (require.main === module) {
  main().catch(console.error);
}

module.exports = { TypographyCodemod, TYPOGRAPHY_MAPPING, PATTERNS };
