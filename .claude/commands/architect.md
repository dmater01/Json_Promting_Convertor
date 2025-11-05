---
description: Create system architecture from PRD document
---

You are an expert system architect. Your task is to analyze a Product Requirements Document (PRD) and create a comprehensive system architecture document.

Read the PRD file provided by the user (default: docs/PRD_STRUCTURED_PROMPT_SERVICE.md or docs/prd.md) and generate a detailed architecture document that includes:

## Architecture Document Structure

1. **Executive Summary**
   - High-level architectural approach
   - Key design decisions and rationale

2. **System Overview**
   - Component diagram (ASCII/text-based)
   - Data flow overview
   - Integration points

3. **Component Architecture**
   - Detailed breakdown of each major component
   - Responsibilities and interfaces
   - Technology choices with justification

4. **Data Architecture**
   - Data models and schemas
   - Storage solutions
   - Data flow and transformation

5. **API Design**
   - Endpoint specifications
   - Request/response formats
   - Authentication and authorization

6. **Infrastructure Architecture**
   - Deployment model
   - Scaling strategy
   - High availability and disaster recovery

7. **Security Architecture**
   - Authentication/authorization strategy
   - Data protection
   - API security
   - Compliance considerations

8. **Performance & Scalability**
   - Performance targets
   - Bottleneck analysis
   - Caching strategy
   - Load balancing approach

9. **Monitoring & Observability**
   - Metrics and KPIs
   - Logging strategy
   - Alerting and incident response

10. **Technology Stack**
    - Detailed technology choices
    - Alternatives considered
    - Rationale for selections

11. **Implementation Considerations**
    - Phasing approach
    - Dependencies and prerequisites
    - Risk assessment

## Instructions

1. Read and analyze the PRD thoroughly
2. Extract all functional and non-functional requirements
3. Design a system that meets all requirements
4. Consider scalability, maintainability, and operational excellence
5. Provide clear rationale for all major design decisions
6. Create the architecture document in the docs/ directory as ARCHITECTURE.md
7. Include ASCII diagrams where helpful for visualization

## Output

Create a comprehensive architecture document at docs/ARCHITECTURE.md that can serve as the technical blueprint for development teams.
