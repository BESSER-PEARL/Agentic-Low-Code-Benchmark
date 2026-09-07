# Low-Code, Agentic, and Hybrid Software Development Benchmark

This repository contains the benchmark artifacts used to compare three software development approaches:

1. Pure low-code development
2. Pure agentic development
3. Hybrid agentic low-code development

The benchmark evaluates how these approaches perform when developing applications from natural-language requirements of increasing complexity and difficulty.

## Repository Structure

The repository contains two case studies. Each case study is organized into six requirement categories:

```text
.
├── README.md
│
├── hotel-booking/
│   ├── crud/
│   │   ├── nl-requirements/
│   │   ├── validation-tests/
│   │   └── low-code-model/
│   │
│   ├── constraints/
│   │   ├── nl-requirements/
│   │   ├── validation-tests/
│   │   └── low-code-model/
│   │
│   ├── complex-behaviour/
│   │   ├── nl-requirements/
│   │   ├── validation-tests/
│   │   └── low-code-model/
│   │
│   ├── edge-cases/
│   │   ├── nl-requirements/
│   │   ├── validation-tests/
│   │   └── low-code-model/
│   │
│   ├── conflicting/
│   │   ├── nl-requirements/
│   │   ├── validation-tests/
│   │   └── low-code-model/
│   │
│   └── non-functional/
│       ├── nl-requirements/
│       ├── validation-tests/
│       └── low-code-model/
│
└── nuclear-medicine-lung-cancer/
    ├── crud/
    ├── constraints/
    ├── complex-behaviour/
    ├── edge-cases/
    ├── conflicting/
    └── non-functional/
```

Each requirement category contains three types of artifacts:

- **`nl-requirements/`** — the natural-language requirements provided as input to the development approaches.
- **`validation-tests/`** — the acceptance tests used to validate the resulting applications.
- **`low-code-model/`** — the low-code model used as an additional input for the pure low-code development process.

## Application Categories

The benchmark progressively introduces different types of requirements and challenges.

### 1. CRUD — Basic Requirements

A simple CRUD application covering the core functionality of the case study.

This category establishes the basic functionality required to implement the application, including the creation, retrieval, modification, and deletion of the main domain entities.

### 2. Constraints — Validation and Business Rules

The basic application is extended with additional validation constraints and domain-specific business rules.

These requirements introduce conditions that must be satisfied by the application beyond basic CRUD functionality.

### 3. Complex Behaviour — Dynamic Calculations

Requirements involving more complex dynamic calculations are introduced.

This category evaluates the ability of the development approaches to implement functionality whose behavior depends on application data, relationships, or runtime conditions.

### 4. Edge Cases — Unconventional and Edge Cases

Requirements include unusual and edge-case scenarios that may be counterintuitive for agentic models.

This category focuses on less common situations and requirements that may challenge the ability of automated development approaches to correctly interpret and implement the specification.

### 5. Conflicting — Defective Requirements

The requirements contain inconsistencies, omissions, and conflicts, resulting in potential goal conflicts.

This category evaluates how the different development approaches handle requirements that are not fully consistent or that may admit conflicting interpretations.

### 6. Non-Functional Requirements

Additional requirements address aspects such as style, colors, accessibility, and multilingual support.

This category evaluates requirements that concern qualities and characteristics of the application beyond its core functional behavior.