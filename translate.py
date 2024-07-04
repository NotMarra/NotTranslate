import re
from numpy import info
from transformers import MarianMTModel, MarianTokenizer
from tqdm import tqdm

def translate_text(text, model, tokenizer):
    translated = model.generate(**tokenizer(text, return_tensors="pt", padding=True))
    return tokenizer.decode(translated[0], skip_special_tokens=True)

def split_text(text, max_words):
    words = text.split()
    return [' '.join(words[i:i+max_words]) for i in range(0, len(words), max_words)]

def translate_ass_file(input_file, output_file, model, tokenizer, max_words_per_line=10):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    pattern = r'^(Dialogue:[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,)(.*)$'
    
    def translate_line(line):
        match = re.match(pattern, line)
        if not match:
            return line
        
        prefix = match.group(1)
        text = match.group(2)
        
        joined_text = text.replace('\\N', ' ').strip()
        
        translated_text = translate_text(joined_text, model, tokenizer)
        
        split_parts = split_text(translated_text, max_words_per_line)
        
        final_text = '\\N'.join(split_parts)
        
        return f"{prefix}{final_text}\n"
    
    total_lines = len(content)
    translated_content = []

    info_text = "Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,Přeloženo pomocí NotTranslate AI ver. 0.1-Alpha\\NKorekce: bez korekce\\NStránky developera: NotMarra.com\n"
    events_section_found = False
    first_dialogue_found = False

    print(f"Překládám {total_lines} řádků...")
    for line in tqdm(content, total=total_lines, desc="Průběh překladu"):
        if line.strip().startswith('[Events]'):
            events_section_found = True

        if events_section_found and line.startswith('Dialogue:')and not first_dialogue_found:
            translated_content.append(info_text)
            first_dialogue_found = True
    
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