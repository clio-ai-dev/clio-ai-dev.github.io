#!/usr/bin/env python3
"""Build playbook HTML with embedded base64 images, then render to PDF."""

import base64, re, os, subprocess, sys
from pathlib import Path

BASE = Path("/home/azureuser/.openclaw/workspace/clio-business/agentic-developer")
IMAGES_DIR = BASE / "images"

# Read all needed images and encode to base64
image_files = [
    "img-01-01.jpg", "img-01-05.jpg", "img-01-09.jpg",
    "img-02-01.jpg", "img-02-02.jpg",
    "img-03-01.jpg", "img-03-02.jpg",
    "img-06-01.jpg", "img-06-02.jpg", "img-06-03.jpg",
    "img-13-01.jpg", "img-13-02.jpg",
]

images_b64 = {}
for f in image_files:
    p = IMAGES_DIR / f
    if p.exists():
        with open(p, "rb") as fh:
            images_b64[f] = base64.b64encode(fh.read()).decode()
        print(f"  Encoded {f} ({p.stat().st_size // 1024}KB)")
    else:
        print(f"  WARNING: {f} not found!")

def img_tag(filename, alt=""):
    if filename in images_b64:
        return f'<div class="figure"><img src="data:image/jpeg;base64,{images_b64[filename]}" alt="{alt}"><p class="figure-caption">{alt}</p></div>'
    return f'<!-- IMAGE NOT FOUND: {filename} -->'

# Read chapter markdown files
chapters_dir = BASE / "chapters"
ch_files = [
    "00-front-matter.md",
    "01-software-development-has-changed.md",
    "02-the-metr-paradox.md",
    "03-your-new-job-description.md",
    "04-writing-effective-context-files.md",
    "05-the-tdd-agent-loop.md",
    "06-back-matter.md",
]

chapters = {}
for f in ch_files:
    p = chapters_dir / f
    if p.exists():
        chapters[f] = p.read_text()
    else:
        print(f"  WARNING: {f} not found!")

def md_to_html(md_text):
    """Simple markdown to HTML conversion for the playbook content."""
    lines = md_text.split('\n')
    html_parts = []
    in_code_block = False
    code_lang = ""
    code_lines = []
    in_list = False
    list_type = None  # 'ul' or 'ol'
    in_table = False
    table_lines = []
    
    def close_list():
        nonlocal in_list, list_type
        if in_list:
            html_parts.append(f'</{list_type}>')
            in_list = False
            list_type = None
    
    def close_table():
        nonlocal in_table, table_lines
        if in_table:
            # Parse table
            rows = [r.strip() for r in table_lines if r.strip()]
            if len(rows) >= 2:
                html_parts.append('<table>')
                # Header
                cells = [c.strip() for c in rows[0].split('|') if c.strip()]
                html_parts.append('<thead><tr>')
                for c in cells:
                    html_parts.append(f'<th>{inline_format(c)}</th>')
                html_parts.append('</tr></thead>')
                # Body (skip separator row)
                html_parts.append('<tbody>')
                for row in rows[2:]:
                    cells = [c.strip() for c in row.split('|') if c.strip()]
                    html_parts.append('<tr>')
                    for c in cells:
                        html_parts.append(f'<td>{inline_format(c)}</td>')
                    html_parts.append('</tr>')
                html_parts.append('</tbody></table>')
            in_table = False
            table_lines = []
    
    def inline_format(text):
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        # Inline code
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        return text
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                close_list()
                html_parts.append(f'<pre><code>{chr(10).join(code_lines)}</code></pre>')
                in_code_block = False
                code_lines = []
                i += 1
                continue
            else:
                close_list()
                close_table()
                in_code_block = True
                code_lang = line.strip()[3:]
                code_lines = []
                i += 1
                continue
        
        if in_code_block:
            # Escape HTML in code
            escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            code_lines.append(escaped)
            i += 1
            continue
        
        stripped = line.strip()
        
        # Empty line
        if not stripped:
            close_list()
            close_table()
            i += 1
            continue
        
        # Table detection
        if '|' in stripped and stripped.startswith('|'):
            if not in_table:
                close_list()
                in_table = True
                table_lines = []
            table_lines.append(stripped)
            i += 1
            continue
        elif in_table:
            close_table()
        
        # Image
        img_match = re.match(r'!\[img-(\d+)-(\d+):\s*(.+?)\]\(.*?img-(\d+)-(\d+)\.jpg\)', stripped)
        if img_match:
            close_list()
            ch_num = img_match.group(1)
            img_num = img_match.group(2)
            alt = img_match.group(3)
            filename = f"img-{ch_num}-{img_num}.jpg"
            html_parts.append(img_tag(filename, alt))
            i += 1
            continue
        
        # Headers
        if stripped.startswith('### '):
            close_list()
            html_parts.append(f'<h3>{inline_format(stripped[4:])}</h3>')
            i += 1
            continue
        if stripped.startswith('## '):
            close_list()
            html_parts.append(f'<h2>{inline_format(stripped[3:])}</h2>')
            i += 1
            continue
        if stripped.startswith('# '):
            close_list()
            # Skip chapter title headers (handled by chapter-header div)
            i += 1
            continue
        
        # Horizontal rule
        if stripped == '---':
            close_list()
            html_parts.append('<hr>')
            i += 1
            continue
        
        # Blockquote
        if stripped.startswith('> '):
            close_list()
            quote_text = inline_format(stripped[2:])
            html_parts.append(f'<blockquote><p>{quote_text}</p></blockquote>')
            i += 1
            continue
        
        # Unordered list
        if stripped.startswith('- '):
            if not in_list or list_type != 'ul':
                close_list()
                html_parts.append('<ul>')
                in_list = True
                list_type = 'ul'
            html_parts.append(f'<li>{inline_format(stripped[2:])}</li>')
            i += 1
            continue
        
        # Ordered list
        ol_match = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if ol_match:
            if not in_list or list_type != 'ol':
                close_list()
                html_parts.append('<ol>')
                in_list = True
                list_type = 'ol'
            html_parts.append(f'<li>{inline_format(ol_match.group(2))}</li>')
            i += 1
            continue
        
        # Regular paragraph
        close_list()
        html_parts.append(f'<p>{inline_format(stripped)}</p>')
        i += 1
    
    close_list()
    close_table()
    
    return '\n'.join(html_parts)


def convert_chapter(md_text, skip_title=False):
    """Convert chapter markdown, optionally skipping the first # heading."""
    if skip_title:
        # Remove first line if it's a # heading
        lines = md_text.split('\n')
        start = 0
        for idx, line in enumerate(lines):
            if line.strip().startswith('# '):
                start = idx + 1
                break
        md_text = '\n'.join(lines[start:])
    return md_to_html(md_text)


# Now build the full HTML
print("Building HTML...")

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Agentic Developer - Free Playbook</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&family=JetBrains+Mono:wght@400;500&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        @page {{
            size: 8.5in 11in;
            margin: 1in;
            margin-left: 1.2in;
            @bottom-center {{
                content: counter(page);
                font-family: 'Inter', sans-serif;
                font-size: 10pt;
                color: #999;
            }}
        }}

        @page :first {{
            @bottom-center {{
                content: '';
            }}
        }}

        html {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #1a1a2e;
            background: white;
        }}

        body {{
            padding: 0;
            margin: 0;
        }}

        h1 {{
            font-size: 32pt;
            font-weight: 900;
            margin: 0.5em 0 0.3em 0;
            color: #1a1a2e;
            line-height: 1.2;
        }}

        h2 {{
            font-size: 24pt;
            font-weight: 700;
            margin: 1.5em 0 0.8em 0;
            color: #1a1a2e;
            line-height: 1.3;
            page-break-after: avoid;
        }}

        h3 {{
            font-size: 14pt;
            font-weight: 600;
            margin: 1.2em 0 0.6em 0;
            color: #1a1a2e;
            page-break-after: avoid;
        }}

        h4 {{
            font-size: 12pt;
            font-weight: 600;
            margin: 0.8em 0 0.4em 0;
            color: #1a1a2e;
        }}

        p {{
            margin: 0 0 1em 0;
            line-height: 1.65;
        }}

        strong {{
            font-weight: 600;
            color: #1a1a2e;
        }}

        em {{
            font-style: italic;
        }}

        a {{
            color: #6366f1;
            text-decoration: none;
        }}

        .cover {{
            page-break-after: always;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            text-align: center;
            background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
            padding: 4em 2em;
        }}

        .cover h1 {{
            font-size: 48pt;
            margin-bottom: 0.2em;
            color: #1a1a2e;
        }}

        .cover .subtitle {{
            font-size: 22pt;
            font-weight: 500;
            color: #6366f1;
            margin-bottom: 1em;
        }}

        .cover .badge {{
            display: inline-block;
            background: #6366f1;
            color: white;
            padding: 0.3em 0.8em;
            border-radius: 20px;
            font-size: 11pt;
            font-weight: 600;
            margin-bottom: 2em;
            letter-spacing: 0.05em;
        }}

        .cover .author {{
            font-size: 14pt;
            color: #666;
            margin-top: 2em;
        }}

        .chapter {{
            page-break-before: always;
            margin-bottom: 3em;
        }}

        .chapter-header {{
            margin-bottom: 2em;
            padding-bottom: 1.5em;
            border-bottom: 2px solid #eee;
        }}

        .chapter-number {{
            font-size: 12pt;
            font-weight: 600;
            color: #6366f1;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.3em;
        }}

        .chapter-title {{
            font-size: 28pt;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 0.5em;
        }}

        .chapter-subtitle {{
            font-size: 14pt;
            color: #666;
            font-style: italic;
        }}

        code {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 9.5pt;
            background: #f8fafc;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            color: #d946ef;
        }}

        pre {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 1em;
            margin: 1em 0;
            overflow-x: auto;
            break-inside: avoid;
        }}

        pre code {{
            background: none;
            padding: 0;
            color: #1a1a2e;
            font-size: 9pt;
            line-height: 1.5;
        }}

        .callout {{
            background: #eef2ff;
            border-left: 4px solid #6366f1;
            padding: 1em;
            margin: 1.5em 0;
            border-radius: 4px;
            break-inside: avoid;
        }}

        .callout.tip {{
            border-left-color: #6366f1;
            background: #eef2ff;
        }}

        .callout.warning {{
            border-left-color: #f59e0b;
            background: #fffbeb;
        }}

        .callout.key {{
            border-left-color: #10b981;
            background: #f0fdf4;
        }}

        .callout strong {{
            color: #1a1a2e;
        }}

        blockquote {{
            border-left: 4px solid #6366f1;
            padding-left: 1em;
            margin: 1.5em 0;
            color: #666;
            font-style: italic;
        }}

        ul, ol {{
            margin: 1em 0 1em 1.5em;
        }}

        li {{
            margin-bottom: 0.5em;
            line-height: 1.65;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5em 0;
            break-inside: avoid;
        }}

        th {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 0.7em;
            text-align: left;
            font-weight: 600;
            color: #1a1a2e;
        }}

        td {{
            border: 1px solid #e2e8f0;
            padding: 0.7em;
            color: #1a1a2e;
        }}

        tr:nth-child(even) {{
            background: #f8fafc;
        }}

        .toc {{
            page-break-after: always;
        }}

        .toc h2 {{
            margin-bottom: 1.5em;
        }}

        .back-matter {{
            page-break-before: always;
        }}

        .feature-list {{
            margin: 1.5em 0;
        }}

        .feature-item {{
            margin-bottom: 1.5em;
            padding-bottom: 1.5em;
            border-bottom: 1px solid #eee;
        }}

        .feature-item:last-child {{
            border-bottom: none;
        }}

        .feature-item h3 {{
            margin-top: 0;
            color: #6366f1;
        }}

        .cta-box {{
            background: linear-gradient(135deg, #6366f1 0%, #0ea5e9 100%);
            color: white;
            padding: 2em;
            border-radius: 8px;
            margin: 2em 0;
            text-align: center;
            break-inside: avoid;
        }}

        .cta-box h2 {{
            color: white;
            margin-top: 0;
        }}

        .cta-box p {{
            color: rgba(255, 255, 255, 0.95);
            font-size: 13pt;
        }}

        hr {{
            border: none;
            border-top: 1px solid #eee;
            margin: 2em 0;
        }}

        .intro {{
            font-size: 12pt;
            line-height: 1.7;
            color: #333;
        }}

        .note {{
            background: #fffbeb;
            border-left: 4px solid #f59e0b;
            padding: 1em;
            margin: 1.5em 0;
            border-radius: 4px;
            break-inside: avoid;
        }}

        .note strong {{
            color: #92400e;
        }}

        .author-section {{
            background: #f8fafc;
            padding: 1.5em;
            border-radius: 6px;
            margin: 2em 0;
            break-inside: avoid;
        }}

        .author-section h3 {{
            color: #6366f1;
            margin-top: 0;
        }}

        .figure {{
            text-align: center;
            margin: 1.5em 0;
            break-inside: avoid;
        }}

        .figure img {{
            max-width: 100%;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
        }}

        .figure-caption {{
            font-size: 10pt;
            color: #666;
            font-style: italic;
            margin-top: 0.5em;
        }}
    </style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover">
    <div class="badge">FREE PLAYBOOK EDITION</div>
    <h1>The Agentic Developer</h1>
    <div class="subtitle">Stop Writing Code. Start Directing AI.</div>
    <p style="font-size: 13pt; color: #666; margin-top: 2em; max-width: 600px; line-height: 1.8;">
        Five essential chapters pulled from a comprehensive guide to building software with AI agents. Learn the mindset shift, the discipline, and the workflows that separate productive agentic developers from those stuck in productivity illusions.
    </p>
    <div class="author" style="margin-top: 4em;">
        <p style="margin: 0;">By Julio Casal</p>
        <p style="margin: 0.3em 0 0 0; color: #999; font-size: 12pt;">Software Engineer, Ex-Microsoft, Founder of .NET Academy</p>
    </div>
</div>

<!-- TABLE OF CONTENTS -->
<div class="toc">
    <h2>What You'll Learn</h2>
    <p style="margin-bottom: 1.5em;">This playbook contains five chapters from the complete 29-chapter book, chosen for immediate impact and practical value.</p>

    <div style="margin-top: 2em;">
        <h3 style="margin-top: 0; color: #6366f1;">Chapter 1</h3>
        <p><strong>Software Development Has Changed</strong></p>
        <p style="color: #666; font-size: 10pt; margin: 0.5em 0 0 0;">From autocomplete to autonomous agents. What actually changed, why it matters, and why "just use Copilot" isn't a strategy.</p>
    </div>

    <div style="margin-top: 1.5em;">
        <h3 style="margin-top: 0; color: #6366f1;">Chapter 2</h3>
        <p><strong>The METR Paradox</strong></p>
        <p style="color: #666; font-size: 10pt; margin: 0.5em 0 0 0;">Why experienced developers are 19% slower with AI tools yet believe they're 20% faster. The discipline gap that separates good from great.</p>
    </div>

    <div style="margin-top: 1.5em;">
        <h3 style="margin-top: 0; color: #6366f1;">Chapter 3</h3>
        <p><strong>Your New Job Description</strong></p>
        <p style="color: #666; font-size: 10pt; margin: 0.5em 0 0 0;">The five new skills you need to thrive as an agentic developer. How your coding expertise becomes even more valuable.</p>
    </div>

    <div style="margin-top: 1.5em;">
        <h3 style="margin-top: 0; color: #6366f1;">Chapter 4</h3>
        <p><strong>Writing Effective Context Files</strong></p>
        <p style="color: #666; font-size: 10pt; margin: 0.5em 0 0 0;">The single most important skill. How to curate what agents see so they produce better results. Complete templates included.</p>
    </div>

    <div style="margin-top: 1.5em;">
        <h3 style="margin-top: 0; color: #6366f1;">Chapter 5</h3>
        <p><strong>The TDD Agent Loop</strong></p>
        <p style="color: #666; font-size: 10pt; margin: 0.5em 0 0 0;">Write tests first, let the agent write the code. The highest-confidence workflow for working with AI, with complete examples.</p>
    </div>
</div>

<!-- INTRODUCTION -->
<div style="page-break-after: always;">
    <h2 style="margin-top: 0;">Introduction</h2>

    {convert_chapter(chapters["00-front-matter.md"])}

    <div class="author-section">
        <h3>About the Author</h3>
        <p>Julio Casal is a software engineer, ex-Microsoft, and founder of .NET Academy where he teaches thousands of developers. He's spent the last year studying agentic workflows so you don't have to learn the hard way. He builds real systems, teaches what works, and skips the hype.</p>
        <p style="margin-bottom: 0;">This playbook is five chapters from a complete 29-chapter guide on agentic development. Details on the full book are at the end.</p>
    </div>
</div>

<!-- CHAPTER 1 -->
<div class="chapter">
    <div class="chapter-header">
        <div class="chapter-number">Chapter 1</div>
        <div class="chapter-title">Software Development Has Changed</div>
    </div>

    {convert_chapter(chapters["01-software-development-has-changed.md"], skip_title=True)}
</div>

<!-- CHAPTER 2 -->
<div class="chapter">
    <div class="chapter-header">
        <div class="chapter-number">Chapter 2</div>
        <div class="chapter-title">The METR Paradox</div>
    </div>

    {convert_chapter(chapters["02-the-metr-paradox.md"], skip_title=True)}
</div>

<!-- CHAPTER 3 -->
<div class="chapter">
    <div class="chapter-header">
        <div class="chapter-number">Chapter 3</div>
        <div class="chapter-title">Your New Job Description</div>
    </div>

    {convert_chapter(chapters["03-your-new-job-description.md"], skip_title=True)}
</div>

<!-- CHAPTER 4 -->
<div class="chapter">
    <div class="chapter-header">
        <div class="chapter-number">Chapter 4</div>
        <div class="chapter-title">Writing Effective Context Files</div>
        <div class="chapter-subtitle">(Chapter 6 in the full book)</div>
    </div>

    {convert_chapter(chapters["04-writing-effective-context-files.md"], skip_title=True)}
</div>

<!-- CHAPTER 5 -->
<div class="chapter">
    <div class="chapter-header">
        <div class="chapter-number">Chapter 5</div>
        <div class="chapter-title">The TDD Agent Loop</div>
        <div class="chapter-subtitle">(Chapter 13 in the full book)</div>
    </div>

    {convert_chapter(chapters["05-the-tdd-agent-loop.md"], skip_title=True)}
</div>

<!-- BACK MATTER -->
<div class="back-matter">
    {convert_chapter(chapters["06-back-matter.md"])}

    <div class="cta-box">
        <h2>Ready for the Full Book?</h2>
        <p>The complete version includes all 29 chapters, downloadable context file templates, companion GitHub repository with working code examples, and access to updates as the field evolves.</p>
        <p style="margin-bottom: 0;"><strong>The Agentic Developer</strong> is available at your next step in mastery.</p>
    </div>

    <hr>

    <p style="text-align: center; color: #999; font-size: 11pt; margin-top: 3em;">
        <strong>Thanks for reading this free playbook.</strong><br>
        Now go write a context file and break the METR paradox.
    </p>
</div>

</body>
</html>'''

# Write HTML
out_html = BASE / "playbook.html"
out_html.write_text(html)
print(f"HTML written to {out_html} ({out_html.stat().st_size // 1024}KB)")

# Render PDF
out_pdf = BASE / "the-agentic-developer-playbook.pdf"
print("Rendering PDF with WeasyPrint...")
result = subprocess.run(
    ["/home/azureuser/.local/bin/weasyprint", str(out_html), str(out_pdf)],
    capture_output=True, text=True, cwd=str(BASE)
)
if result.returncode != 0:
    print(f"WeasyPrint stderr: {result.stderr}")
    sys.exit(1)

print(f"PDF written to {out_pdf} ({out_pdf.stat().st_size // 1024}KB)")

# Page count
try:
    import pikepdf
    with pikepdf.open(out_pdf) as pdf:
        print(f"Page count: {len(pdf.pages)}")
except ImportError:
    # Try pdfinfo
    r = subprocess.run(["pdfinfo", str(out_pdf)], capture_output=True, text=True)
    if r.returncode == 0:
        for line in r.stdout.split('\n'):
            if 'Pages' in line:
                print(line.strip())
    else:
        print("Could not determine page count")

print("Done!")
