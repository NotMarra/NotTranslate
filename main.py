import re
from numpy import info
from transformers import MarianMTModel, MarianTokenizer
from tqdm import tqdm

def translate_text(text, model, tokenizer):
    translated = model.generate(**tokenizer(text, return_tensors="pt", padding=True))
    return tokenizer.decode(translated[0], skip_special_tokens=True)

def translate_ass_file(input_file, output_file, model, tokenizer):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    pattern = r'^(Dialogue:[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,)(.*)$'
    
    def translate_line(line):
        match = re.match(pattern, line)
        if not match:
            return line
        
        prefix = match.group(1)
        text = match.group(2)
        
        parts = text.split('\\N')
        translated_parts = []
        for part in parts:
            part = part.strip()
            if part:
                translated_part = translate_text(part, model, tokenizer)
                translated_parts.append(translated_part)
        
        translated_text = '\\N'.join(translated_parts)
        return f"{prefix}{translated_text}\n"
    
    total_lines = len(content)
    translated_content = []

    info_text = "Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,Přeloženo pomocí NotTranslate AI ver. 0.1-Alpha\\NStránky developera: NotMarra.com\n"
    events_section_found = False
    first_dialogue_found = False

    print(f"Překládám {total_lines} řádků...")
    for line in tqdm(content, total=total_lines, desc="Průběh překladu"):
        if line.strip().startswith('[Events]'):
            events_section_found = True

        if events_section_found and line.startswith('Dialogue:')and not first_dialogue_found:
            translated_content.append(info_text)
            first_dialogue_found = True
            
        translated_line = translate_line(line)
        translated_content.append(translated_line)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(translated_content)
    
    print(f"Překlad dokončen. Výstup uložen do {output_file}")

# Načtení modelu a tokenizeru
model_name = 'Helsinki-NLP/opus-mt-en-cs'  # Model pro překlad z angličtiny do češtiny
print("Načítám překladový model...")
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

# Příklad použití
input_file = 'input.ass'
output_file = 'output.ass'

translate_ass_file(input_file, output_file, model, tokenizer)