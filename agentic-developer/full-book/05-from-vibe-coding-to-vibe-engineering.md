# Chapter 5: From Vibe Coding to Vibe Engineering

In February 2025, Andrej Karpathy posted a tweet that named something everyone was already doing: "I just mass mass mass mass prompt, write barely any code. Sometimes I don't even read the diffs. I just accept them." He called it "vibe coding." The term went viral because it was honest. Millions of developers were doing exactly this and nobody had a word for it.

One year later, in February 2026, Karpathy posted again. This time, the term was "agentic engineering." He described it as "a serious engineering discipline involving autonomous agents." Same person, same field, twelve months apart. The progression from "fully give in to the vibes" to "serious engineering discipline" tells you everything about how fast this field matured.

This chapter traces that evolution. Not as history for its own sake, but because understanding the spectrum from vibe coding to agentic engineering tells you which mode to use when. And the answer is: all of them, depending on what you're building.

## What Karpathy Actually Said

Let's be precise about vibe coding, because the term got distorted as it spread. Karpathy's original description was specific: "I just see things, say things, run things, and copy-paste things, and it mostly works." The key phrase was "forget that the code even exists."


This wasn't laziness. Karpathy is one of the most technically capable people on the planet, founding member of OpenAI, former head of AI at Tesla. He was describing a genuinely new interaction model. For certain tasks (quick scripts, prototypes, one-off tools), you could describe what you wanted in natural language, let the AI generate code, run it, see if it worked, and iterate. You didn't need to understand the code at a line-by-line level. You just needed to evaluate the output.

The context matters too. In early 2025, the tools were chat-based. You described what you wanted. The AI generated code. You pasted it into your editor. You ran it. If it failed, you pasted the error back. This loop was clunky but surprisingly effective for small, self-contained tasks.

Karpathy was explicit about the scope: "It's not really coding. I just see stuff, say stuff, run stuff." He positioned it as something different from professional software engineering. A new way of interacting with computers that happened to produce code as a side effect.

## What Vibe Coding Got Right

Let's give vibe coding its due. It identified something genuinely important that the professional software engineering community was slow to acknowledge.

### The Accessibility Revolution

Before vibe coding, if you wanted a custom script to rename 10,000 files according to a specific pattern, you needed to know Python or Bash or PowerShell. After vibe coding, you needed to describe the pattern in English. This is a real, meaningful expansion of who can create software. Researchers, designers, marketers, small business owners: people who were previously locked out of automation gained access to it.

This wasn't a toy. Non-engineers started building real tools. Internal dashboards. Data processing pipelines. Workflow automations. Anthropic's 2026 report identifies "non-engineers embrace agentic coding" as one of its eight major trends, noting that sales, legal, and marketing teams are now building their own tools.

### The Prototyping Speed

For exploratory work, vibe coding was and remains blazingly fast. When you're trying to figure out if an idea even works, the overhead of writing specs, setting up project structure, configuring CI/CD, and writing tests is counterproductive. You need a quick-and-dirty prototype that lets you evaluate the concept. Vibe coding delivers that in minutes instead of days.

I still use vibe coding for this exact purpose. When I want to test whether a particular API integration is feasible, I don't need production-quality code. I need code that runs, calls the API, and shows me the response shape. Vibe coding gets me there in five minutes.

### The Creative Energy

This is the most underappreciated contribution of vibe coding. It reintroduced *play* into programming. The rapid feedback loop of "describe, generate, run, see" has an almost game-like quality. You're experimenting, iterating, exploring possibilities at a pace that traditional development doesn't allow. That creative energy is valuable. It shouldn't be discarded just because it doesn't produce production-quality code.

## What Vibe Coding Got Wrong

Vibe coding had a fatal flaw, and it was right there in Karpathy's original description: "forget that the code even exists."

For prototypes, that's fine. For anything that persists, that's a disaster.


### No Verification

The core of vibe coding was "run it and see if it works." But "works" meant "produces visually correct output for the one case I tested." It didn't mean correct, secure, performant, or maintainable. It meant "doesn't crash on the happy path."

This is how vibe-coded projects accumulate debt at staggering speed. The code works for the cases you tried. The cases you didn't try are time bombs. And because you "forgot the code exists," you don't even have a mental model of where the bombs are planted.

GitClear's research found a 4x growth in code clones with AI assistants. Code clones are a proxy for copy-paste development, taking generated code without understanding it. That's vibe coding at scale.

### No Structure

Vibe-coded projects tend to grow into unmaintainable tangles because nobody made architectural decisions. The AI generated code that worked, and that code accumulated. There's no separation of concerns because nobody specified one. There's no consistent error handling because nobody defined a strategy. There are three different ways to call the database because each prompt got a different response from the model.

This is fine for a 200-line script. It's catastrophic for a 20,000-line application. And the transition from 200 lines to 20,000 lines happens faster than you'd think when an agent is generating code.

### No Sustainability

The final failure of pure vibe coding is that it produces code that only the original prompter can work with, and even they can't work with it a month later. There are no comments (because the human didn't write the code and didn't review it closely enough to add comments). There are no tests (because tests are overhead that slows down the vibes). There's no documentation (because the prompts that generated the code aren't saved alongside it).

Try handing a vibe-coded project to a new developer. Or try coming back to your own vibe-coded project after three months. You'll find yourself re-prompting from scratch because the existing code is inscrutable, even though (especially because) you didn't read it carefully the first time.

## Simon Willison's Intervention: "Vibe Engineering"

In October 2025, Simon Willison published a piece that reframed the entire conversation. He'd been one of the most prolific users of AI coding tools, running multiple agents in parallel daily, and he had strong opinions about what was working and what wasn't.

His key move was reclaiming the word "vibe" while adding engineering discipline to it. Vibe engineering kept the creative energy, the rapid iteration, the natural language interaction model. But it added the things that pure vibe coding lacked: verification, structure, and sustainability.

### The Willison Method

Willison's workflow, as described across his blog posts and conference talks, looked like this:

1. **Start with a spec.** Not a formal PRD. A description of what you want, written in your own words, specific enough that you could review the output against it. "Code that started from your own specification is a lot less effort to review."

2. **Use agents, not chat.** By late 2025, Willison had moved from chat-based coding to Claude Code and Codex CLI: agents that could read his codebase, run tests, and iterate. The agent didn't just generate code. It operated within the project.

3. **Run agents in parallel.** His "parallel coding agent lifestyle" involved 3-5 agents simultaneously, each on a different task in a different git worktree. One researching a library, one implementing a feature, one fixing bugs. He orchestrated and reviewed.

4. **Review everything.** Not at the diff level for every change, but at the outcome level for every task. Does it work? Does it match the spec? Does it follow conventions? Are there tests?

5. **Maintain context.** His projects had context files that told agents about conventions, patterns, and constraints. Each agent interaction benefited from this accumulated context.

The "vibe" in vibe engineering was the creative flow, the willingness to explore, the natural language interaction. The "engineering" was everything else: specs, tests, reviews, structure, context management.

### Why This Mattered

Willison's framing mattered because it created permission to enjoy the process while being disciplined about the output. The vibe coding camp said "just let go and trust the AI." The traditional engineering camp said "AI-generated code is dangerous, review everything manually." Vibe engineering said "both of you are half right."

You can enjoy the creative flow of rapid AI-assisted development AND maintain engineering standards. These aren't in tension. The standards actually enable the flow by catching mistakes early and giving you confidence to move fast.

## The Spectrum


By early 2026, the field had settled into a spectrum with four distinct modes. Each has legitimate uses. The skill isn't committing to one mode. It's knowing which mode fits the situation.

### Mode 1: Pure Vibe Coding

**What it is:** Prompt, generate, run, iterate. Don't read the code. Evaluate the output.

**When it's appropriate:**
- One-off scripts you'll use once and delete
- Rapid prototyping to test if an idea is feasible
- Personal tools that only you will use and that don't handle sensitive data
- Learning and exploration ("show me how webhooks work in .NET")
- Hackathons and time-boxed experiments

**When it's dangerous:**
- Anything that goes to production
- Anything that handles user data
- Anything other people will maintain
- Anything that needs to work in six months

**Realistic assessment:** Maybe 10-15% of your development work can safely be pure vibe coding. That's higher than the traditional engineering camp would admit and lower than the vibe coding evangelists claim.

### Mode 2: Vibe Engineering

**What it is:** The Willison method. Creative flow plus engineering discipline. Write specs, use agents, review outcomes, maintain context. You still use natural language as your primary interface, but you verify the results against defined criteria.

**When it's appropriate:**
- Feature development where you have clear requirements
- Building new services or modules within an existing architecture
- Refactoring with defined before/after states
- Any task where you can write a spec and define "done"

**When it's not enough:**
- Performance-critical systems where you need to understand every instruction
- Security-sensitive code that requires formal review
- Distributed systems debugging
- Anything where the cost of a subtle bug is very high

**Realistic assessment:** This is the sweet spot for maybe 50-60% of professional development work. Most feature development, most bug fixes, most incremental work fits comfortably in this mode.

### Mode 3: Agentic Engineering

**What it is:** The full discipline. Context engineering, TDD agent loops, comprehensive test suites, formal review processes, architectural specifications, multi-agent orchestration. You're directing a team of agents the way a senior engineer directs a team of developers.

**When it's appropriate:**
- Production systems
- Anything that needs to scale
- Security-sensitive features
- Performance-sensitive features
- Projects with multiple contributors
- Long-lived codebases

**When it's overkill:**
- Quick experiments
- Internal tools with a single user
- Throwaway prototypes

**Realistic assessment:** About 25-30% of your work warrants full agentic engineering discipline. But that 25-30% is the work that matters most: the production code, the systems that users depend on, the features that generate revenue.

### Mode 4: Traditional Engineering

**What it is:** You write the code. By hand. With full understanding of every line.

**When it's still necessary:**
- Novel algorithms where correctness is paramount
- Performance-critical hot paths (the inner 1% of code that handles 99% of load)
- Code that must be formally verifiable
- Debugging distributed system failures where you need to reason about state across time
- Extremely domain-specific logic where the agent doesn't have relevant training data

**Realistic assessment:** Probably 5-10% of your work. Shrinking, but not zero. And that's fine. The goal isn't to eliminate manual coding. It's to reserve your manual coding effort for the tasks where human judgment is genuinely irreplaceable.

## Knowing Which Mode to Use

The choice of mode isn't a personality preference. It's a risk/value calculation. Here's the decision framework:

**What's the blast radius if this code is wrong?**
- Crash in production affecting users? Agentic engineering or traditional.
- Bug in an internal tool that someone might notice? Vibe engineering.
- Wrong output in a script you'll run once? Vibe coding.


**How long will this code live?**
- Months or years? Agentic engineering.
- Weeks? Vibe engineering.
- Hours? Vibe coding.

**Who else will touch this code?**
- Your team? Agentic engineering.
- Just you? Vibe engineering or vibe coding.
- Nobody (throwaway)? Vibe coding.

**How well-defined is the task?**
- Clear spec with acceptance criteria? Agentic engineering.
- Rough idea that needs exploration? Vibe engineering.
- "I wonder if this is possible"? Vibe coding.

Most developers should be spending the majority of their time in the vibe engineering and agentic engineering modes. Pure vibe coding is for exploration. Traditional hand-coded engineering is for the critical paths. The middle two modes are where the bulk of productive work happens.

## The Maturation of a Field


The progression from vibe coding to agentic engineering mirrors a pattern we've seen before in technology. Every significant shift goes through the same phases: novelty, hype, disillusionment, and maturation.

### Phase 1: Novelty (Early 2025)

"Look what this can do!" Developers shared screenshots of AI-generated apps. Karpathy named the vibe. Everyone was amazed that you could describe a feature and get working code. The focus was on the capability, not the quality.

### Phase 2: Hype (Mid 2025)

"This changes everything!" Breathless predictions that developers would be obsolete. LinkedIn posts about "10x" productivity. Companies mandating AI tool adoption. The discourse outpaced the reality.

### Phase 3: Disillusionment (Late 2025)

The METR study dropped in July 2025 like a bomb: experienced developers were 19% slower with AI tools. GitClear published data showing 4x growth in code clones. Production incidents caused by unreviewed AI-generated code made the news. The backlash began. "AI coding tools are overrated." "They make developers sloppy." "The productivity gains are illusory."

The disillusionment was healthy. It forced honesty about what the tools could and couldn't do. It separated the "AI will write all our code" fantasy from the reality that AI tools require discipline to use effectively.

### Phase 4: Maturation (2026)

Now we're here. The hype has burned off. The skepticism has been addressed. What's left is a genuine engineering discipline. The tools are better (agents, not just chat). The practices are defined (context engineering, spec-first development, TDD agent loops). The expectations are calibrated (real productivity gains, but only with disciplined use).

Karpathy's terminology evolution captured this perfectly. "Vibe coding" was Phase 1/2. "Agentic engineering" is Phase 4. Same person, same tools, different understanding of how to use them well.

## The METR Study: What It Really Tells Us

The METR study deserves deeper attention because it's been cited by both sides (AI skeptics and AI advocates) to support their positions. Both readings are wrong.

The study found that experienced open-source developers were 19% slower using AI coding tools on tasks in codebases they were already deeply familiar with. The developers believed they were 20% faster. That's a 39-percentage-point gap between perception and reality.

The skeptic reading: "See? AI tools make you slower. Stop using them."

The advocate reading: "That study was flawed. The tasks were unusual. The developers didn't use the tools properly."

The accurate reading: AI tools make you slower when you use them naively on tasks where your existing expertise already makes you fast. The overhead of prompting, reviewing, and correcting AI output exceeds the time savings from generating code when you could have written the code faster yourself.

This is the argument for everything in this book. Naive AI tool use hurts. Disciplined agentic development helps. The gap between the two is the gap between the METR study's 19% slowdown and the reports of 2-3x productivity gains from practitioners like Willison who use structured workflows.

The METR finding isn't an argument against AI tools. It's an argument against using AI tools without a methodology. It's an argument for this book.

## What Changes Next

The spectrum from vibe coding to agentic engineering isn't static. It's shifting toward more agent autonomy as models improve. Tasks that required full agentic engineering discipline in 2025 (comprehensive context files, heavy review, tight test loops) might need only vibe engineering by 2027 as models get better at inference, context management, and self-verification.

But the fundamental dynamic won't change: there will always be tasks where you can trust agents more and tasks where you need to verify more. The spectrum won't collapse. It will shift.

What will change:

**The "vibe coding" zone will expand.** As models improve at self-verification and error detection, more tasks will be safe to handle with minimal review. Internal tools, scripts, prototypes, these will increasingly be fire-and-forget.

**The "agentic engineering" zone will move up the complexity stack.** Full agent orchestration with comprehensive testing and review will handle increasingly complex tasks. Things that require traditional hand-coding today (performance-critical paths, security-sensitive features) will move into the agentic engineering zone.

**The "traditional" zone will shrink but never disappear.** Some tasks will always require human judgment applied directly to code. Novel algorithm design. Debugging emergent behavior in distributed systems. Making the call about whether to ship or hold.

The developers who thrive will be the ones who can move fluidly across the spectrum, matching their approach to the task. Not zealots for any one mode. Pragmatists who use every tool available, including the oldest tool of all: their own brain, their own keyboard, their own judgment.

## The Choice

Here's where this gets personal. You're reading this book because you want to get better at building software with AI agents. The spectrum I've described isn't just a framework for choosing tools. It's a mirror for choosing who you want to be as an engineer.

Pure vibe coders are already hitting a ceiling. The prototypes are impressive. The production code is a mess. The technical debt accumulates silently until it doesn't.

Traditional holdouts are being outpaced. They write better code line-by-line, but they ship less of it. In a world where an agent can produce a decent first draft in seconds, spending an hour hand-crafting the same code is a competitive disadvantage for tasks that don't require that level of care.

The sweet spot, the place where careers are being built and companies are gaining advantage, is in the middle of the spectrum. Vibe engineering for the bulk of your work. Full agentic engineering for the critical paths. Vibe coding for exploration. Traditional engineering for the irreducible core that requires human judgment.

This is what the rest of the book teaches you to do. Not just which tools to use, but how to think about the work so that you're applying the right level of discipline to each task. The mindset from Chapter 4, the spectrum from this chapter: together they form the foundation for everything that follows.

The field matured fast. Twelve months from "forget the code exists" to "serious engineering discipline." The developers who matured with it are building things that weren't possible two years ago, faster than was possible one year ago, at a quality level that matches or exceeds what they could achieve by hand.

That's not hype. That's the new baseline. Let's build on it.
