#!/usr/bin/env python3
"""Build the full book HTML from markdown sources."""

import re
import markdown
from pathlib import Path

BASE = Path("/home/azureuser/.openclaw/workspace/clio-business/agentic-developer")
CHAPTERS_DIR = BASE / "chapters"
FULL_BOOK_DIR = BASE / "full-book"

# Book structure: (part_name, [(chapter_num, title, file_path), ...])
BOOK_STRUCTURE = [
    ("Part I: The Shift", [
        (1, "Software Development Has Changed", CHAPTERS_DIR / "01-software-development-has-changed.md"),
        (2, "The METR Paradox", CHAPTERS_DIR / "02-the-metr-paradox.md"),
        (3, "Your New Job Description", CHAPTERS_DIR / "03-your-new-job-description.md"),
        (4, "The Agentic Engineering Mindset", FULL_BOOK_DIR / "04-the-agentic-engineering-mindset.md"),
        (5, "From Vibe Coding to Vibe Engineering", FULL_BOOK_DIR / "05-from-vibe-coding-to-vibe-engineering.md"),
    ]),
    ("Part II: Context Engineering", [
        (6, "Writing Effective Context Files", CHAPTERS_DIR / "04-writing-effective-context-files.md"),
        (7, "Path-Scoped Rules", FULL_BOOK_DIR / "07-path-scoped-rules.md"),
        (8, "Skills: Teaching Your Agent New Tricks", FULL_BOOK_DIR / "08-skills.md"),
        (9, "MCP Servers and External Tool Integration", FULL_BOOK_DIR / "09-mcp-servers.md"),
        (10, "Designing an AI-Friendly Codebase", FULL_BOOK_DIR / "10-designing-ai-friendly-codebase.md"),
    ]),
    ("Part III: The Tools", [
        (11, "IDE Agents", FULL_BOOK_DIR / "11-ide-agents.md"),
        (12, "CLI and Cloud Agents", FULL_BOOK_DIR / "12-cli-cloud-agents.md"),
    ]),
    ("Part IV: The Workflows", [
        (13, "The TDD Agent Loop", CHAPTERS_DIR / "05-the-tdd-agent-loop.md"),
        (14, "Spec-First Development", FULL_BOOK_DIR / "14-spec-first-development.md"),
        (15, "Error-Message-Driven Debugging", FULL_BOOK_DIR / "15-error-driven-debugging.md"),
        (16, "Codebase Archaeology", FULL_BOOK_DIR / "16-codebase-archaeology.md"),
        (17, "Migration Generation", FULL_BOOK_DIR / "17-migration-generation.md"),
    ]),
    ("Part V: Scaling Up", [
        (18, "The Parallel Agent Lifestyle", FULL_BOOK_DIR / "18-parallel-agent-lifestyle.md"),
        (19, "Background Agents", FULL_BOOK_DIR / "19-background-agents.md"),
        (20, "Multi-Agent Coordination", FULL_BOOK_DIR / "20-multi-agent-coordination.md"),
        (21, "Agent + CI/CD Integration", FULL_BOOK_DIR / "21-agent-cicd-integration.md"),
        (22, "Cost Management", FULL_BOOK_DIR / "22-cost-management.md"),
    ]),
    ("Part VI: .NET-Specific Patterns", [
        (23, "Context Files for .NET", FULL_BOOK_DIR / "23-context-files-dotnet.md"),
        (24, "Agents and .NET Aspire", FULL_BOOK_DIR / "24-agents-and-aspire.md"),
        (25, "EF Core Migrations with Agents", FULL_BOOK_DIR / "25-ef-core-migrations.md"),
        (26, "Microsoft Agent Framework", FULL_BOOK_DIR / "26-microsoft-agent-framework.md"),
    ]),
    ("Part VII: The Discipline", [
        (27, "Security Review with Agents", FULL_BOOK_DIR / "27-security-review.md"),
        (28, "When NOT to Use Agents", FULL_BOOK_DIR / "28-when-not-to-use-agents.md"),
        (29, "The 30-Day Agentic Transformation", FULL_BOOK_DIR / "29-thirty-day-transformation.md"),
    ]),
]

def fix_emdash(text):
    """Replace em dashes with appropriate alternatives."""
    # Replace em dash with comma or colon contextually
    text = text.replace('\u2014', ', ')
    text = text.replace('—', ', ')
    text = text.replace('&mdash;', ', ')
    return text

def convert_md_to_html(md_text):
    """Convert markdown to HTML, stripping the first H1 (we use our own chapter headers)."""
    md_text = fix_emdash(md_text)
    
    # Remove the first markdown H1 line (# Title)
    lines = md_text.split('\n')
    new_lines = []
    found_h1 = False
    for line in lines:
        if not found_h1 and line.startswith('# ') and not line.startswith('## '):
            found_h1 = True
            continue  # skip first H1
        new_lines.append(line)
    md_text = '\n'.join(new_lines)
    
    # Remove leading italic subtitle lines (e.g., *This is where...*)
    md_text = re.sub(r'^\s*\*[^*]+\*\s*\n', '', md_text, count=1)
    
    # Convert markdown to HTML
    html = markdown.markdown(md_text, extensions=['fenced_code', 'tables', 'smarty'])
    
    # Convert blockquotes that look like callouts
    # Pattern: blockquote containing bold text starting with tip/warning/key
    html = re.sub(
        r'<blockquote>\s*<p><strong>(Tip|Warning|Key Insight|Note|Important|Remember)</strong>',
        r'<div class="callout tip"><p><strong>\1</strong>',
        html
    )
    # Close the callout divs properly
    html = re.sub(
        r'(class="callout tip"><p><strong>(?:Tip|Warning|Key Insight|Note|Important|Remember)</strong>.*?)</p>\s*</blockquote>',
        r'\1</p></div>',
        html,
        flags=re.DOTALL
    )
    
    return html


def build_introduction():
    """Build intro from front matter, skipping the playbook-specific parts."""
    fm = (CHAPTERS_DIR / "00-front-matter.md").read_text()
    fm = fix_emdash(fm)
    
    # Extract the "About the Author" and intro sections
    # Skip the playbook-specific "What This Playbook Is" and "What You'll Learn" 
    # Use a general introduction instead
    
    # Get author bio
    author_section = ""
    if "### About the Author" in fm:
        start = fm.index("### About the Author")
        end = fm.index("---", start + 10) if "---" in fm[start+10:] else len(fm)
        author_bio = fm[start:start + fm[start:].index("\n---") if "\n---" in fm[start:] else len(fm)]
        author_html = markdown.markdown(author_bio, extensions=['fenced_code'])
        author_section = f'<div class="author-section">{author_html}</div>'
    
    intro_html = f"""
<div class="chapter">
    <div class="chapter-header">
        <div class="chapter-title">Introduction</div>
    </div>
    {author_section}
    <p>This is not a hype piece. This is not "AI will replace developers" clickbait.</p>
    <p>This is a field guide. Twenty-nine chapters covering everything from the mindset shift to concrete workflows, from context engineering to multi-agent coordination, from IDE tools to CI/CD integration.</p>
    <p>Developers are adopting AI tools at a staggering rate. Anthropic's 2026 report says developers now use AI in 60% of their work. GitHub Copilot has generated over a million pull requests. Every IDE ships an "agent mode." The tools are everywhere.</p>
    <p>But a landmark study from METR found that experienced open-source developers were actually 19% <em>slower</em> when using AI tools on familiar codebases. And here's the kicker: those same developers <em>believed</em> they were 20% faster.</p>
    <p>That gap between perception and reality is where most developers live right now. They're using AI. They think it's helping. And in many cases, it's making them worse.</p>
    <p>This book exists because the difference between those two outcomes (slower versus faster) isn't the tool. It's the technique. The developers who are genuinely more productive with AI agents aren't the ones who type the best prompts. They're the ones who provide the best context, write the best specs, and review the output with the sharpest eye.</p>
    <p>They've become agentic developers.</p>
    <h3>A Note on Language</h3>
    <p>The code examples in this book use C# because that's what I write every day. But every pattern, every workflow, every principle applies to whatever language you use. If you write Python, TypeScript, Go, Java, or Rust, this book is for you. The agent doesn't care about your language. It cares about your context.</p>
    <h3>Let's Go</h3>
    <p>You can read this book in a weekend. By the end, you'll have a fundamentally different understanding of how to work with AI agents, and concrete workflows you can start using on Monday.</p>
</div>
"""
    return intro_html


def build_toc():
    """Build table of contents."""
    toc = '<div class="toc"><h2>Table of Contents</h2>\n'
    toc += '<div class="toc-entry"><span>Introduction</span></div>\n'
    
    for part_name, chapters in BOOK_STRUCTURE:
        toc += f'<div style="margin-top: 1.2em; margin-bottom: 0.3em; font-weight: 700; color: #6366f1; font-size: 12pt;">{part_name}</div>\n'
        for ch_num, title, _ in chapters:
            toc += f'<div class="toc-entry"><span>Chapter {ch_num}: {title}</span></div>\n'
    
    toc += '</div>\n'
    return toc


def build_part_divider(part_name, part_num):
    """Build a part divider page."""
    return f"""
<div style="page-break-before: always; padding-top: 35vh; text-align: center;">
    <div style="font-size: 14pt; font-weight: 600; color: #6366f1; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 0.5em;">{part_name.split(':')[0].strip()}</div>
    <div style="font-size: 32pt; font-weight: 700; color: #1a1a2e;">{part_name.split(':', 1)[1].strip() if ':' in part_name else ''}</div>
</div>
"""


def build_chapter(ch_num, title, filepath):
    """Build a chapter section."""
    md_text = filepath.read_text()
    content_html = convert_md_to_html(md_text)
    
    return f"""
<div class="chapter">
    <div class="chapter-header">
        <div class="chapter-number">Chapter {ch_num}</div>
        <div class="chapter-title">{fix_emdash(title)}</div>
    </div>
    {content_html}
</div>
"""


def build_full_book():
    """Assemble the complete book HTML."""
    
    # Cover page
    cover = """
<div class="cover">
    <h1>The Agentic Developer</h1>
    <div class="subtitle">Stop Writing Code. Start Directing AI.</div>
    <p style="font-size: 13pt; color: #666; margin-top: 2em; max-width: 600px; line-height: 1.8;">
        A comprehensive guide to building software with AI agents. 
        29 chapters covering mindset, context engineering, workflows, 
        tools, scaling, .NET patterns, and the discipline to do it right.
    </p>
    <div class="author" style="margin-top: 4em;">
        <p style="margin: 0;">By Julio Casal</p>
        <p style="margin: 0.3em 0 0 0; color: #999; font-size: 12pt;">Software Engineer, Ex-Microsoft, Founder of .NET Academy</p>
    </div>
</div>
"""
    
    # TOC
    toc = build_toc()
    
    # Introduction
    intro = build_introduction()
    
    # Parts and chapters
    body_parts = []
    for i, (part_name, chapters) in enumerate(BOOK_STRUCTURE):
        body_parts.append(build_part_divider(part_name, i + 1))
        for ch_num, title, filepath in chapters:
            body_parts.append(build_chapter(ch_num, title, filepath))
    
    chapters_html = '\n'.join(body_parts)
    
    # CSS from playbook (with adjustments for full book)
    css = """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&family=JetBrains+Mono:wght@400;500&display=swap');

        * { margin: 0; padding: 0; box-sizing: border-box; }

        @page {
            size: 8.5in 11in;
            margin: 1in;
            margin-left: 1.2in;
            @bottom-center {
                content: counter(page);
                font-family: 'Inter', sans-serif;
                font-size: 10pt;
                color: #999;
            }
        }
        @page :first { @bottom-center { content: ''; } }

        html {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #1a1a2e;
            background: white;
        }
        body { padding: 0; margin: 0; }

        h1 { font-size: 32pt; font-weight: 900; margin: 0.5em 0 0.3em 0; color: #1a1a2e; line-height: 1.2; }
        h2 { font-size: 24pt; font-weight: 700; margin: 1.5em 0 0.8em 0; color: #1a1a2e; line-height: 1.3; page-break-after: avoid; }
        h3 { font-size: 14pt; font-weight: 600; margin: 1.2em 0 0.6em 0; color: #1a1a2e; page-break-after: avoid; }
        h4 { font-size: 12pt; font-weight: 600; margin: 0.8em 0 0.4em 0; color: #1a1a2e; }
        p { margin: 0 0 1em 0; line-height: 1.65; }
        strong { font-weight: 600; color: #1a1a2e; }
        em { font-style: italic; }

        .cover {
            page-break-after: always;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            min-height: 100vh; text-align: center;
            background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
            padding: 4em 2em;
        }
        .cover h1 { font-size: 48pt; margin-bottom: 0.2em; color: #1a1a2e; }
        .cover .subtitle { font-size: 22pt; font-weight: 500; color: #6366f1; margin-bottom: 1em; }
        .cover .author { font-size: 14pt; color: #666; margin-top: 2em; }

        .chapter { page-break-before: always; margin-bottom: 3em; }
        .chapter-header { margin-bottom: 2em; padding-bottom: 1.5em; border-bottom: 2px solid #eee; }
        .chapter-number { font-size: 12pt; font-weight: 600; color: #6366f1; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.3em; }
        .chapter-title { font-size: 28pt; font-weight: 700; color: #1a1a2e; margin-bottom: 0.5em; }

        code {
            font-family: 'JetBrains Mono', monospace;
            font-size: 9.5pt; background: #f8fafc; padding: 0.2em 0.4em;
            border-radius: 3px; color: #d946ef;
        }
        pre {
            background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px;
            padding: 1em; margin: 1em 0; overflow-x: auto; break-inside: avoid;
        }
        pre code { background: none; padding: 0; color: #1a1a2e; font-size: 9pt; line-height: 1.5; }

        .callout {
            background: #eef2ff; border-left: 4px solid #6366f1;
            padding: 1em; margin: 1.5em 0; border-radius: 4px; break-inside: avoid;
        }
        .callout.tip { border-left-color: #6366f1; background: #eef2ff; }
        .callout.warning { border-left-color: #f59e0b; background: #fffbeb; }
        .callout.key { border-left-color: #10b981; background: #f0fdf4; }

        blockquote {
            border-left: 4px solid #6366f1; padding-left: 1em;
            margin: 1.5em 0; color: #666; font-style: italic;
        }
        ul, ol { margin: 1em 0 1em 1.5em; }
        li { margin-bottom: 0.5em; line-height: 1.65; }

        table { width: 100%; border-collapse: collapse; margin: 1.5em 0; break-inside: avoid; }
        th { background: #f8fafc; border: 1px solid #e2e8f0; padding: 0.7em; text-align: left; font-weight: 600; color: #1a1a2e; }
        td { border: 1px solid #e2e8f0; padding: 0.7em; color: #1a1a2e; }
        tr:nth-child(even) { background: #f8fafc; }

        .toc { page-break-after: always; }
        .toc h2 { margin-bottom: 1.5em; }
        .toc-entry { margin-bottom: 0.5em; }

        .author-section { background: #f8fafc; padding: 1.5em; border-radius: 6px; margin: 2em 0; break-inside: avoid; }
        .author-section h3 { color: #6366f1; margin-top: 0; }

        .note { background: #fffbeb; border-left: 4px solid #f59e0b; padding: 1em; margin: 1.5em 0; border-radius: 4px; break-inside: avoid; }

        hr { border: none; border-top: 1px solid #eee; margin: 2em 0; }
    """
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>The Agentic Developer</title>
    <style>{css}</style>
</head>
<body>
{cover}
{toc}
{intro}
{chapters_html}
</body>
</html>"""
    
    # Final em-dash cleanup on the entire output
    html = fix_emdash(html)
    
    return html


if __name__ == "__main__":
    html = build_full_book()
    out_path = BASE / "full-book.html"
    out_path.write_text(html)
    print(f"Written {out_path} ({len(html)} bytes)")
