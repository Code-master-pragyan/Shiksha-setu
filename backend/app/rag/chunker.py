import re
from typing import List, Dict, Any, Tuple, Optional

def extract_metadata(line: str, current_chapter_num: Optional[int], current_chapter: Optional[str], current_section: Optional[str]) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """
    Extracts chapter and section metadata from a line of text using regex.
    """
    # Detect Chapter: e.g. "Chapter 2 - The Invisible Living World"
    chapter_match = re.search(r'(?i)^Chapter\s+(\d+)[\s\-\—\:]+(.*)$', line.strip())
    if chapter_match:
        try:
            return int(chapter_match.group(1)), chapter_match.group(2).strip(), current_section
        except ValueError:
            pass
            
    # Detect Section: e.g. "2.1 What Is a Cell?"
    section_match = re.search(r'^(\d+\.\d+)\s+(.+)$', line.strip())
    if section_match:
        return current_chapter_num, current_chapter, line.strip()
        
    return current_chapter_num, current_chapter, current_section

def semantic_chunk_document(pages: List[Dict[str, Any]], target_words: int = 500, overlap_sentences: int = 3) -> List[Dict[str, Any]]:
    """
    Sentence-aware semantic chunking across multiple pages.
    Extracts headers and tracks state.
    """
    sentences = []
    
    current_chapter_num = None
    current_chapter = None
    current_section = None
    
    for page_dict in pages:
        page_num = page_dict["page"]
        text = page_dict["text"]
        
        lines = text.split('\n')
        
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
                
            current_chapter_num, current_chapter, current_section = extract_metadata(
                line_str, current_chapter_num, current_chapter, current_section
            )
            
            line_sentences = re.split(r'(?<=[.!?])\s+', line_str)
            
            for s in line_sentences:
                s_str = s.strip()
                if s_str:
                    sentences.append({
                        "text": s_str,
                        "page": page_num,
                        "chapter_num": current_chapter_num,
                        "chapter": current_chapter,
                        "section": current_section
                    })
                    
    chunks = []
    current_chunk_sentences = []
    current_word_count = 0
    
    i = 0
    while i < len(sentences):
        sent = sentences[i]
        words = sent["text"].split()
        word_count = len(words)
        
        current_chunk_sentences.append(sent)
        current_word_count += word_count
        
        if current_word_count >= target_words:
            _save_chunk(chunks, current_chunk_sentences)
            
            overlap = []
            overlap_words = 0
            for s in reversed(current_chunk_sentences):
                overlap.insert(0, s)
                overlap_words += len(s["text"].split())
                if len(overlap) >= overlap_sentences:
                    break
            
            current_chunk_sentences = overlap
            current_word_count = overlap_words
            
        i += 1
        
    if current_word_count > 0:
        if not chunks or current_chunk_sentences != chunks[-1].get("raw_sentences"):
            _save_chunk(chunks, current_chunk_sentences)
            
    return chunks

def _save_chunk(chunks_list: List[Dict[str, Any]], sentences: List[Dict[str, Any]]):
    if not sentences:
        return
        
    text = " ".join(s["text"] for s in sentences)
    page_start = sentences[0]["page"]
    page_end = sentences[-1]["page"]
    
    # We use the chapter/section of the FIRST sentence in the chunk as the primary metadata
    chapter_num = sentences[0]["chapter_num"]
    chapter = sentences[0]["chapter"]
    section = sentences[0]["section"]
    
    chunks_list.append({
        "text": text,
        "page_start": page_start,
        "page_end": page_end,
        "chapter_number": chapter_num,
        "chapter": chapter,
        "section": section,
        "raw_sentences": list(sentences)
    })
