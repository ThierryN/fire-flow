#!/usr/bin/env node
/**
 * Export Excalidraw diagrams to PNG using Playwright.
 * Uses Excalidraw's native "Copy to clipboard" for high-quality rendering.
 *
 * Usage:
 *   node export_playwright.js input.excalidraw [output.png]
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function exportDiagram(inputPath, outputPath) {
    const absoluteInput = path.resolve(inputPath);
    if (!fs.existsSync(absoluteInput)) {
        console.error(`Input file not found: ${absoluteInput}`);
        process.exit(1);
    }

    const diagramData = fs.readFileSync(absoluteInput, 'utf-8');
    const diagram = JSON.parse(diagramData);
    const absoluteOutput = path.resolve(outputPath || inputPath.replace(/\.excalidraw$/, '.png'));

    console.log(`Exporting: ${absoluteInput}`);
    console.log(`Output: ${absoluteOutput}`);

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 1920, height: 1200 },
        permissions: ['clipboard-read', 'clipboard-write'],
    });
    const page = await context.newPage();

    // Accept any dialogs
    page.on('dialog', dialog => dialog.accept());

    let exportSuccess = false;

    try {
        await page.goto('https://excalidraw.com/', { waitUntil: 'networkidle' });
        await page.waitForSelector('.excalidraw', { timeout: 30000 });
        await page.waitForTimeout(1500);

        // Load diagram via file drop
        const fileContent = JSON.stringify(diagram);
        await page.evaluate(async (content) => {
            const blob = new Blob([content], { type: 'application/json' });
            const file = new File([blob], 'diagram.excalidraw', { type: 'application/json' });
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            document.querySelector('.excalidraw')?.dispatchEvent(
                new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer })
            );
        }, fileContent);

        await page.waitForTimeout(2000);

        // Select all elements
        await page.keyboard.press('Control+a');
        await page.waitForTimeout(300);

        // Open menu (hamburger icon in top left)
        console.log('Opening menu...');
        const menuButton = await page.$('.App-menu button')
            || await page.$('button[aria-label="Main menu"]')
            || await page.$('.dropdown-menu-button');

        if (menuButton) {
            await menuButton.click();
        } else {
            await page.click('.excalidraw', { position: { x: 25, y: 25 } });
        }
        await page.waitForTimeout(500);

        // Click "Export image..."
        console.log('Opening export dialog...');
        const exportOption = await page.$('text="Export image..."')
            || await page.$('text="Export image"')
            || await page.$('[data-testid="dropdown-menu-export"]');

        if (exportOption) {
            await exportOption.click();
        } else {
            await page.keyboard.press('Meta+Shift+e');
        }
        await page.waitForTimeout(1500);

        // Verify export dialog opened
        const copyBtn = await page.$('button:has-text("Copy to clipboard")');
        if (!copyBtn) {
            throw new Error('Export dialog did not open');
        }
        console.log('Export dialog opened');

        // Click "Copy to clipboard" for high-quality PNG export
        console.log('Copying to clipboard...');
        await copyBtn.click();

        // Wait for the copy to complete - look for success toast or just wait longer
        await page.waitForTimeout(2000);

        // Read PNG from clipboard
        const pngData = await page.evaluate(async () => {
            try {
                const items = await navigator.clipboard.read();
                for (const item of items) {
                    if (item.types.includes('image/png')) {
                        const blob = await item.getType('image/png');
                        const arrayBuffer = await blob.arrayBuffer();
                        // Convert to base64
                        const bytes = new Uint8Array(arrayBuffer);
                        let binary = '';
                        for (let i = 0; i < bytes.length; i++) {
                            binary += String.fromCharCode(bytes[i]);
                        }
                        return btoa(binary);
                    }
                }
                return null;
            } catch (e) {
                console.error('Clipboard read failed:', e.message);
                return null;
            }
        });

        if (pngData && pngData.length > 100) {  // Validate we got actual image data
            const buffer = Buffer.from(pngData, 'base64');
            // Verify it's a valid PNG (starts with PNG signature)
            if (buffer[0] === 0x89 && buffer[1] === 0x50 && buffer[2] === 0x4E && buffer[3] === 0x47) {
                fs.writeFileSync(absoluteOutput, buffer);
                console.log(`Exported: ${absoluteOutput} (${buffer.length} bytes)`);
                exportSuccess = true;
            } else {
                console.error('Clipboard data is not a valid PNG');
            }
        } else {
            console.error('No PNG data in clipboard or data too small');
        }

    } catch (error) {
        console.error('Export failed:', error.message);
    }

    // Fallback if clipboard export didn't work
    if (!exportSuccess) {
        console.log('Falling back to canvas screenshot...');

        try {
            // IMPORTANT: Close any dialogs first
            await page.keyboard.press('Escape');
            await page.waitForTimeout(500);
            await page.keyboard.press('Escape');  // Press twice to be sure
            await page.waitForTimeout(500);

            // Click somewhere on canvas to ensure focus and dismiss any overlays
            await page.click('.excalidraw', { position: { x: 960, y: 600 } });
            await page.waitForTimeout(300);

            // Fit view to content (Shift+1)
            await page.keyboard.press('Shift+1');
            await page.waitForTimeout(1000);

            // Take debug screenshot to verify dialog is closed
            await page.screenshot({ path: '/tmp/excalidraw_pre_export.png' });

            // Get the canvas element
            const canvas = await page.$('canvas');
            if (canvas) {
                // Get canvas bounding box
                const box = await canvas.boundingBox();
                if (box) {
                    // Screenshot just the canvas area
                    await page.screenshot({
                        path: absoluteOutput,
                        clip: {
                            x: box.x,
                            y: box.y,
                            width: box.width,
                            height: box.height
                        }
                    });
                    console.log(`Fallback export (canvas clip): ${absoluteOutput}`);
                    exportSuccess = true;
                }
            }

            if (!exportSuccess) {
                // Last resort: full page but should have no dialog
                await page.screenshot({ path: absoluteOutput });
                console.log(`Fallback export (full page): ${absoluteOutput}`);
            }
        } catch (fallbackError) {
            console.error('Fallback failed:', fallbackError.message);
            await page.screenshot({ path: absoluteOutput });
        }
    }

    await browser.close();
    return absoluteOutput;
}

// CLI entry point
const args = process.argv.slice(2);
if (args.length < 1) {
    console.log('Usage: node export_playwright.js <input.excalidraw> [output.png]');
    process.exit(1);
}

exportDiagram(args[0], args[1])
    .then(output => {
        console.log('Done!');
        process.exit(0);
    })
    .catch(err => {
        console.error(err);
        process.exit(1);
    });
