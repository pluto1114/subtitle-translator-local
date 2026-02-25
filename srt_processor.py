import re
import os

class SRTProcessor:
    @staticmethod
    def parse_srt(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')

        # Split by double newlines to isolate blocks
        raw_blocks = re.split(r'\n\n+', content.strip())
        
        parsed_blocks = []
        for raw_block in raw_blocks:
            lines = raw_block.strip().split('\n')
            if len(lines) >= 3 and '-->' in lines[1]:
                index = lines[0]
                timestamp = lines[1]
                text = "\n".join(lines[2:])
                parsed_blocks.append({"index": index, "timestamp": timestamp, "text": text, "raw": raw_block, "is_valid": True})
            else:
                parsed_blocks.append({"raw": raw_block, "is_valid": False})
        
        return parsed_blocks

    @staticmethod
    def save_srt(file_path, blocks):
        final_content = []
        for b in blocks:
            if not b.get("is_valid", True):
                final_content.append(b['raw'])
            else:
                final_content.append(f"{b['index']}\n{b['timestamp']}\n{b.get('translated_text', b['text'])}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(final_content))
