"""
Harry Potter screenplay chunking by scenes
"""
import re
import json

def chunk_by_scenes(text_file_path: str, output_file_path: str):
    """
    Split Harry Potter screenplay by scene markers and save as JSON chunks.
    
    Args:
        text_file_path: Path to the screenplay text file with scene markers
        output_file_path: Path to save the JSON chunks
    
    Returns:
        List of chunk dictionaries
    """
    # Read the text file
    with open(text_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by scene markers (e.g., "Scene 1: Title")
    scene_pattern = r'Scene (\d+): ([^\n]+)'
    scenes = re.split(scene_pattern, content)
    
    chunks = []
    
    # First element is content before first scene (if any)
    if scenes[0].strip():
        chunk = {
            'id': 'scene_0',
            'scene_number': 0,
            'scene_title': 'Introduction',
            'text': scenes[0].strip(),
            'metadata': {
                'source': 'harry-potter-and-the-sorcerers-stone-screenplay',
                'scene': 0,
                'chunk_type': 'scene'
            }
        }
        chunks.append(chunk)
    
    # Process scenes (list alternates: scene_num, scene_title, content)
    for i in range(1, len(scenes), 3):
        if i+2 < len(scenes):
            scene_num = scenes[i]
            scene_title = scenes[i+1].strip()
            scene_content = scenes[i+2].strip()
            
            if scene_content:  # Only add non-empty scenes
                chunk = {
                    'id': f'scene_{scene_num}',
                    'scene_number': int(scene_num),
                    'scene_title': scene_title,
                    'text': scene_content,
                    'metadata': {
                        'source': 'harry-potter-and-the-sorcerers-stone-screenplay',
                        'scene': int(scene_num),
                        'title': scene_title,
                        'chunk_type': 'scene'
                    }
                }
                chunks.append(chunk)
    
    # Save chunks to JSON file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    
    print(f"Created {len(chunks)} scene-based chunks")
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
    text_file = "./db/harry-potter-text.txt"
    output_file = "./db/harry-potter-chunks.json"
    
    # Create chunks
    chunks = chunk_by_scenes(text_file, output_file)
    
    # Show first chunk as example
    print("\nExample chunk (first scene):")
    print(json.dumps(chunks[0], indent=2))
