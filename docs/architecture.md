# Driver Dynamics Lab – Software Architecture

## Vision

Driver Dynamics Lab (DDL) is a data-driven platform for vehicle dynamics,
sim racing, motorsport and real-world vehicle knowledge.

The software is built around one central principle:

> Every data source is imported into one unified data model.

---

# High Level Architecture

External Data
│
├── Assetto Corsa
├── Assetto Corsa EVO
├── BeamNG
├── ACC
├── GT7
├── Real Vehicle Data
└── Future Sources

↓

Import Engine

↓

DDL Domain Model

↓

Database

↓

Applications

├── Website
├── Desktop
├── API
└── AI

---

# Core Principles

- Single Source of Truth
- Clean Architecture
- Modular Design
- Data First
- Test Driven
- No Duplicate Data