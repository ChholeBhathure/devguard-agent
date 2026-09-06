from devguard.chunker import chunk_ast_payloads, estimate_tokens

def test_estimate_tokens():
    text = "a" * 40
    assert estimate_tokens(text) == 10

def test_chunk_ast_payloads_single_chunk():
    files = [{"filename": "test.py", "ast": "data"}]
    chunks = chunk_ast_payloads(files, max_tokens=1000)
    assert len(chunks) == 1
    assert len(chunks[0]) == 1

def test_chunk_ast_payloads_splits_properly():
    # Large item that uses roughly ~100 tokens (400 chars)
    large_item = {"filename": "large.py", "content": "x" * 400}
    files = [large_item for _ in range(5)]
    
    # Set max_tokens small enough to force chunking into multiple batches
    chunks = chunk_ast_payloads(files, max_tokens=250)
    assert len(chunks) > 1