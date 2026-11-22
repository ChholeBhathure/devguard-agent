import math
from typing import Any

def chunk_source_code(
    source_code: str, 
    file_path: str, 
    max_tokens: int = 5000, 
    overlap_lines: int = 5
) -> list[dict[str, Any]]:
    """
    Splits raw source code into token-bounded chunks, preserving line numbers.
    """
    if max_tokens <= 0:
        raise ValueError("max_tokens must be greater than 0")
    if overlap_lines < 0:
        raise ValueError("overlap_lines cannot be negative")
    if not source_code.strip():
        return []

    # Approximate characters per token (a safe estimate for code is ~3.5)
    CHARS_PER_TOKEN = 3.5
    max_chars = int(max_tokens * CHARS_PER_TOKEN)

    lines = source_code.splitlines(keepends=True)
    chunks = []
    
    current_chunk_lines = []
    current_chars = 0
    start_line = 1

    for current_line_num, line in enumerate(lines, start=1):
        line_len = len(line)

        # Handle a single line that is larger than the max token limit
        if line_len > max_chars:
            if current_chunk_lines:
                # Save what we have so far before handling the giant line
                chunks.append({
                    "file_path": file_path,
                    "start_line": start_line,
                    "end_line": current_line_num - 1,
                    "source_code": "".join(current_chunk_lines)
                })
                current_chunk_lines = []
                current_chars = 0
                start_line = current_line_num
            
            # Split the giant line into pieces
            num_pieces = math.ceil(line_len / max_chars)
            piece_size = math.ceil(line_len / num_pieces)
            
            for i in range(0, line_len, piece_size):
                piece = line[i:i+piece_size]
                chunks.append({
                    "file_path": file_path,
                    "start_line": current_line_num,
                    "end_line": current_line_num,
                    "source_code": piece
                })
            
            # Setup for the next lines
            start_line = current_line_num + 1
            continue

        # If adding this line exceeds the limit, save the chunk and start a new one
        if current_chars + line_len > max_chars and current_chunk_lines:
            chunks.append({
                "file_path": file_path,
                "start_line": start_line,
                "end_line": current_line_num - 1,
                "source_code": "".join(current_chunk_lines)
            })

            # Apply overlap: keep the last N lines for the next chunk
            overlap_count = min(overlap_lines, len(current_chunk_lines))
            overlap_data = current_chunk_lines[-overlap_count:]
            
            current_chunk_lines = overlap_data
            current_chars = sum(len(l) for l in current_chunk_lines)
            start_line = current_line_num - overlap_count + 1

        current_chunk_lines.append(line)
        current_chars += line_len

    # Don't forget the final chunk!
    if current_chunk_lines:
        chunks.append({
            "file_path": file_path,
            "start_line": start_line,
            "end_line": len(lines),
            "source_code": "".join(current_chunk_lines)
        })

    return chunks

