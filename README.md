# Bachelor Thesis: Connection Migration and Multipath Communication in QUIC

This repository contains the source material for my bachelor thesis on
connection migration and multipath support in the QUIC transport protocol.

The thesis is developed concurrently with an implementation-focused QUIC
prototype project. Practical observations from the prototype help inform the
analysis, while this repository focuses on a literature-driven examination of
protocol design choices and trade-offs.

| Role | Name | Affiliation |
|------|------|-------------|
| Author | Ki Chun Tong | Aalto University |
| Thesis Advisor | Pasi Sarolahti | Aalto University |

## Background

Modern devices frequently move between networks, such as switching from Wi-Fi
to cellular or roaming across access points, while applications are expected to
remain responsive. Traditional transport protocols like TCP bind a connection
to a fixed network path defined by IP addresses and ports, which forces
reconnection when the network changes.

QUIC addresses this limitation by decoupling connection identity from the
underlying network path and supporting connection migration. Ongoing
standardization work further extends QUIC with multipath support, which allows a
single connection to use multiple network paths simultaneously to improve
robustness, performance, and handover behavior.

This thesis examines how connection migration and multipath support are designed
and realized in QUIC, with a focus on protocol mechanisms, design trade-offs, and
practical implications. The work is primarily literature-based and grounded in
IETF specifications, with a small exploratory evaluation used to relate
specification mechanisms to observable behavior.

## Scope and Goals

The main goals of this thesis are:

- Understand the design rationale behind QUIC connection migration
- Study current Multipath QUIC proposals and standardization efforts
- Relate protocol design decisions to observed behavior in practice
- Identify open challenges and trade-offs in multipath transport over QUIC

## Writing and Build Workflow

- The thesis is written as individual Markdown files
- Documents are compiled using pandoc
- A Makefile-based build (with optional CMake support) is used to assemble the final document
- Figures and plots are generated separately and included during compilation
- Citations are managed in Zotero and exported as BibLaTeX when needed

The repository is structured to keep content modular and iteration-friendly.

## Repository Structure

```
.
├── thesis/        # Markdown source files for the thesis
├── notes/         # Reading notes and literature summaries
├── experiments/   # Optional scripts and exploratory experiments
├── figures/       # Generated plots and diagrams
├── build/         # Build artifacts (ignored)
├── Makefile       # Build orchestration
└── README.md
```

## Status

Current status: **Planning / Literature review**

## Key Deadlines

| Date | Milestone |
|------|-----------|
| 29 Jan | Research plan due (23:59) |
| 13 Feb | First draft (33%) due (23:59) |
| 13 Mar | Second draft (66%) due (23:59) |
| 10 Apr | Third draft due (23:59) |
| 13 Apr – 24 Apr | Final presentations |
| 24 Apr | Final thesis due (23:59) |

## Work Plan Overview

The thesis follows a structured seminar timeline (weeks 4–17):

- **Weeks 4–6 (late Jan – mid Feb):**  
  Literature review setup, research plan, QUIC migration background, first draft.

- **Weeks 7–10 (mid Feb – mid Mar):**  
  Expanded literature review, Multipath QUIC, design trade-offs, second draft.

- **Weeks 11–13 (mid Mar – early Apr):**  
  Revisions, evaluation design, testbed setup.

- **Weeks 14–16 (Apr):**  
  Exploratory experiments, final writing, presentations, and submission.

- **Week 17 (late Apr):**  
  Seminar reflection and course completion.

Advisor meetings are held approximately biweekly.

## References

Primary sources include IETF RFCs and Internet-Drafts related to QUIC and
Multipath QUIC, as well as academic publications on transport protocols and
mobile networking.
