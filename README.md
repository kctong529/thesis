# Bachelor Thesis: Connection Migration and Multipath Communication in QUIC

This repository contains the source material for my bachelor thesis on
connection migration and multipath communication in the QUIC transport protocol.

The thesis is developed alongside an implementation-focused QUIC prototype project. Practical observations from the prototype help inform the analysis, while this repository focuses on a literature-driven examination of protocol design choices, trade-offs, and deployment considerations.

| Role | Name | Affiliation |
|------|------|-------------|
| Author | Ki Chun Tong | Aalto University |
| Thesis Advisor | Pasi Sarolahti | Aalto University |

## Background and Motivation

The original Internet architecture was designed with the assumption that IP addresses are static and globally unique, and that hosts remain attached to a single network during the lifetime of a connection. This assumption was largely valid in early fixed-network environments.

Over time, host mobility became more common. Mobile devices regularly switch between Wi-Fi and cellular networks, and even fixed hosts may experience address changes due to NAT rebinding or provider changes. These developments invalidate the original assumptions and make transport connections fragile under address changes.

Several network-layer solutions were proposed to address host mobility, such as Mobile IP and the Host Identity Protocol (HIP). While these approaches were technically valid, they have faced deployment challenges in the open Internet, including infrastructure requirements, middlebox interference, and limited adoption.

At the same time, hosts have become increasingly multihomed, with multiple network interfaces and IP addresses available simultaneously. This is true both for mobile devices (e.g. Wi-Fi + cellular) and fixed environments such as enterprises and datacenters. To address this, transport-layer solutions such as SCTP and Multipath TCP were developed to enable communication over multiple paths.

More recently, HTTP/3 was introduced to improve web performance and reliability. Together with HTTP/3, QUIC was developed as a new transport protocol on top of UDP. Unlike earlier transport protocols, QUIC separates connection identification from IP addressing, enabling connection migration as a fundamental design feature rather than an extension.

## Scope and Goals

This thesis studies how mobility and multihoming challenges are addressed at the transport layer, with a focus on QUIC.

The main goals of this work are to:

- Explain why mobility and multihoming cause problems in the traditional Internet architecture
- Review earlier solutions and their limitations
- Describe how QUIC and HTTP/3 address these challenges by design
- Analyze QUIC connection migration mechanisms and their practical implications
- Discuss deployment considerations, including NATs, firewalls, and path failure
- Identify open challenges and trade-offs in current designs

While Multipath QUIC is discussed, it is treated as work in progress in the IETF. Simultaneous multipath support is a separate work item from connection migration, and its specifications and implementations are still evolving. As a result, multipath is covered at a high level, with emphasis on design intent and open issues rather than full performance evaluation.

An additional focus area is connection migration triggering: how implementations detect path changes, decide when migration is needed, and whether external signals (e.g. link monitoring) could assist these decisions.

## Thesis Structure

The thesis is structured as follows:

1. Introduction  
Motivation, context, and research goals.

2. Mobility and Multihoming in the Internet  
Why mobility and multihoming are problematic in the original Internet design and how earlier solutions attempted to address them.

3. HTTP/3 and QUIC Overview  
General architecture and design principles of HTTP/3 and QUIC relevant to mobility.

4. Connection Migration and Extensions in QUIC  
QUIC connection migration mechanisms, migration triggers, deployment considerations, and an overview of multipath extensions.

5. Exploratory Evaluation  
A small set of controlled scenarios that illustrate migration behavior and highlight practical consequences of the mechanisms described earlier.

6. Conclusions  
Summary of findings, limitations, and future work.

## Writing and Build Workflow

The repository uses a metadata-driven, reproducible build pipeline designed for iterative writing and CI-friendly builds.

- Thesis content is written in Markdown, organized by chapter and section
- Chapter and section skeletons are generated using a custom script
- Thesis metadata (title, abstract, keywords, degree info) is defined in `metadata.yaml`
- Metadata is compiled into LaTeX and PDF metadata automatically
- The final document is built using pandoc -> LaTeX -> pdfLaTeX, targeting the official Aalto University thesis class
- A Makefile orchestrates the full build pipeline

## Repository Structure

```
.
├── chapters/           # Thesis chapters (Markdown + config.yaml)
├── notes/              # Reading notes and literature summaries
├── experiments/        # Exploratory scripts and test setups
├── figures/            # Generated plots and diagrams
├── metadata.yaml       # Thesis metadata
├── extract_metadata.py # Metadata -> LaTeX/PDF generator
├── gen_thesis.py       # Chapter and section scaffold generator
├── Makefile            # Build orchestration
├── build/              # Build artifacts (ignored)
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
  Expanded literature review, QUIC connection migration, multipath-related design considerations, second draft.

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
