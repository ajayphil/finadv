from .llm_client import OpenRouterClient
from .rag_store import TabularRAG

# lazily create RAG store
rag = TabularRAG()


def _get_llm():
    try:
        return OpenRouterClient()
    except Exception:
        # fallback dummy LLM for local testing when API key not present
        class DummyLLM:
            def chat(self, messages, model=None, max_tokens=None):
                return "[MOCK LLM RESPONSE]"

        return DummyLLM()


def _call_llm_with_context(system_prompt, user_prompt, retrieved_contexts=None):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if retrieved_contexts:
        messages.append({"role": "system", "content": "Context:\n" + "\n---\n".join(retrieved_contexts)})
    messages.append({"role": "user", "content": user_prompt})
    llm = _get_llm()
    return llm.chat(messages)


def analyze_debt(user_financials):
    # Build prompt
    system = "You are a helpful financial analysis assistant that produces clear, actionable debt analyses."
    prompt = f"User income: {user_financials['income']}. Debts: {user_financials['debts']}. Savings: {user_financials.get('savings',0)}. Provide a debt analysis, categorization, and recommended actions."
    ctx = rag.retrieve(prompt)
    resp = _call_llm_with_context(system, prompt, ctx)
    return {"summary": resp}


def savings_strategy(user_financials):
    system = "You are an experienced personal finance coach. Produce personalized savings strategies."
    prompt = f"Income: {user_financials['income']}. Spending: {user_financials['recurring_spending']}. Current savings: {user_financials.get('savings',0)}. Provide 3 savings strategies prioritized by expected impact."
    ctx = rag.retrieve(prompt)
    resp = _call_llm_with_context(system, prompt, ctx)
    return {"summary": resp}


def budget_advice(user_financials):
    system = "You are a practical budget coach. Produce a monthly budget with line items and percent allocations."
    prompt = f"Income: {user_financials['income']}. Recurring spending: {user_financials['recurring_spending']}. Discretionary: {user_financials.get('discretionary_spending',0)}. Provide an actionable monthly budget and 5 short actionable tips."
    ctx = rag.retrieve(prompt)
    resp = _call_llm_with_context(system, prompt, ctx)
    return {"summary": resp}


def debt_payoff_optimizer(user_financials):
    system = "You are a financial planner who optimizes debt payoff plans considering interest rates and minimum payments."
    prompt = f"Debts: {user_financials['debts']}. Monthly available for debt repayment (beyond minimums): {max(0, user_financials['income'] - user_financials['recurring_spending'] - user_financials.get('discretionary_spending',0))}. Provide optimized payoff plan (timeline, order, monthly amounts)."
    ctx = rag.retrieve(prompt)
    resp = _call_llm_with_context(system, prompt, ctx)
    return {"summary": resp}


# compatibility wrapper expected by API
def debt_payoff(user_financials):
    return debt_payoff_optimizer(user_financials)
