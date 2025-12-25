"""
Generate PDF from Eye Tracker Setup Guides
Preserves clickable links, high-quality images, and beautiful formatting.

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    1. Start the Flask server: python app.py
    2. Run this script: python generate_setup_pdfs.py
    3. PDFs will be saved to the 'pdf_exports' folder
"""

import asyncio
import os
from pathlib import Path
from datetime import datetime

async def generate_pdf(page, url, output_path, tab_selector=None):
    """Generate high-quality PDF from a webpage with clickable links"""
    await page.goto(url, wait_until='networkidle')
    
    # If a specific tab needs to be selected
    if tab_selector:
        await page.click(tab_selector)
        await page.wait_for_timeout(500)
    
    # Wait for all images to load
    await page.wait_for_timeout(1000)
    
    # Apply PDF-optimized styling
    await page.evaluate("""
        () => {
            // === HIDE NON-ESSENTIAL ELEMENTS ===
            const hideElements = [
                'nav', 'footer', 'header', '.et-hero', '.et-back-nav', 
                '.et-tabs', '.et-export-btn', '.navbar', '.site-footer'
            ];
            hideElements.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => el.style.display = 'none');
            });
            
            // Hide inactive tabs
            document.querySelectorAll('.et-tab-content:not(.active)').forEach(el => {
                el.style.display = 'none';
            });
            
            // Get the active tab
            const activeTab = document.querySelector('.et-tab-content.active');
            if (!activeTab) return;
            
            // Get title from data-title attribute
            const title = activeTab.getAttribute('data-title') || 'Setup Guide';
            
            // === REMOVE ALL HIDDEN/EMPTY ELEMENTS FIRST ===
            // Remove elements with display:none that take up space
            activeTab.querySelectorAll('[style*="display: none"], [style*="display:none"]').forEach(el => {
                el.remove();
            });
            
            // Remove empty divs and spacers
            activeTab.querySelectorAll('div, section').forEach(el => {
                if (el.children.length === 0 && el.textContent.trim() === '') {
                    el.remove();
                }
            });
            
            // === RESET ALL MARGINS AND PADDING ON TAB ===
            activeTab.style.paddingTop = '0';
            activeTab.style.marginTop = '0';
            activeTab.style.paddingBottom = '0';
            
            // === INJECT COMPACT PDF TITLE ===
            const existingTitle = activeTab.querySelector('.pdf-title-header');
            if (!existingTitle) {
                const titleEl = document.createElement('div');
                titleEl.className = 'pdf-title-header';
                titleEl.innerHTML = `
                    <h1 style="
                        text-align: center;
                        font-size: 22px;
                        font-weight: 700;
                        color: #0f172a;
                        margin: 0 0 10px 0;
                        padding: 10px 0 10px 0;
                        border-bottom: 3px solid #0077b6;
                        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
                    ">${title}</h1>
                `;
                activeTab.insertBefore(titleEl, activeTab.firstChild);
            }
            
            // === REMOVE DUPLICATE SECTION HEADERS ===
            activeTab.querySelectorAll('.et-section-header').forEach((header, index) => {
                const h2 = header.querySelector('h2');
                if (h2) {
                    const text = h2.textContent.toLowerCase();
                    if (text.includes('tobii eye tracker 5') || text.includes('tobii eye tracker 4c') || 
                        text.includes('optikey setup') || text.includes('windows eye control setup')) {
                        header.remove();
                    }
                }
            });
            
            // === AGGRESSIVELY REMOVE EMPTY SPACE ===
            // Remove ALL excessive margins on first children - go deeper
            const firstSection = activeTab.querySelector('.et-section, section');
            if (firstSection) {
                firstSection.style.marginTop = '0';
                firstSection.style.paddingTop = '0';
                firstSection.style.marginBottom = '5px';
                
                // Fix ALL children of first section
                firstSection.querySelectorAll('*').forEach((el, idx) => {
                    if (idx < 20) { // First 20 elements to avoid being too slow
                        const style = window.getComputedStyle(el);
                        if (parseInt(style.marginTop) > 15) {
                            el.style.marginTop = '5px';
                        }
                        if (parseInt(style.paddingTop) > 15) {
                            el.style.paddingTop = '5px';
                        }
                    }
                });
            }
            
            // === COMPACT ALL INTRO BOXES ===
            // Make all info/context boxes more compact
            activeTab.querySelectorAll('div[style*="background"]').forEach(box => {
                box.style.marginTop = '5px';
                box.style.marginBottom = '5px';
                box.style.padding = '8px 12px';
            });
            
            // === COMPACT QUICK STEPS OVERVIEW ===
            // This box is particularly large in 4C
            activeTab.querySelectorAll('div[style*="linear-gradient"]').forEach(box => {
                box.style.marginTop = '5px';
                box.style.marginBottom = '5px';
                box.style.padding = '10px 15px';
            });
            
            // === COMPACT et-section-desc paragraphs ===
            activeTab.querySelectorAll('.et-section-desc, p[class*="desc"]').forEach(p => {
                p.style.marginTop = '0';
                p.style.marginBottom = '5px';
            });
            
            // === COMPACT WARNING/INFO BOXES ===
            activeTab.querySelectorAll('p[style*="background"]').forEach(p => {
                p.style.marginTop = '3px';
                p.style.marginBottom = '3px';
                p.style.padding = '6px 10px';
            });
            
            // === COMPACT ALL SECTIONS ===
            activeTab.querySelectorAll('.et-section, section').forEach((section, index) => {
                section.style.marginTop = index === 0 ? '0' : '10px';
                section.style.paddingTop = '0';
                section.style.marginBottom = '5px';
            });
            
            // === STYLE SECTION HEADERS ===
            activeTab.querySelectorAll('.et-section-header h2').forEach(h2 => {
                h2.style.fontSize = '16px';
                h2.style.fontWeight = '600';
                h2.style.color = '#1e40af';
                h2.style.borderBottom = '2px solid #e2e8f0';
                h2.style.paddingBottom = '8px';
                h2.style.marginBottom = '15px';
            });
            
            // === STYLE STEPS WITH CARD DESIGN ===
            activeTab.querySelectorAll('.et-step').forEach(step => {
                step.style.marginBottom = '20px';
                step.style.padding = '15px';
                step.style.background = '#f8fafc';
                step.style.border = '1px solid #e2e8f0';
                step.style.borderLeft = '4px solid #0077b6';
                step.style.borderRadius = '8px';
                step.style.pageBreakInside = 'avoid';
            });
            
            // === STYLE STEP NUMBERS ===
            activeTab.querySelectorAll('.et-step-num').forEach(num => {
                num.style.width = '28px';
                num.style.height = '28px';
                num.style.background = '#0077b6';
                num.style.color = 'white';
                num.style.borderRadius = '50%';
                num.style.display = 'flex';
                num.style.alignItems = 'center';
                num.style.justifyContent = 'center';
                num.style.fontSize = '14px';
                num.style.fontWeight = '700';
                num.style.flexShrink = '0';
            });
            
            // === STYLE STEP TITLES ===
            activeTab.querySelectorAll('.et-step-title').forEach(title => {
                title.style.fontSize = '15px';
                title.style.fontWeight = '600';
                title.style.color = '#1e293b';
                title.style.margin = '0';
            });
            
            // === STYLE STEP CONTENT ===
            activeTab.querySelectorAll('.et-step-content').forEach(content => {
                content.style.paddingLeft = '40px';
                content.style.fontSize = '12px';
                content.style.lineHeight = '1.6';
            });
            
            // === LARGE, HIGH-QUALITY IMAGES ===
            activeTab.querySelectorAll('.et-step-image img, .et-image-item img, img[onclick]').forEach(img => {
                // Remove any size constraints for full quality
                img.style.maxWidth = '95%';
                img.style.width = 'auto';
                img.style.height = 'auto';
                img.style.border = '2px solid #e2e8f0';
                img.style.borderRadius = '8px';
                img.style.display = 'block';
                img.style.margin = '20px auto';
                img.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                // Force load at full resolution
                img.removeAttribute('loading');
            });
            
            // === CENTER IMAGE CONTAINERS ===
            activeTab.querySelectorAll('.et-step-image, .et-image-item').forEach(container => {
                container.style.textAlign = 'center';
                container.style.margin = '15px 0';
                container.style.pageBreakInside = 'avoid';
            });
            
            // === STYLE IMAGE CAPTIONS ===
            activeTab.querySelectorAll('.et-step-image p, .et-image-item p').forEach(caption => {
                caption.style.fontSize = '10px';
                caption.style.fontStyle = 'italic';
                caption.style.color = '#64748b';
                caption.style.marginTop = '8px';
                caption.style.textAlign = 'center';
            });
            
            // === STYLE LINKS - Ensure they're clickable ===
            activeTab.querySelectorAll('a[href]').forEach(link => {
                link.style.color = '#0077b6';
                link.style.textDecoration = 'underline';
                link.style.fontWeight = '500';
                // Keep href for clickability - Playwright preserves these
            });
            
            // === STYLE ALERT BOXES ===
            activeTab.querySelectorAll('.et-alert').forEach(alert => {
                alert.style.padding = '12px 15px';
                alert.style.margin = '15px 0';
                alert.style.fontSize = '11px';
                alert.style.borderRadius = '6px';
                alert.style.pageBreakInside = 'avoid';
            });
            
            activeTab.querySelectorAll('.et-alert-info').forEach(alert => {
                alert.style.background = '#eff6ff';
                alert.style.border = '1px solid #bfdbfe';
                alert.style.borderLeft = '4px solid #3b82f6';
            });
            
            activeTab.querySelectorAll('.et-alert-warning').forEach(alert => {
                alert.style.background = '#fffbeb';
                alert.style.border = '1px solid #fde68a';
                alert.style.borderLeft = '4px solid #f59e0b';
            });
            
            activeTab.querySelectorAll('.et-alert-danger').forEach(alert => {
                alert.style.background = '#fef2f2';
                alert.style.border = '1px solid #fecaca';
                alert.style.borderLeft = '4px solid #ef4444';
            });
            
            // === STYLE INFO BOXES ===
            activeTab.querySelectorAll('div[style*="background: #f8f6f1"], div[style*="background: linear-gradient"]').forEach(box => {
                box.style.background = '#f8fafc';
                box.style.padding = '15px';
                box.style.margin = '15px 0';
                box.style.border = '1px solid #e2e8f0';
                box.style.borderRadius = '8px';
            });
            
            // === STYLE CODE ELEMENTS ===
            activeTab.querySelectorAll('code').forEach(code => {
                code.style.background = '#f1f5f9';
                code.style.padding = '2px 6px';
                code.style.borderRadius = '4px';
                code.style.fontFamily = 'Consolas, Monaco, monospace';
                code.style.fontSize = '11px';
            });
            
            // === HIDE SETUP GUIDE HEADER (redundant) ===
            activeTab.querySelectorAll('.et-setup-guide-header').forEach(header => {
                header.style.display = 'none';
            });
            
            // === REMOVE EXCESS MARGINS ===
            activeTab.style.paddingTop = '0';
            activeTab.style.marginTop = '0';
            
            // === SET BASE FONT ===
            activeTab.style.fontFamily = "'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif";
            activeTab.style.fontSize = '12px';
            activeTab.style.lineHeight = '1.6';
            activeTab.style.color = '#1e293b';
        }
    """)
    
    # Generate high-quality PDF
    await page.pdf(
        path=output_path,
        format='A4',
        print_background=True,
        display_header_footer=False,
        prefer_css_page_size=False,
        margin={
            'top': '20mm',
            'bottom': '20mm',
            'left': '15mm',
            'right': '15mm'
        },
        scale=1.0  # Full scale for best image quality
    )
    
    print(f"✅ Generated: {output_path}")

async def main():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Playwright not installed!")
        print("   Run: pip install playwright")
        print("   Then: playwright install chromium")
        return
    
    # Create output directory
    output_dir = Path("pdf_exports")
    output_dir.mkdir(exist_ok=True)
    
    base_url = "http://localhost:5000"
    
    # Define guides to generate
    guides = [
        {
            "name": "Tobii_Eye_Tracker_5_OptiKey_Setup_Guide",
            "url": f"{base_url}/eye-tracker-setup?tab=tobii5-optikey",
            "tab_selector": None
        },
        {
            "name": "Tobii_Eye_Tracker_5_Windows_Eye_Control_Setup_Guide",
            "url": f"{base_url}/eye-tracker-setup?tab=tobii5-winec",
            "tab_selector": None
        },
        {
            "name": "Tobii_Eye_Tracker_4C_Setup_Guide",
            "url": f"{base_url}/eye-tracker-setup?tab=tobii4c",
            "tab_selector": None
        }
    ]
    
    print("\n📄 Eye Tracker Setup PDF Generator (High Quality)")
    print("=" * 55)
    print("Features: Clickable links | Large images | Beautiful design")
    print("Make sure Flask server is running: python app.py\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # Use large viewport with high DPI for crisp images
        page = await browser.new_page(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2  # Retina-quality rendering
        )
        
        for guide in guides:
            output_path = str(output_dir / f"{guide['name']}.pdf")
            
            try:
                await generate_pdf(
                    page, 
                    guide['url'], 
                    output_path,
                    guide.get('tab_selector')
                )
            except Exception as e:
                print(f"❌ Error generating {guide['name']}: {e}")
        
        await browser.close()
    
    print("\n" + "=" * 55)
    print(f"📁 PDFs saved to: {output_dir.absolute()}")
    print("\n✨ Features in generated PDFs:")
    print("   • Clickable links (open in browser)")
    print("   • High-quality, large images")
    print("   • Beautiful card-style steps")
    print("   • No duplicate headers")
    print("   • Professional formatting")

if __name__ == "__main__":
    asyncio.run(main())
