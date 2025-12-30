"""
Document storage for expert agents.
Each agent has 5-6 documents with high diversity per paper Section 3.2.
"""

# Document paths will be stored here
# Documents can be loaded and added to agent context

DOCUMENT_PATHS = {
    "sqli": [
        # SQL injection documents (5-6 documents)
        "prompts/documents/sqli/doc1.txt",
        "prompts/documents/sqli/doc2.txt",
        "prompts/documents/sqli/doc3.txt",
        "prompts/documents/sqli/doc4.txt",
        "prompts/documents/sqli/doc5.txt",
    ],
    "xss": [
        # XSS documents (5-6 documents)
        "prompts/documents/xss/doc1.txt",
        "prompts/documents/xss/doc2.txt",
        "prompts/documents/xss/doc3.txt",
        "prompts/documents/xss/doc4.txt",
        "prompts/documents/xss/doc5.txt",
    ],
    "csrf": [
        # CSRF documents (5-6 documents)
        "prompts/documents/csrf/doc1.txt",
        "prompts/documents/csrf/doc2.txt",
        "prompts/documents/csrf/doc3.txt",
        "prompts/documents/csrf/doc4.txt",
        "prompts/documents/csrf/doc5.txt",
    ],
    "ssti": [
        # SSTI documents (5-6 documents)
        "prompts/documents/ssti/doc1.txt",
        "prompts/documents/ssti/doc2.txt",
        "prompts/documents/ssti/doc3.txt",
        "prompts/documents/ssti/doc4.txt",
        "prompts/documents/ssti/doc5.txt",
    ],
    "zap": [
        # ZAP documents (5-6 documents)
        "prompts/documents/zap/doc1.txt",
        "prompts/documents/zap/doc2.txt",
        "prompts/documents/zap/doc3.txt",
        "prompts/documents/zap/doc4.txt",
        "prompts/documents/zap/doc5.txt",
    ],
    "generic": [
        # Generic web security documents (5-6 documents)
        "prompts/documents/generic/doc1.txt",
        "prompts/documents/generic/doc2.txt",
        "prompts/documents/generic/doc3.txt",
        "prompts/documents/generic/doc4.txt",
        "prompts/documents/generic/doc5.txt",
    ],
}

def load_documents(vulnerability_type: str):
    """
    Load documents for a specific vulnerability type.
    
    Args:
        vulnerability_type: Type of vulnerability (sqli, xss, etc.)
        
    Returns:
        List of document contents
    """
    from pathlib import Path
    
    documents = []
    doc_paths = DOCUMENT_PATHS.get(vulnerability_type.lower(), [])
    
    for doc_path in doc_paths:
        full_path = Path(__file__).parent.parent.parent / doc_path
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    documents.append(f.read())
            except Exception as e:
                # Skip documents that can't be read
                pass
    
    return documents

