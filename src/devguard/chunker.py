from typing import List, Dict, Any

# Approximate token limit per context window for Gemini requests
DEFAULT_TOKEN_LIMIT = 8000  

def estimate_tokens(text: str) -> int:
    """Rough token estimation (approx. 4 characters per token)."""
    return len(text) // 4

def chunk_ast_payloads(
    files: List[Dict[str, Any]], 
    max_tokens: int = DEFAULT_TOKEN_LIMIT
) -> List[List[Dict[str, Any]]]:
    """
    Groups indexed AST file entries into batches that fit within token constraints.
    """
    chunks = []
    current_chunk = []
    current_tokens = 0

    for file_entry in files:
        file_repr = str(file_entry)
        entry_tokens = estimate_tokens(file_repr)

        if current_tokens + entry_tokens > max_tokens and current_chunk:
            chunks.append(current_chunk)
            current_chunk = [file_entry]
            current_tokens = entry_tokens
        else:
            current_chunk.append(file_entry)
            current_tokens += entry_tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks