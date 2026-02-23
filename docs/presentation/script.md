# Foundry Presentation Script

**Target Length:** ~30 minutes talking time
**Format:** Working demo with fast-forwarding through AI execution

### Script Conventions

- `[SCREEN: ...]` — Switch to this screen/window
- `[ACTION: ...]` — Do this on screen (click, type, navigate)
- `[FF]` — Fast-forward the video (show sped-up AI execution)
- `[CUT]` — Hard cut, skip entirely to the result
- Plain text — Teleprompter / spoken words

---

## Act 1: Build the Foundation (~13 min)

---

### 1. The Problem (1.5 min)

[SCREEN: Website — foundry-ai.io]

If you're using Claude Code today, you probably started the same way most of us did. You created a CLAUDE.md file, typed some instructions into it, maybe copy-pasted a few things from a blog post or a previous project, and started working.

And that works. For one project, with one person, it's fine.

But then you start a second project. And you write another CLAUDE.md from scratch. And it's a little different from the first one. Different conventions, different structure, different level of detail. Your third project drifts even further.

And here's the deeper problem — in a vanilla Claude Code setup, you have one agent doing everything. It's your architect, your developer, your QA engineer, your tech writer, all in one. That's like hiring a single person and expecting them to context-switch between system design, implementation, testing, and documentation — all at the same quality level.

Now scale that up. You have a team of people, each with their own Claude Code projects, all set up differently. There's no shared library, no consistency, no way to say "this is how we do things here."

And there's no orchestration. You can ask Claude Code to build one thing at a time. But you can't say "here are nine features — go build them in parallel."

That's the world before Foundry.

---

### 2. What Foundry Is (1.5 min)

[SCREEN: Website — foundry-ai.io]

Foundry solves this by treating your AI development team the same way you'd treat any engineering system — with structure, reusability, and automation.

At its core, Foundry is three things.

First, it's a **library**. A curated collection of building blocks — personas, expertise modules, templates, and workflows. Twenty-four team member personas across four categories. Thirty-nine expertise domains, from Python to Kubernetes to HIPAA compliance. All of it open, all of it extensible.

Second, it's a **compiler**. You write a short YAML file that describes the team you want — which personas, what expertise, how they should operate. Foundry compiles that into a complete Claude Code project folder. Agents, instructions, templates, folder structure — everything, generated in seconds.

Third, it's an **orchestrator**. Foundry ships with what we call playbooks — multi-step agentic workflows that coordinate your AI team. Things like backlog refinement, parallel execution across multiple teams, and Trello integration. You don't just get a team — you get a team that knows how to operate.

Library. Compiler. Orchestrator. That's Foundry.

---

### 3. The Library (2.5 min)

[SCREEN: Terminal — Claude Code in Foundry project]

Let me show you what the library looks like. This is the ai-team-library directory — this is where all the building blocks live.

[ACTION: Navigate to ai-team-library/ and list contents]

Let's start with personas. These are the team members you can put on your AI team.

[ACTION: Navigate to ai-team-library/personas/ and list the directories]

There are twenty-four personas organized into four categories.

The biggest category is Software Development — fourteen personas. Your core team is here: Team Lead, Developer, Architect, Business Analyst, Tech QA. But also specialists you might not expect — a Database Administrator, a UX/UI Designer, a DevOps Engineer, even an Integrator whose whole job is merging work from multiple contributors.

Beyond software development, there are three more categories — Data and Analytics, Business Operations, and Compliance and Legal. Roles like Product Owner, Data Analyst, Legal Counsel, Security Engineer. Twenty-four personas in total, and you can see all of them listed here.

These aren't just labels. Each persona has a full constitution. Let me open one.

[ACTION: Open ai-team-library/personas/developer/persona.md]

This is the Developer persona. You can see it has a mission statement, a defined scope, operating principles, the inputs it expects, the outputs it produces, and how it collaborates with other personas. This is a complete role definition.

And each persona also has output specifications, prompt patterns, and templates.

[ACTION: Briefly show the outputs.md and templates/ directory]

Now let me show you expertise modules.

[ACTION: Navigate to ai-team-library/expertise/ and list the directories]

Thirty-nine expertise domains. Languages like Python, .NET, Java, Go, Rust. Platforms like AWS, Azure, GCP. Infrastructure like Kubernetes and Terraform. And compliance frameworks — HIPAA, GDPR, PCI-DSS, SOX, ISO 9000. You can scroll through the full list here.

Here's what's important about expertise — it's separate from personas. Expertise describes *what the team knows*, not *who they are*. When you attach Python expertise to your team, the Developer gets Python coding conventions, the Tech QA engineer gets Python testing patterns, the Architect gets Python architectural patterns. Same expertise, different lens depending on the role.

And this entire library is yours to extend — but we'll come back to that later.

---

### 4. Composing a Team (2 min)

[SCREEN: Terminal — Claude Code in Foundry project]

So we've seen the building blocks. Now let's compose a team.

[ACTION: Open examples/small-python-team.yml]

This is a composition file. It's YAML, and it's short — about forty lines. This is all Foundry needs to generate a complete project.

Let me walk through it.

At the top, we have the project section — just a name, a slug, and where to put the output.

Next is expertise. We're pulling in Python and Clean Code, in that order. The ordering matters — it controls how the knowledge is layered into the generated instructions.

Then the team. We're putting four personas on this team: Team Lead, Developer, Tech QA, and Code Quality Reviewer. For each one, we specify whether to generate an agent file, whether to include templates, and a strictness level.

There's a hooks section for policy enforcement. And a generation section with options like whether to seed initial tasks and write a manifest.

That's it. This is a complete team definition. It's declarative — you're describing *what* team you want, not *how* to build it.

[ACTION: Briefly show file listing of examples/ directory]

We ship several example compositions. There's a full-stack web team, a security-focused team, and this one — the foundry-dogfood composition. That's the team that builds Foundry itself. We eat our own cooking.

You can write a composition like this in a few minutes. Setting up the equivalent project by hand would take hours.

---

### 5. Generation (1 min)

[SCREEN: Terminal — Claude Code in Foundry project]

Let's compile this team.

[ACTION: Run `foundry-cli generate examples/small-python-team.yml --library ai-team-library`]

One command. Foundry reads the composition, pulls the building blocks from the library, and generates a complete Claude Code project.

[ACTION: Let the output scroll, briefly]

You can see it generating agent files, compiling the CLAUDE.md, copying templates, setting up the folder structure. This takes seconds.

There's also a GUI — if you run `foundry`, it launches a desktop application where you can compose teams visually.

[ACTION: Flash the Foundry GUI briefly — 3 seconds]

But for this demo, the CLI shows you exactly what's happening.

---

### 6. The Generated Output (2.5 min)

[SCREEN: Terminal — Claude Code in Foundry project]

Let's look at what we got.

[ACTION: cd into the generated project directory, list the structure]

This is a complete Claude Code project, ready to use. Let me walk through the key pieces.

[ACTION: Open the generated CLAUDE.md]

First, the CLAUDE.md. This is the master instruction file — it's what Claude Code reads when it starts up. Foundry composed this automatically from all the personas and expertise we selected. It has the project conventions, the team structure, the Python coding standards, the clean code principles — all woven together.

You didn't write a single line of this. It came from the library, assembled by the compiler.

[ACTION: Navigate to .claude/agents/ and list the files]

Next, agent files. Each persona on the team gets its own agent. Let me open two of them.

[ACTION: Open the developer agent file]

This is the Developer agent. It has the developer's mission, scope, responsibilities, and operating principles. It knows it's a developer. It knows how to collaborate with the other personas on the team.

[ACTION: Open the tech-qa agent file]

And this is the Tech QA agent. Completely different personality. Different responsibilities. Its job is to verify acceptance criteria, catch edge cases, write test plans. It's not going to try to do architecture. It's not going to try to write features. It knows its role.

That's the power of specialized agents versus one generalist. And when you need to work with a specific persona, you invoke their agent directly — you can ask the Developer to implement a feature, or ask Tech QA to write a test plan, and they'll respond in role.

[ACTION: Show the ai/ folder structure — ai/beans/, ai/outputs/, ai/context/]

And here's the workspace. The beans directory is where work items live. The outputs directory has a subfolder for each persona — that's where they put their deliverables. And context holds shared knowledge like architectural decisions.

Every project you generate from the same library will have this same consistent structure. Your developers can move between projects and immediately know where things are.

---

### 7. Claude Kit / Sharing Across Projects (2 min)

[SCREEN: Terminal — Claude Code in Foundry project]

Now, there's one more piece of the foundation I want to show you, and this is about scale.

What happens when you have five projects? Ten? All generated by Foundry, all using the same team structure. If you improve a playbook or add a new skill, do you have to regenerate every project?

No. That's what Claude Kit solves.

[ACTION: Show the .claude/ directory structure, pointing out kit/ and the symlinks]

Inside every generated project, there's a `.claude/kit/` directory. This is a git submodule — it points to a shared repository. All your projects can point to the same kit.

The kit contains the playbooks, skills, agent configurations, and hooks that are common across projects. The project-specific things — things unique to one project — live in `.claude/local/`, which overrides the kit when there's a name collision.

Everything connects automatically so Claude Code sees it all in its expected paths. It doesn't know or care that some of it comes from the kit and some from local.

[ACTION: Show claude-sync.sh briefly]

Updating is one command. `claude-sync.sh` pulls the latest kit changes and rebuilds the symlinks. You run it, and every improvement to your shared tooling is immediately available in that project.

So the model is: one team maintains the kit — your playbooks, your shared configurations, your quality standards. Every project that uses the kit benefits from every improvement. That's how you scale from one project to an organization.

---

## Act 2: Two Ways to Work (~14 min)

[SCREEN: Terminal — Claude Code in Foundry project]

We've built a team. We've compiled it into a project. Now let's put that team to work.

There are two ways to feed work into the system, and I want to show you both. The first is developer-driven — you're in Claude Code, brainstorming features, building a backlog, and running it through the system. The second is team-driven — work comes in through Trello from people who never touch a terminal, and the AI team picks it up automatically.

Let's start with the developer path.

---

### 8. The Bean Lifecycle (1.5 min)

[SCREEN: Terminal — Claude Code in Foundry project]

Before we start creating work, I need to explain one concept: the bean.

A bean is Foundry's unit of work. It could be a feature, a bug fix, an enhancement, an epic — any discrete piece of work that you want the AI team to deliver. The name is just our term for it. Think of it like a ticket or a story, but with more structure.

[ACTION: Open ai/beans/_bean-template.md]

Here's what a bean looks like. It has a title, a description, acceptance criteria, status, and metadata. It's a markdown file in a folder — nothing exotic.

Every bean goes through a lifecycle. It starts as **Unapproved** — someone created it, but nobody's committed to it yet. Then it gets **Approved** — we've decided this is worth building. Then **In Progress** — the team is actively working on it. And finally **Done** — the work is complete, tested, and merged.

[ACTION: Show ai/beans/_index.md briefly]

There's a backlog index that tracks every bean and its current status. This is what the Team Lead reads to decide what to work on next.

When a bean gets picked up, the Team Lead decomposes it into tasks and assigns them to the right personas. The Developer writes the code, Tech QA writes and runs the tests — every bean gets tested, that's mandatory. If the work needs it, the Business Analyst and Architect get pulled in too.

Beans are the currency of work in Foundry. Everything flows through them. Now let me show you how we create them.

---

### 9. Parallel Backlog Refinement (2.5 min)

[SCREEN: Terminal — three Claude Code windows side by side]

This is how I typically brainstorm new features. I'm going to open three Claude Code windows, all pointing at the same project, on the same branch.

[ACTION: Show three terminal windows arranged side by side, each with Claude Code open]

In each window, I'm going to run the same playbook — `/backlog-refinement`.

[ACTION: Type `/backlog-refinement` in each window]

Each of these is an independent Claude instance. They don't know about each other. Each one is going to have a conversation about what the project needs, analyze the current state of the code, and then create well-formed beans with acceptance criteria.

I typically get two to three beans per session. So across three windows, we'll end up with somewhere around six to nine new beans.

[ACTION: Hit enter to start `/backlog-refinement` in all three windows]

[FF — fast-forward through the AI work in all three windows]

[ACTION: Show the results — list the ai/beans/ directory to show the new beans created]

And there we go. We've got our new beans. Each one has a title, description, acceptance criteria — everything the team needs to start working.

Now, here's the thing. These three Claude instances were working independently. They didn't coordinate with each other. So it's entirely possible — even likely — that two of them independently decided the project needs similar features. Maybe two sessions both created a bean about error handling, or about input validation, with slightly different scope.

That's expected. And it's exactly what the next step handles.

---

### 10. Backlog Consolidation (2 min)

[SCREEN: Terminal — single Claude Code window]

Now I'm going to run a second playbook — `/backlog-consolidate`.

[ACTION: Type and run `/backlog-consolidate`]

This playbook reads every bean in the backlog and analyzes them for problems. It's looking for duplicates — two beans that describe the same thing. Scope overlaps — beans that partially cover the same ground. Contradictions — beans that conflict with each other. Merge candidates — beans that would be better as one. And missing dependencies — beans that should be ordered because one depends on the other.

[FF — fast-forward through the analysis]

[ACTION: Show the findings as they appear — grouped by severity]

You can see it found some issues. It's presenting them grouped by severity — critical, high, medium — and for each one, it shows the evidence. Here's an overlap it detected between these two beans.

[ACTION: Walk through one or two findings interactively — choose to merge one pair, delete a duplicate]

For this one, I'm going to merge these two beans — they're really the same feature described from slightly different angles. And this one is a straight duplicate, so I'll delete it.

[FF — fast-forward through the cleanup]

And now we have a clean backlog. No duplicates, no overlaps, clear dependencies. These beans are ready to be built.

At this point, I'd push to main. Let me do that now.

[ACTION: Push to main]

We're only committing bean definitions — markdown files. No code has been written yet. The code comes next.

---

### 11. Long Run — Parallel Execution (3 min)

[SCREEN: Remote Server — SSH terminal]

Now for the fun part.

I'm going to switch over to our build server. This is a remote machine with Claude Code installed, connected to the same repository. I use this for heavy execution because it can run multiple teams in parallel without tying up my local machine.

[ACTION: SSH into the remote server, cd to Foundry project directory]

I'm going to start tmux, which lets us see all five teams working side by side. And then I'm going to run the long run playbook.

[ACTION: Start tmux]
[ACTION: Type `/long-run --fast 5`]

`/long-run --fast 5`. That flag tells it to spin up five parallel teams.

Here's what's about to happen. Long Run reads the backlog and finds all the approved beans. It creates five git worktrees — these are isolated copies of the repository, one for each team. Then it spawns five Claude Code instances, each in its own tmux window. Each instance gets a Team Lead who picks up a bean, decomposes it into tasks, and coordinates the team through the work.

[ACTION: Show the tmux windows being created — five panes/windows appearing]

You can see the five teams spinning up. Each one is working on a different bean. They're completely isolated from each other — separate branches, separate working directories. No merge conflicts while they work.

As each team finishes a bean — the code is written, the tests pass, everything is verified — it merges the worktree back to main, cleans up, and the team picks up the next bean from the backlog.

We loaded about nine beans. With five teams running in parallel, the first five beans get picked up immediately. As teams finish, they grab the remaining four. The whole batch processes much faster than running them one at a time.

[FF — fast-forward through the parallel execution]

[ACTION: Show the results — completed beans, git log showing merges, run tests briefly]

And there it is. Nine features, built in parallel by five AI teams. Each one was implemented by a Developer, tested by Tech QA, and merged cleanly. We went from brainstorming ideas in three Claude Code windows to working, tested code — with minimal manual intervention.

Let me show you the second way to do this.

---

### Path B: Team-Driven (Trello)

That was the developer-driven path. You're in the terminal, you're running playbooks, you're directing the work.

But what if the work isn't coming from a developer? What if it's coming from your QA team filing bugs? Or a virtual assistant defining feature requests? Or a product manager prioritizing the roadmap? Those people aren't going to open a terminal and run backlog refinement. They need a different interface.

That's where Trello comes in.

---

### 12. Trello Board Setup (2 min)

[SCREEN: Trello — project board]

Let me switch over to our Trello board.

[ACTION: Show the full Trello board with all four lists visible]

This board has four lists, and they map directly to the workflow.

The first list is **Backlog**. This is the parking lot — ideas, feature requests, bugs, anything that someone thinks we might want to do. Anyone can add cards here. Your virtual assistant, your manual tester, your product manager — anyone with access to the board.

[ACTION: Click on a card in the Backlog list to show its contents]

Here's a card that a tester added — it's a bug report. Title, description, maybe a screenshot attached. That's all they had to write. They didn't need to know about beans, or acceptance criteria, or any of our internal structure. They just described the problem in plain language on a Trello card.

[ACTION: Close the card, point to the Sprint Backlog list]

The second list is **Sprint Backlog**. This is the commitment — these are the things we're going to build right now. Moving a card from Backlog to Sprint Backlog is a decision: "yes, we're doing this."

[ACTION: Drag 4-5 cards from Backlog to Sprint Backlog]

I'm going to pull a few cards over. These are the features and fixes we're committing to for this cycle.

The third and fourth lists — **In Progress** and **Completed** — are hands-off. You don't move cards into those lists manually. The system does it automatically. Let me show you how.

---

### 13. Trello-Driven Long Run (3 min)

[SCREEN: Remote Server — SSH terminal with tmux]

I'm switching back to the build server.

[ACTION: Show the tmux session, type `/long-run --fast 5`]

Same command as before — `/long-run --fast 5`. But this time, the beans aren't coming from backlog refinement sessions I ran in Claude Code. They're coming from Trello.

Here's what happens. Long Run connects to the Trello board and pulls every card from the Sprint Backlog list. For each card, it runs that card's information through backlog refinement — the same playbook we used earlier — to create a proper bean with structured acceptance criteria.

But here's the key difference. Because these cards came from the Sprint Backlog — someone already made the decision to commit to this work — the beans are auto-approved. They skip the Unapproved stage entirely and go straight to Approved, ready for execution.

As soon as a card is processed into a bean, it moves on the Trello board.

[SCREEN: Trello — project board]

[ACTION: Show the cards moving from Sprint Backlog to In Progress]

Watch the Sprint Backlog list. The cards are moving to In Progress. The system is telling everyone — including people who are just watching the Trello board — that this work has been picked up.

[SCREEN: Remote Server — tmux windows showing parallel teams]

Meanwhile, on the build server, five teams are processing beans in parallel. Same git worktrees, same tmux windows, same parallel execution we saw before.

And each bean knows where it came from. The metadata records which Trello board and which Trello card originated this work. Full traceability — you can always trace a piece of code back to the Trello card that requested it.

[FF — fast-forward through the parallel execution]

[SCREEN: Trello — project board]

[ACTION: Show the cards now in the Completed list]

And look at the board. The cards have moved from In Progress to Completed. The work is done. Code written, tests passing, merged to the main branch.

Think about what just happened. A virtual assistant wrote a Trello card describing a feature. A tester wrote a card describing a bug. Someone moved those cards to the Sprint Backlog. I ran one command. And five AI teams picked up those cards, turned them into structured work items, built the code, tested it, merged it, and moved the cards to done.

The person who wrote that Trello card never touched a terminal. They never heard of Claude Code. They just described what they needed, and the system delivered it.

That's the full loop.

---

## Act 3: Close (~3 min)

---

### 14. Customization / Extensibility (2 min)

[SCREEN: Terminal — Claude Code in Foundry project]

Before I wrap up, I want to address a question you're probably asking: "This is great, but my team isn't a Python team. We're building in Go. Or .NET. Or we have a compliance requirement you haven't covered."

The answer is — the library is yours to extend. Everything you've seen today is built from markdown files in folders. Adding to it works the same way.

[ACTION: Navigate to ai-team-library/personas/, show the directory listing]

Want to add a new persona? Create a folder. Add a `persona.md` with the role's mission, scope, and operating principles. Add an `outputs.md` describing what that role delivers. Add `prompts.md` with the prompt patterns. Optionally add templates. That's it — Foundry will pick it up in your next composition.

[ACTION: Navigate to ai-team-library/expertise/, show the directory listing]

Same with expertise. Need your team to know about a framework you use internally? A proprietary process? An industry regulation that's not in the library yet? Create a folder, add your topic files. The next time you compose a team with that expertise attached, every persona on the team gets that knowledge filtered through their role.

The library already covers a lot of ground. Thirty-nine expertise domains, including five compliance frameworks — HIPAA, GDPR, PCI-DSS, SOX, and ISO 9000. But the point isn't that we've covered everything. The point is that the system is designed so *you* can cover whatever you need.

Your custom personas compose with the built-in ones. Your custom expertise composes with the built-in expertise. Mix and match. A team with three of our standard personas and two of your custom ones, with a mix of built-in and proprietary expertise — that works.

The library is meant to grow with your organization.

---

### 15. Wrap-Up (1 min)

[SCREEN: Website — foundry-ai.io]

Let me bring it all together.

We started with a problem — Claude Code projects are manual, inconsistent, and don't scale. One agent trying to do everything. No reusable structure. No orchestration.

Foundry solves that in three layers.

You **build** a team by composing personas and expertise from a curated library. You can do that in minutes.

You **compile** that team into a complete Claude Code project — agents, instructions, templates, workspace — generated in seconds.

And you **orchestrate** work through that team using playbooks. Whether the work comes from a developer brainstorming in Claude Code or a virtual assistant writing a Trello card, the system picks it up, decomposes it, builds it in parallel, tests it, and delivers it.

And as your organization grows, Claude Kit lets you share your tooling across every project, and the library lets you extend it with your own domain knowledge.

That's Foundry. Compile your AI software team.

[ACTION: Hold on the website for a few seconds]

Thanks for watching. Visit foundry-ai.io to get started.

---

[END OF SCRIPT]
