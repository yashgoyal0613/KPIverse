"""
LLM wrapper — Groq (free tier) with RAG-grounded KPI analysis.
Uses llama-3.3-70b-versatile model — fast and free.
"""
import os
from groq import Groq
from core.retriever import build_context

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set. Add it to your .env file.")
        _client = Groq(api_key=api_key)
    return _client


SYSTEM_PROMPT = """You are an expert Business Intelligence analyst specializing in Sales & Revenue and Finance & Accounting KPIs.

You have access to retrieved business data context below. Your job is to:
1. Answer questions using ONLY the provided data context — never fabricate numbers.
2. Calculate, interpret, and explain KPIs clearly for business stakeholders.
3. Highlight trends, anomalies, risks, and opportunities based on the data.
4. Provide actionable recommendations when appropriate.
5. If data is insufficient to answer a question, say so clearly and suggest what data would help.

Formatting rules:
- Use concise bullet points for lists of KPIs or recommendations.
- Use markdown tables when comparing multiple metrics.
- Always state the source dataset when quoting specific numbers.
- Be confident but precise — round numbers appropriately.
"""


def ask(
    user_question: str,
    chat_history: list[dict] = None,
    source_filter: str = None,
    n_context_chunks: int = 6,
    stream: bool = False,
) -> str:
    client = _get_client()

    # --- RAG: retrieve context ---
    context = build_context(user_question, n_results=n_context_chunks, source_filter=source_filter)

    # --- Build messages ---
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    messages.append({
        "role": "user",
        "content": f"Here is the relevant business data context:\n\n{context}\n\nPlease confirm you have this data.",
    })
    messages.append({
        "role": "assistant",
        "content": "I have the business data context. I'll use only this data to answer your questions accurately.",
    })

    if chat_history:
        for turn in chat_history:
            messages.append(turn)

    messages.append({"role": "user", "content": user_question})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1500,
        messages=messages,
    )

    return response.choices[0].message.content


def ask_with_sources(
    user_question: str,
    chat_history: list[dict] = None,
    source_filter: str = None,
    n_context_chunks: int = 6,
) -> tuple[str, list[dict]]:
    from core.retriever import retrieve
    chunks = retrieve(user_question, n_results=n_context_chunks, source_filter=source_filter)
    answer = ask(user_question, chat_history, source_filter, n_context_chunks)
    return answer, chunks