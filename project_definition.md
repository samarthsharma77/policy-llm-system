# Project Title

Controlled LLM System for Enterprise Policy Intelligence

## Target Users

- Internal enterprise employees
- Pre-joining candidates

## Problem Statement

In mid-sized and large organizations—and increasingly in smaller companies—employees and pre-joining candidates frequently raise questions related to:

- Company policies
- HR rules
- Compliance guidelines
- Employee benefits and perks

Existing internal solutions for addressing these queries typically rely on document repositories or basic LLM-powered chatbots. While such tools can retrieve or generate responses, they often lack reliability, clarity, and decision control.

In policy-driven domains, incorrect or overconfident answers can lead to compliance risks, employee confusion, and poor organizational decision-making.

Critically, most chatbot-based solutions do not handle uncertainty effectively. They tend to respond even when information is missing, ambiguous, or outside defined policy scope—situations where refusal or clarification would be the correct behaviour.

## In-Scope Query Types

The system will answer only policy-governed, rule-based questions supported by official documentation.

### HR and Employment Policies
- What is the leave policy during the probation period?
- How many casual and sick leaves are allowed per year?
- What is the notice period for resignation?
- Is there a probation period, and how long does it last?
- What is the company policy on moonlighting?
- What are the working hours and overtime rules?
- What is the policy for remote or hybrid work?
- Are employees allowed to work from outside the country?

### Employee Benefits and Perks
- When does health insurance coverage start?
- What benefits are available during probation?
- What is the travel reimbursement policy?
- What expenses are eligible for reimbursement?
- Is there a relocation allowance or joining bonus policy?
- What perks are available to full-time employees?

### Compliance and Conduct
- What is the company’s code of conduct?
- What actions are considered policy violations?
- What is the policy on data privacy and confidentiality?
- What disciplinary actions are defined for non-compliance?
- What is the company policy on workplace harassment?

### Security and IT Policies
- What security training is mandatory for employees?
- What is the process to request access to internal systems?
- What are the guidelines for handling confidential data?
- What is the policy for using personal devices at work?

### Onboarding and Pre-Joining Policies
- What documents are required before joining the company?
- When does salary processing begin for new employees?
- What benefits apply during the onboarding phase?
- What policies apply before the official joining date?

All answers must be:
- Derived from official documents
- Grounded in retrieved policy sections
- Refused if sufficient evidence is unavailable

## Out-of-Scope Query Types

The system will explicitly refuse to answer the following categories of queries.

### Hiring and Recruitment Decisions
- Should I be hired for this role?
- Why was my application rejected?
- Who is the best candidate for this position?
- How are interview scores evaluated?

### Policy Exceptions and Approvals
- Can I get an exception to the leave policy?
- Will my manager approve extended remote work?
- Can HR waive the notice period for me?

### Personal or Employee-Specific Data
- What is my salary or appraisal status?
- How many leaves have I personally used?
- What is my manager’s private feedback about me?

### Opinions, Advice, or Interpretation
- Is this policy fair?
- What should I do in this situation?
- Do you think this rule should be changed?

### Unsupported or Speculative Queries
- What policy changes will happen next year?
- What would happen if I break this rule?
- What is the best way to bypass this policy?

### Non-Policy Company Information
- Who is working on which project?
- What is the company’s future roadmap?
- Internal discussions not documented as policy

## Core System Guarantees

The system enforces the following guarantees at all times:

- Responses are generated only when fully supported by retrieved official policy documents.
- Each query is evaluated using retrieval relevance and grounding signals, and answered only if confidence exceeds a predefined threshold.
- Queries with insufficient, ambiguous, or missing evidence result in explicit refusal rather than speculative output.
- Strict domain boundaries are enforced regardless of linguistic similarity or user intent.
- The system does not interpret policies, provide opinions, or suggest exceptions.
- Every interaction is logged with the user query, retrieved document sections, and the final decision.
- Responses are filtered based on user role (pre-joining candidate or employee).
- Model selection is treated as an interchangeable component, enabling controlled routing and replacement.
- Reliability and safety are prioritized over query coverage.

## Non-Goals

The following are explicitly out of scope:

- Training or fine-tuning language models
- Automating or influencing hiring or HR decisions
- Providing personalized employee data
- Granting approvals or policy exceptions
- Acting as a general-purpose company assistant
- Providing legal, financial, or personal advice
- Replacing human judgment in compliance processes

## Success Criteria

The project is considered successful if:

- The system consistently refuses unsupported or ambiguous queries.
- All answers are traceable to specific policy document sections.
- Confidence thresholds reliably separate answerable queries from refusal cases.
- Answer and refusal behavior is consistent and predictable.
- Role-based access control is correctly enforced.
- All interactions are logged for traceability.
- System behavior can be clearly explained without referencing model internals.
- The system runs reproducibly inside a documented virtual environment.

## Summary

This project implements a controlled LLM-based system for answering enterprise policy-related questions for internal employees and pre-joining candidates. The system prioritizes document grounding, confidence-based decision-making, and explicit refusal over unrestricted generation. By enforcing strict scope boundaries, role-aware access, and traceable decision logic, the project demonstrates how large language models can be safely and responsibly deployed in policy-driven enterprise environments.