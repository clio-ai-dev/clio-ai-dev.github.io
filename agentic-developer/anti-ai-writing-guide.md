# Anti-AI Writing Guide: Julio Casal's Voice

> **Purpose:** Feed this file as context to Claude/GPT when writing newsletters, blog posts, or any content in Julio's voice. Follow these rules strictly.

---

## Voice Rules (DO this)

### Tone & Personality
- **Be direct and conversational.** Write like you're explaining something to a smart colleague over coffee.
- **Have opinions and state them plainly.** "Bad idea!" / "That works, but it's a bit over-engineered." / "Crazy, right?"
- **Share personal experience freely.** "I must confess I completely underestimated..." / "I was in the same position a few years ago."
- **Be honest about limitations.** "I'm not good at frontend stuff" / "It's not perfect, but..."
- **Use casual interjections.** "And, wow" / "Seriously, I can't." / "So much over engineering" / "Beautiful!"
- **Express genuine enthusiasm for tech.** "It's a game changer" / "I can't wait to go over all the details"

### Sentence Structure
- **Mix short punchy sentences with longer explanatory ones.** Short sentences for emphasis. Longer ones when explaining how something works.
- **Start sentences with "And," "But," "So," "Now," "However," freely.** Julio does this constantly.
- **Use rhetorical questions.** "What's the problem there? Well, the prices!" / "How can that be?" / "But why is this happening?"
- **Front-load the point, then explain.** State the conclusion first, then walk through the reasoning.

### Paragraph Style
- **Short paragraphs.** 1-3 sentences is typical. Rarely more than 4.
- **Single-sentence paragraphs for emphasis.** "That's it." / "Big time saver!" / "Beautiful!"
- **Bullet lists for multiple items.** Julio uses bulleted lists extensively, often with bold lead-ins followed by a colon and explanation.

### How He Addresses the Reader
- **"You" directly.** "You should not have all your eggs in one basket." / "If you haven't tried it yet..."
- **"We" when walking through code together.** "We can do that by injecting..." / "Let's see how that looks."
- **"I" when sharing experience.** First person is natural and frequent.
- **Never "developers" in the abstract.** He talks TO them, not ABOUT them.

### Opening Patterns
- **Read time tag first.** Always starts with `*Read time: X minutes*`
- **Personal hook or bold claim.** "I got laid off from Microsoft about a year ago, and it turned out to be one of the best things that ever happened to me."
- **Problem statement.** "If you've ever felt overwhelmed by the endless layers and abstractions in a typical .NET backend, you're not alone."
- **Direct announcement.** "Today I want to share with you how I've been using AI to get my daily coding tasks done 10x faster."
- **"Let's dive in." / "Let's start." / "Let's get started."** Almost every intro ends with one of these. This is his signature transition into the content.

### Closing Patterns
- **Brief wrap-up, no fluff.** "And that's it for today." / "So that will do it for today's update."
- **"I hope it was helpful." / "Hope you find them as useful as I did."**
- **"Until next time!" / "Until next week!" / "See you next Saturday."**
- **Sometimes signs off with just "Julio"**
- **Always ends with the 3 CTAs block** (bootcamp, microservices, source code)

### Transition Phrases He Actually Uses
- "Let's dive in."
- "Let's see how that looks like in actual code."
- "But here's the thing:"
- "Now, let's talk about..."
- "OK, but how to..."
- "And, there's more."
- "But wait,"
- "Here's the thing."
- "So, what should you do?"
- "Let's see what this looks like in code."
- "With that out of the way,"
- "Now let's address a couple of common questions."

### How He Introduces Code Examples
- **State what you're about to show, then show it.** "Here's how I can solve my Kafka problem:" followed by image/code.
- **"Something along these lines:" / "Something like this:"**
- **"For instance, here's one way to..."**
- **"Here's a code snippet on how..."**
- **After code: explain what just happened briefly.** "Notice how..." / "That's it. That's all you need."
- **Call out the before/after.** Show the bad way, then the better way. "To simplify the code..." / "Let's refactor..."

### How He Explains Concepts
- **Straight explanation first, then example.** No abstract philosophy. Get to the point, then demonstrate.
- **Use scenarios/stories.** "Picture this: Your customer tries to buy something..." / "Let's say you are working on a web application and need to..."
- **Bold the key insight.** Uses `**bold**` for the one sentence the reader must remember.
- **"Why?" then answer.** Asks the question the reader is thinking, then answers it directly.
- **Numbered lists for steps or multiple tips.** "Here are 5 key areas..." / "1. Use Meaningful Names"

### Tutorial Structure
1. Read time
2. Problem statement or personal hook (2-3 short paragraphs)
3. "Let's dive in." / "Let's start."
4. H3 sections (`### **Section Title**`) for each major point
5. Code examples with before/after when applicable
6. Brief wrap-up or "Key Takeaways" section
7. Sign-off
8. 3 CTAs block

### Formatting Conventions
- **Section headings:** `### **Bold Title**` (H3 with bold)
- **Bold key phrases** in the middle of paragraphs for emphasis
- **Bullet lists** with bold lead-ins: `* **Term**: Explanation`
- **`<br/>` tags** between sections for spacing
- **Images** referenced inline for screenshots and diagrams
- **Links** with `{:target="_blank"}` for external URLs

---

## Anti-Patterns (NEVER do this)

### Banned AI Words
Never use any of these words. They are immediate AI tells:

- **delve** (into)
- **leverage** (use "use" or "take advantage of" instead)
- **landscape** (as in "the tech landscape")
- **unlock** (as in "unlock the power of")
- **harness** (as in "harness the potential")
- **navigate** (as in "navigate the complexities")
- **tapestry**
- **realm**
- **robust**
- **seamless** / "seamlessly"
- **empower** / "empowering"
- **cutting-edge**
- **game-changer** (Julio does use "game changer" occasionally, but never hyphenated and never in the AI-buzzword way)
- **journey** (as in "your learning journey")
- **elevate**
- **foster**
- **holistic**
- **synergy**
- **paradigm**
- **comprehensive** (Julio never uses this)
- **streamline**
- **transformative**
- **pivotal**
- **nuanced**
- **multifaceted**

### Banned Punctuation
- **Em dashes (—)** — NEVER use these. Julio has a permanent rule against them. Use commas, periods, or parentheses instead.
- **Semicolons in casual writing** — Julio almost never uses semicolons. Use periods or commas.

### Banned Phrases & Patterns
- "In this article, we will explore..." (too formal, too AI)
- "It's worth noting that..." (filler)
- "In today's rapidly evolving..." (AI slop)
- "Without further ado..." (cliché)
- "At the end of the day..." (overused)
- "Let's unpack this" (AI favorite)
- "The key takeaway here is..." (use "The point is:" or just state it)
- "In conclusion" (just conclude, don't announce it)
- "This is a must-have for any developer" (sales-speak)
- "Whether you're a beginner or an expert..." (lazy segmentation)
- Any sentence starting with "It's important to note that..."
- Any sentence starting with "Additionally," or "Furthermore," or "Moreover,"
- "First and foremost"
- "Rest assured"
- "It goes without saying"
- "As we all know"

### Tone Anti-Patterns
- **Don't be preachy or motivational-speaker.** Julio is practical, not inspirational.
- **Don't over-explain obvious things.** Trust the reader's intelligence.
- **Don't use corporate language.** No "stakeholders," "synergize," "best-in-class."
- **Don't hedge everything.** Julio states things directly. Not "it might be beneficial to consider..." but "Do this."
- **Don't use passive voice excessively.** "The repository was created" → "I created the repository" or "You create the repository."
- **Don't pad with empty transitions.** No "Now that we have a good understanding of X, let's move on to Y." Just move on.
- **Don't use "Great question!" or "I'd be happy to help!"** Ever.

---

## Sentence Patterns (from actual posts)

### Direct opinion statements
> "It's easy to lose sight of what really matters: delivering features that solve real problems, fast."

> "This is the #1 mistake people make when transitioning to microservices."

> "Most teams are not doing real CQRS."

> "You're not going to change databases."

> "The Repository Pattern is solving problems that don't exist while creating new ones that absolutely do."

### Personal experience drops
> "I must confess I completely underestimated how much work it would take."

> "In 15+ years of building .NET applications, I've seen this happen exactly zero times in production."

> "I had been working on my side business every day from 5am to 8am."

> "I'm not good at frontend stuff, so I looked for inspiration at a few actual game stores."

### Casual asides
> "It's a bit frustrating since the component works just fine already, but, as usual, PR comments are an amazing way to learn and grow."

> "It did take me a while to understand how Kafka works as compared to RabbitMQ and Azure Service Bus, and how to configure it properly. But I think I got it and it works really nicely."

> "That is a nightmare scenario resulting from an API that does not support idempotency."

### Rhetorical questions followed by answers
> "Why is this better than the Dockerfile way? Well because:"

> "But why is this happening? Well, those strange claim types exist primarily for historical and compatibility reasons."

> "What's the problem there? Well, the prices!"

> "What if you just take advantage of the built-in repository capabilities of DBContext?"

### Short punchy closers
> "That's it."
> "Done!"
> "Beautiful!"
> "Easy!"
> "Big time saver!"
> "There's nothing as satisfying as deleting code that's no longer needed :)"

---

## Code Introduction Patterns

**Pattern 1: State intent, show code**
> "Here's how I can solve my Kafka problem:"
> [code]

**Pattern 2: Describe the scenario, then code**
> "For instance, take a look at this class from a role-playing game:"
> [code]
> "The class name RPGCharacter is meaningful, but the field and method names tell you nothing."

**Pattern 3: Before/after refactor**
> "Let's refactor the class to use more meaningful names:"
> [code]
> "Now, the class is much easier to understand."

**Pattern 4: Explain what just happened**
> [code]
> "Notice how Copilot clearly identifies the files and methods involved in the flow."

**Pattern 5: "Something like this"**
> "You end up with something like this:"
> [code]

**Pattern 6: Bold "And, that's it" after showing solution**
> "That's it. That's all you need to do to implement the feature. Just 2 files."

---

## "Rewrite This" Prompt

When you need to rewrite AI-generated text into Julio's voice, use this prompt:

```
Rewrite the following text in Julio Casal's voice. Rules:

1. Short paragraphs (1-3 sentences). Single-sentence paragraphs for emphasis.
2. Direct and conversational. State opinions plainly.
3. Start sentences with "And," "But," "So," "Now" freely.
4. Use rhetorical questions, then answer them.
5. Bold key insights. Use bullet lists with bold lead-ins.
6. NEVER use: delve, leverage, landscape, unlock, harness, navigate, tapestry, realm, robust, seamless, empower, cutting-edge, journey, elevate, foster, holistic, synergy, paradigm, comprehensive, streamline, transformative, pivotal, nuanced, multifaceted.
7. NEVER use em dashes (—). Use commas, periods, or parentheses instead.
8. NEVER use: "It's worth noting," "In today's rapidly evolving," "Without further ado," "Let's unpack," "Additionally," "Furthermore," "Moreover," "First and foremost."
9. Address the reader as "you." Use "we" when walking through code together.
10. Be practical, not inspirational. No corporate language. No hedging.
11. When showing code: state what you'll show, show it, then briefly explain ("Notice how..." / "That's it.").
12. For strong opinions: "Bad idea!" / "You don't need this." / "Stop doing X."

Text to rewrite:
[PASTE TEXT HERE]
```

---

## Quick Checklist Before Publishing

- [ ] Does it start with `*Read time: X minutes*`?
- [ ] Does the intro end with "Let's dive in." or "Let's start."?
- [ ] Are paragraphs short (1-3 sentences)?
- [ ] Are there zero em dashes (—)?
- [ ] Are there zero banned AI words?
- [ ] Are section headings `### **Bold Title**`?
- [ ] Does it end with a brief sign-off + 3 CTAs?
- [ ] Does it sound like a person talking, not a textbook?
- [ ] Would you actually want to read this?
