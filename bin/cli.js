#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// ─────────────────────────────────────────────
//  fire-flow installer for Claude Code
// ─────────────────────────────────────────────

const PLUGIN_NAME = 'fire-flow';
const VERSION = require('../package.json').version;

// Colors for terminal output
const cyan = (s) => `\x1b[36m${s}\x1b[0m`;
const green = (s) => `\x1b[32m${s}\x1b[0m`;
const red = (s) => `\x1b[31m${s}\x1b[0m`;
const yellow = (s) => `\x1b[33m${s}\x1b[0m`;
const bold = (s) => `\x1b[1m${s}\x1b[0m`;
const dim = (s) => `\x1b[2m${s}\x1b[0m`;

function banner() {
  console.log('');
  console.log(cyan('  ╔══════════════════════════════════════════╗'));
  console.log(cyan('  ║') + bold('     🔥 fire-flow installer              ') + cyan('║'));
  console.log(cyan('  ║') + dim(`     v${VERSION} — Workflow Orchestration   `) + cyan('║'));
  console.log(cyan('  ╚══════════════════════════════════════════╝'));
  console.log('');
}

function getPluginsDir() {
  const home = process.env.HOME || process.env.USERPROFILE;
  if (!home) {
    console.error(red('Could not determine home directory.'));
    process.exit(1);
  }
  return path.join(home, '.claude', 'plugins');
}

function copyRecursive(src, dest) {
  if (!fs.existsSync(src)) return;

  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    for (const item of fs.readdirSync(src)) {
      // Skip files that shouldn't be installed
      if (item === '.git' || item === 'node_modules' || item === 'bin' || item === 'package.json' || item === 'package-lock.json' || item === '.npmignore') continue;
      copyRecursive(path.join(src, item), path.join(dest, item));
    }
  } else {
    fs.copyFileSync(src, dest);
  }
}

function countFiles(dir, ext) {
  let count = 0;
  if (!fs.existsSync(dir)) return 0;
  for (const item of fs.readdirSync(dir, { recursive: true })) {
    if (item.endsWith(ext)) count++;
  }
  return count;
}

function install() {
  banner();

  const args = process.argv.slice(2);

  // Handle --help
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`  ${bold('Usage:')} npx fire-flow [options]`);
    console.log('');
    console.log(`  ${bold('Options:')}`);
    console.log(`    --help, -h       Show this help message`);
    console.log(`    --version, -v    Show version`);
    console.log(`    --uninstall      Remove fire-flow plugin`);
    console.log(`    --update         Update existing installation`);
    console.log(`    --path <dir>     Install to custom directory`);
    console.log('');
    console.log(`  ${bold('Default install path:')}`);
    console.log(`    ~/.claude/plugins/${PLUGIN_NAME}/`);
    console.log('');
    console.log(`  ${dim('GitHub: https://github.com/ThierryN/fire-flow')}`);
    process.exit(0);
  }

  // Handle --version
  if (args.includes('--version') || args.includes('-v')) {
    console.log(`  fire-flow v${VERSION}`);
    process.exit(0);
  }

  // Determine install path
  let installDir;
  const pathIdx = args.indexOf('--path');
  if (pathIdx !== -1 && args[pathIdx + 1]) {
    installDir = path.resolve(args[pathIdx + 1]);
  } else {
    installDir = path.join(getPluginsDir(), PLUGIN_NAME);
  }

  // Handle --uninstall
  if (args.includes('--uninstall')) {
    if (fs.existsSync(installDir)) {
      console.log(`  Removing ${yellow(installDir)}...`);
      fs.rmSync(installDir, { recursive: true, force: true });
      console.log(green('  fire-flow has been uninstalled.'));
    } else {
      console.log(yellow('  fire-flow is not installed at ' + installDir));
    }
    process.exit(0);
  }

  // Check for existing installation
  const isUpdate = args.includes('--update');
  if (fs.existsSync(installDir) && !isUpdate) {
    console.log(yellow(`  fire-flow is already installed at:`));
    console.log(`  ${installDir}`);
    console.log('');
    console.log(`  Run ${cyan('npx fire-flow --update')} to update.`);
    console.log(`  Run ${cyan('npx fire-flow --uninstall')} to remove.`);
    process.exit(0);
  }

  // Source directory (the npm package root, one level up from bin/)
  const srcDir = path.join(__dirname, '..');

  console.log(`  Installing to: ${cyan(installDir)}`);
  console.log('');

  // Create plugins directory if needed
  const pluginsDir = path.dirname(installDir);
  fs.mkdirSync(pluginsDir, { recursive: true });

  // Copy plugin files
  const filesToCopy = [
    'agents',
    'commands',
    'hooks',
    'skills-library',
    'templates',
    'references',
    'workflows',
    '.claude-plugin',
    'plugin.json',
    'validation-config.yml',
    'version.json',
    'README.md',
    'QUICK-START.md',
    'COMMAND-REFERENCE.md',
    'DOMINION-FLOW-OVERVIEW.md',
    'ARCHITECTURE-DIAGRAM.md',
    'TROUBLESHOOTING.md',
  ];

  let copiedDirs = 0;
  let copiedFiles = 0;

  for (const item of filesToCopy) {
    const src = path.join(srcDir, item);
    const dest = path.join(installDir, item);

    if (!fs.existsSync(src)) {
      continue;
    }

    const stat = fs.statSync(src);
    if (stat.isDirectory()) {
      copyRecursive(src, dest);
      copiedDirs++;
      console.log(`  ${green('+')} ${item}/`);
    } else {
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      fs.copyFileSync(src, dest);
      copiedFiles++;
      console.log(`  ${green('+')} ${item}`);
    }
  }

  // Count what was installed
  const cmdCount = countFiles(path.join(installDir, 'commands'), '.md');
  const agentCount = countFiles(path.join(installDir, 'agents'), '.md');
  const skillCount = countFiles(path.join(installDir, 'skills-library'), '.md');

  console.log('');
  console.log(green('  Installation complete!'));
  console.log('');
  console.log(`  ${bold('Installed:')}`);
  console.log(`    ${cyan(cmdCount)} commands`);
  console.log(`    ${cyan(agentCount)} agents`);
  console.log(`    ${cyan(skillCount)} skills`);
  console.log('');
  console.log(`  ${bold('Location:')}`);
  console.log(`    ${installDir}`);
  console.log('');
  console.log(`  ${bold('Quick start:')}`);
  console.log(`    1. Open Claude Code in any project`);
  console.log(`    2. Type ${cyan('/fire-0-orient')} to orient on your project`);
  console.log(`    3. Type ${cyan('/fire-1-new')} to start a new project workflow`);
  console.log(`    4. Type ${cyan('/fire-debug')} when you hit a bug`);
  console.log('');
  console.log(`  ${bold('Docs:')} ${dim('https://github.com/ThierryN/fire-flow')}`);
  console.log(`  ${bold('Help:')} ${dim('/fire-dashboard for full command overview')}`);
  console.log('');
}

install();
