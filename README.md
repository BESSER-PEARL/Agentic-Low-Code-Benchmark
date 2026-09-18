# Low-Code, Agentic, and Hybrid Software Development Benchmark

This repository contains the benchmark artifacts used to compare three software development approaches:

1. Pure low-code development
2. Pure agentic development
3. Hybrid agentic low-code development

The benchmark evaluates how these approaches perform when developing applications from natural-language requirements of increasing complexity and difficulty.

## Repository Structure

The repository contains two case studies. Each case study is organized into five requirement categories:

```text
.
├── README.md
│
├── hotel-booking/
│   ├── 1-CRUD-and-dynamic-calculations/
│   │   ├── nl-requirements/
│   │   ├── validation-tests/
│   │   └── low-code-model/
│   │
│   ├── 2-validation-and-business-rules/
│   │   ├── nl-requirements/
│   │   ├── validation-tests/
│   │   └── low-code-model/
│   │
│   ├── 3-edge-cases/
│   │   ├── nl-requirements/
│   │   ├── validation-tests/
│   │   └── low-code-model/
│   │
│   ├── 4-non-functional/
│   │   ├── nl-requirements/
│   │   ├── validation-tests/
│   │   └── low-code-model/
│   │
│   └── 5-defective/
│       ├── nl-requirements/
│       ├── validation-tests/
│       └── low-code-model/
│
└── nuclear-medicine-lung-cancer/
    ├── 1-CRUD-and-dynamic-calculations/
    ├── 2-validation-and-business-rules/
    ├── 3-edge-cases/
    ├── 4-non-functional/
    └── 5-defective/
```

Each requirement category contains three types of artifacts:

- **`nl-requirements/`** — the natural-language requirements provided as input to the development approaches.
- **`validation-tests/`** — the acceptance tests used to validate the resulting applications.
- **`low-code-model/`** — the low-code model used as an additional input for the pure low-code development process.

## Application Categories

The benchmark progressively introduces different types of requirements and challenges.

### 1. CRUD Baseline with Dynamic Calculations

A simple data-centric application description (creating, reading, updating, and deleting), including derived or computed values (e.g., automatically updating a project's budget allocation when a sub-item changes).

This category establishes the basic functionality required to implement the application, including the creation, retrieval, modification, and deletion of the main domain entities, together with the dynamic calculations whose behavior depends on application data, relationships, or runtime conditions.

### 2. Validation and Business Rules

Requirements expressing semantic constraints across attributes or entities (e.g., an allocation cannot exceed the remaining budget), which stress the expressiveness of a platform's constraint language.

These requirements introduce conditions that must be satisfied by the application beyond basic CRUD functionality.

### 3. Unconventional Requirements and Edge Cases

Requirements describing atypical or boundary scenarios that can be counter-intuitive for agentic models to infer correctly without explicit guidance, and that are not always anticipated by a platform's default generators.

This category focuses on less common situations and requirements that may challenge the ability of automated development approaches to correctly interpret and implement the specification.

### 4. Non-Functional Requirements

Requirements concerning style, color scheme, accessibility, multi-language support, and similar cross-cutting qualities, which are typically outside the scope of deterministic low-code generation.

This category evaluates requirements that concern qualities and characteristics of the application beyond its core functional behavior.

### 5. Defective Requirements

Specifications deliberately containing an inconsistent, incomplete, or conflicting requirement, representing the most challenging condition and the one most likely to expose differences in how each approach handles ambiguity or contradiction.

This category evaluates how the different development approaches handle requirements that are not fully consistent or that may admit conflicting interpretations.