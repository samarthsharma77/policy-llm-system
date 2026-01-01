"""
Decision Engine for the Controlled Enterprise Policy LLM System.

This module defines the central controller responsible for all
decision-making within the system. The controller determines
whether a user query should be answered or explicitly refused.

The controller enforces:
- Strict policy-domain boundaries
- Role-based access control
- Document-grounded answer generation
- Confidence-based decision-making between answering and refusal
- Traceable and auditable decision outcomes

Refusal is treated as a first-class, correct outcome whenever
a query is ambiguous, unsupported by policy documents, or
falls outside the defined system scope.
"""


# Controller Responsibilities:
# 1. Validate that the query falls within the policy domain.
# 2. Enforce role-based access (employee vs pre-joining candidate).
# 3. Decide whether document retrieval is required.
# 4. Execute retrieval and evaluate evidence sufficiency.
# 5. Decide whether generation is permitted based on confidence.
# 6. Trigger answer generation when allowed.
# 7. Verify grounding of the generated answer.
# 8. Produce a final decision: ANSWER or REFUSE.
# 9. Log all intermediate decisions for auditability.

# Controller Inputs:
# - user_query: str
# - user_role: str  ("employee" or "pre_joining_candidate")

# Controller Outputs:
# - decision: str   # "ANSWER" or "REFUSE"
# - answer: Optional[str]
# - refusal_reason: Optional[str]
# - supporting_documents: Optional[list]

# Refusal Conditions (non-exhaustive):
# - Query is outside defined policy scope
# - Query violates role-based access rules
# - No relevant policy documents retrieved
# - Retrieved evidence confidence below threshold
# - Generated answer is not sufficiently grounded

# High-Level Decision Flow:
#
# 1. Receive user query and role.
# 2. Perform domain validation.
#    - If invalid -> REFUSE.
# 3. Apply role-based constraints.
#    - If violation -> REFUSE.
# 4. Retrieve relevant policy documents.
#    - If none -> REFUSE.
# 5. Evaluate retrieval confidence.
#    - If below threshold -> REFUSE.
# 6. Generate answer using controlled prompt.
# 7. Verify answer grounding against retrieved documents.
#    - If grounding fails -> REFUSE.
# 8. Return ANSWER with supporting evidence.

def is_policy_domain_query(user_query:str)->bool:
    """
    Gate 1: Deterministic policy-domain validation.

    This function performs a conservative, rule-based check to
    determine whether a query is eligible for further processing
    by the system.

    NOTE:
    This gate is intentionally strict and explainable.
    Future stages may augment this check with semantic or
    LLM-based intent classification as secondary decision layers.
    """

    if not user_query or not user_query.strip():
        return False

    query=user_query.lower().strip()

    # Hard rejection patterns (always refuse)
    rejection_signals=[
        "should i",
        "do you think",
        "is it fair",
        "what happens if",
        "will i",
        "my salary",
        "my manager",
        "recommend",
        "opinion",
        "best way",
        "what should i do",
    ]

    for signal in rejection_signals:
        if signal in query:
            return False

    # Policy domain keywords (allowlist)
    policy_keywords=[
        "policy",
        "leave",
        "vacation",
        "pto",
        "probation",
        "notice period",
        "benefits",
        "insurance",
        "reimbursement",
        "compliance",
        "code of conduct",
        "work hours",
        "remote",
        "hybrid",
        "hr",
        "onboarding",
    ]

    for keyword in policy_keywords:
        if keyword in query:
            return True

    return False

# NOTE:
# Role-based access is intentionally conservative.
# More granular authorization can be layered in future iterations.
def is_role_authorized(user_query: str, user_role: str) -> bool:
    """
    Gate 2: Role-based access control.

    Determines whether a user is authorized to receive an answer
    based on their role and the sensitivity of the policy topic.
    """
    if not user_query or not user_query.strip():
        return False

    if user_role not in {"employee", "pre_joining_candidate"}:
        return False

    query=user_query.lower().strip()

    # Topics restricted to internal employees only
    employee_only_topics=[
        "disciplinary action",
        "internal investigation",
        "performance review",
        "appraisal",
        "salary structure",
        "internal reimbursement",
        "it access",
        "system access",
        "vpn",
        "internal policy",
        "escalation process",
    ]

    # Topics safe for all users (including pre-joining candidates)
    public_policy_topics=[
        "leave",
        "vacation",
        "probation",
        "notice period",
        "work hours",
        "code of conduct",
        "benefits",
        "insurance",
        "onboarding",
        "joining documents",
    ]

    # Pre-joining candidates are restricted from employee-only topics
    if user_role=="pre_joining_candidate":
        for topic in employee_only_topics:
            if topic in query:
                return False

    # Allow if query matches public policy topics
    for topic in public_policy_topics:
        if topic in query:
            return True

    # Default: refuse
    return False

# NOTE:
# Retrieval is only attempted for queries that are expected to have
# a concrete, document-grounded answer.

def should_retrieve_documents(user_query: str) -> bool:
    """
    Gate 3: Retrieval decision.

    Determines whether a query is sufficiently specific and factual
    to justify retrieving policy documents.
    """

    if not user_query or not user_query.strip():
        return False

    query=user_query.lower().strip()

    # Reject interpretive or speculative intent
    interpretive_signals=[
        "why",
        "intent",
        "reason",
        "what happens if",
        "explain why",
        "should",
    ]

    for signal in interpretive_signals:
        if signal in query:
            return False

    # Reject vague or overly broad queries
    vague_signals=[
        "tell me about",
        "overview",
        "everything",
        "all policies",
        "general rules",
    ]

    for signal in vague_signals:
        if signal in query:
            return False

    # Allow factual or procedural policy queries
    factual_signals=[
        "what is",
        "how many",
        "how long",
        "when does",
        "process",
        "procedure",
        "steps",
        "policy on",
        "is there",
    ]

    for signal in factual_signals:
        if signal in query:
            return True

    return False

# NOTE:
# Evidence sufficiency is intentionally conservative.
# Retrieval success does not imply answerability.

def retrieve_and_evaluate_evidence(user_query: str, vector_store, top_k: int = 5) -> dict:
    """
    Gate 4: Retrieval execution and evidence sufficiency check.

    Executes vector-based retrieval and determines whether the
    retrieved documents provide sufficient evidence to justify
    answer generation.
    """
    # Execute retrieval (FAISS)
    retrieved_docs=vector_store.search(user_query,top_k=top_k)

    if not retrieved_docs:
        return{
            "documents": [],
            "evidence_score": 0.0,
            "sufficient": False,
        }
    
    # Extract similarity scores
    scores = [doc["score"] for doc in retrieved_docs]

    # Conservative sufficiency rules
    MIN_DOCS = 2
    MIN_SCORE = 0.6

    sufficient = (
        len(retrieved_docs) >= MIN_DOCS
        and max(scores) >= MIN_SCORE
    )

    evidence_score = sum(scores) / len(scores)

    return {
        "documents": retrieved_docs,
        "evidence_score": evidence_score,
        "sufficient": sufficient,
    }


# NOTE:
# The LLM is treated as a constrained text transformation component,
# not as a source of knowledge.

def generate_controlled_answer(user_query:str, evidence_documents:list, llm_client)->dict:
    """
    Gate 5: Controlled answer generation.

    Generates an answer strictly grounded in retrieved policy
    documents. The model is not permitted to use external knowledge.
    """

    if not evidence_documents:
        return{
            "answer":None,
            "used_documents":[],
            "generation_status":"INSUFFICIENT_EVIDENCE",
        }
    
    system_prompt=( 
        "You are a policy answer generation component.\n"
        "Rules:\n"
        "- Use only the provided policy excerpts.\n"
        "- Do not use external knowledge.\n"
        "- Do not interpret or extend policies.\n"
        "- If the documents do not fully answer the question, respond with:\n"
        "  INSUFFICIENT_EVIDENCE\n"
        "- Do not provide advice or opinions.\n"
    )

    user_prompt=(
        f"Question:\n{user_query}\n\n"
        f"Policy Documents:\n{evidence_documents}"
    )

    response = llm_client.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt
    )

    if not response or response.strip()=="INSUFFICIENT_EVIDENCE":
        return{
            "answer":None,
            "used_documents":evidence_documents,
            "generation_status":"INSUFFICIENT_EVIDENCE",
        }

    return {
        "answer": response,
        "used_documents": evidence_documents,
        "generation_status": "GENERATED",
    }


# NOTE:
# Generation does not imply correctness.
# Final acceptance is based on grounding and confidence thresholds.

def verify_answer_grounding_and_confidence(generated_answer: str,evidence_documents: list,evidence_score: float)->dict:
    """
    Gate 6: Post-generation grounding verification and confidence scoring.

    Determines whether a generated answer is sufficiently grounded
    in retrieved documents to be safely returned to the user.
    """

    if not generated_answer or generated_answer.strip()=="INSUFFICIENT_EVIDENCE":
        return{
            "final_decision":"REFUSE",
            "confidence_score":0.0,
            "refusal_reason":"Model reported insufficient evidence",
        }
    
    # Normalization
    answer_tokens=set(generated_answer.lower().split())

    doc_text=" ".join(doc.get("text","") for doc in evidence_documents).lower()
    doc_tokens=set(doc_text.split())

    if not doc_tokens:
        return{
            "final_decision":"REFUSE",
            "confidence_score":0.0,
            "refusal_reason":"No document text available for grounding",
        }
    
    # Token overlap
    overlap_tokens=answer_tokens.intersection(doc_tokens)
    overlap_score=len(overlap_tokens)/max(len(answer_tokens),1)

    # Length check
    if(len(generated_answer)>2*len(doc_text)):
        return{
            "final_decision":"REFUSE",
            "confidence_score":overlap_score,
            "refusal_reason":"Answer length exceeds supporting evidence",
        }
    
    # Confidence calculation
    confidence_score=(0.6*evidence_score)+(0.4*overlap_score)

    CONFIDENCE_THRESHOLD=0.7

    if confidence_score<CONFIDENCE_THRESHOLD:
        return{
            "final_decision":"REFUSE",
            "confidence_score":confidence_score,
            "refusal_reason":"Grounding confidence below threshold",
        }

    return{
        "final_decision":"ANSWER",
        "confidence_score":confidence_score,
        "refusal_reason":None,
    }


# Final Controller Function
def handle_user_query(user_query:str,user_role:str,vector_store,llm_client)->dict:
    """
    Main controller orchestration function.

    Executes all decision gates in order and returns
    a final ANSWER or REFUSE decision.
    """

    # Gate 1: Policy domain validation
    if not is_policy_domain_query(user_query):
        return{
            "decision":"REFUSE",
            "answer":None,
            "refusal_reason":"Query outside policy domain",
            "confidence_score":0.0,
        }
    
    # Gate 2: Role-based access control
    if not is_role_authorized(user_query, user_role):
        return{
            "decision":"REFUSE",
            "answer":None,
            "refusal_reason":"User not authorized for this policy query",
            "confidence_score":0.0,
        }
    
    # Gate 3: Retrieval decision
    if not should_retrieve_documents(user_query):
        return{
            "decision":"REFUSE",
            "answer":None,
            "refusal_reason":"Query not suitable for document-based answering",
            "confidence_score":0.0,
        }
    
    # Gate 4: Retrieval + evidence sufficiency
    retrieval_result=retrieve_and_evaluate_evidence(
        user_query=user_query,
        vector_store=vector_store,
    )

    if not retrieval_result["sufficient"]:
        return{
            "decision":"REFUSE",
            "answer":None,
            "refusal_reason":"Insufficient policy evidence",
            "confidence_score":retrieval_result["evidence_score"],
        }
    
    # Gate 5: Controlled generation
    generation_result=generate_controlled_answer(
        user_query=user_query,
        evidence_documents=retrieval_result["documents"],
        llm_client=llm_client,
    )

    if generation_result["generation_status"]!="GENERATED":
        return{
            "decision":"REFUSE",
            "answer":None,
            "refusal_reason":"Model could not generate grounded answer",
            "confidence_score":retrieval_result["evidence_score"],
        }
    


    # Gate 6: Grounding + confidence
    verification_result=verify_answer_grounding_and_confidence(
        generated_answer=generation_result["answer"],
        evidence_documents=retrieval_result["documents"],
        evidence_score=retrieval_result["evidence_score"],
    )

    if verification_result["final_decision"]!="ANSWER":
        return{
            "decision":"REFUSE",
            "answer":None,
            "refusal_reason":verification_result["refusal_reason"],
            "confidence_score":verification_result["confidence_score"],
        }
    
    # FINAL ANSWER
    return{
        "decision":"ANSWER",
        "answer":generation_result["answer"],
        "refusal_reason":None,
        "confidence_score":verification_result["confidence_score"],
    }

