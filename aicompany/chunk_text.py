"""
AICompany policy document chunking by sections
"""
import re
import json

def chunk_by_sections(text_file_path: str, output_file_path: str):
    """
    Split AICompany policy document by section markers and save as JSON chunks.
    
    Args:
        text_file_path: Path to the policy text file with section markers
        output_file_path: Path to save the JSON chunks
    
    Returns:
        List of chunk dictionaries
    """
    # Read the text file
    with open(text_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by section markers (e.g., "Section 1: Title")
    section_pattern = r'Section (\d+): ([^\n]+)'
    sections = re.split(section_pattern, content)
    
    chunks = []
    
    # First element is content before first section (header/intro)
    if sections[0].strip():
        chunk = {
            'id': 'section_0',
            'section_number': 0,
            'section_title': 'Introduction',
            'text': sections[0].strip(),
            'metadata': {
                'source': 'aicompany-policies',
                'section': 0,
                'chunk_type': 'policy_section'
            }
        }
        chunks.append(chunk)
    
    # Process sections (list alternates: section_num, section_title, content)
    for i in range(1, len(sections), 3):
        if i+2 < len(sections):
            section_num = sections[i]
            section_title = sections[i+1].strip()
            section_content = sections[i+2].strip()
            
            if section_content:  # Only add non-empty sections
                chunk = {
                    'id': f'section_{section_num}',
                    'section_number': int(section_num),
                    'section_title': section_title,
                    'text': section_content,
                    'metadata': {
                        'source': 'aicompany-policies',
                        'section': int(section_num),
                        'title': section_title,
                        'chunk_type': 'policy_section'
                    }
                }
                chunks.append(chunk)
    
    # Save chunks to JSON file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    
    print(f"Created {len(chunks)} section-based chunks")
    print(f"Saved to: {output_file_path}")
    
    # Print some statistics
    chunk_sizes = [len(chunk['text']) for chunk in chunks]
    print(f"\nChunk statistics:")
    print(f"  Average size: {sum(chunk_sizes) / len(chunk_sizes):.0f} characters")
    print(f"  Min size: {min(chunk_sizes)} characters")
    print(f"  Max size: {max(chunk_sizes)} characters")
    
    return chunks

if __name__ == "__main__":
    # Define paths
    text_file = "./db/aicompany-policies.txt"
    output_file = "./db/aicompany-chunks.json"
    
    # Create chunks
    chunks = chunk_by_sections(text_file, output_file)
    
    # Show first chunk as example
    print("\nExample chunk (first section):")
    print(json.dumps(chunks[0], indent=2))
