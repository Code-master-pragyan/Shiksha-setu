import sys
import os
import json
import statistics

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_knowledge():
    processed_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed'))
    jsonl_file = os.path.join(processed_dir, 'knowledge_chunks.jsonl')
    manifest_file = os.path.join(processed_dir, 'manifest.json')
    
    if not os.path.exists(jsonl_file):
        print(f"Error: {jsonl_file} not found.")
        sys.exit(1)
        
    if not os.path.exists(manifest_file):
        print(f"Error: {manifest_file} not found.")
        sys.exit(1)
        
    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
        
    documents = len(manifest)
    
    chunks = []
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
                
    total_chunks = len(chunks)
    
    pages_processed = sum(m.get("pages", 0) for m in manifest)
    
    missing_title = sum(1 for c in chunks if not c.get("title"))
    missing_chapters = sum(1 for c in chunks if not c.get("chapter"))
    missing_sections = sum(1 for c in chunks if not c.get("section"))
    
    # Check page_start and page_end
    missing_pages = sum(1 for c in chunks if c.get("page_start") is None or c.get("page_end") is None)
    
    missing_subject = sum(1 for c in chunks if not c.get("subject"))
    missing_grade = sum(1 for c in chunks if c.get("grade") is None)
    
    chunk_ids = [c["chunk_id"] for c in chunks]
    duplicate_ids = len(chunk_ids) - len(set(chunk_ids))
    
    chunk_sizes = [len(c.get("text", "").split()) for c in chunks]
    
    below_target = 0
    above_target = 0
    
    if chunk_sizes:
        avg_size = statistics.mean(chunk_sizes)
        min_size = min(chunk_sizes)
        max_size = max(chunk_sizes)
        below_target = sum(1 for s in chunk_sizes if s < 300) # Using 300 as a lower bound for warning
        above_target = sum(1 for s in chunk_sizes if s > 1000)
    else:
        avg_size = min_size = max_size = 0
        
    print("\nKNOWLEDGE BASE CHECK")
    print("--------------------")
    print(f"Documents: {documents}")
    print(f"Pages: {pages_processed}")
    print(f"Chunks: {total_chunks}")
    print("")
    print(f"Missing titles: {missing_title}")
    print(f"Missing chapters: {missing_chapters}")
    print(f"Missing sections: {missing_sections} (Normal for intro texts)")
    print(f"Missing page metadata: {missing_pages}")
    print(f"Missing subject: {missing_subject}")
    print(f"Missing grade: {missing_grade}")
    print(f"Duplicate chunk IDs: {duplicate_ids}")
    print("")
    print(f"Average chunk size: {avg_size:.1f} words")
    print(f"Minimum chunk size: {min_size} words")
    print(f"Maximum chunk size: {max_size} words")
    print(f"Chunks below target range (<300 words): {below_target} (Note: Small chunks are normal near headers)")
    print(f"Chunks above target range (>1000 words): {above_target}")
    
if __name__ == "__main__":
    check_knowledge()
