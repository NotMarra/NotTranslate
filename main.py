import re
from transformers import MarianMTModel, MarianTokenizer
from tqdm import tqdm

def split_sentence(sentence, max_words=10):
    words = sentence.split()
    if len(words) <= max_words:
        return [sentence]
    
    parts = []
    current_part = []
    word_count = 0
    
    for word in words:
        current_part.append(word)
        word_count += 1
        
        if word_count >= max_words and (word.endswith(',') or word.endswith('.')):
            parts.append(' '.join(current_part))
            current_part = []
            word_count = 0
    
    if current_part:
        parts.append(' '.join(current_part))
    
    return parts

def translate_text(text, model, tokenizer, formal=True, gender='neutral'):
    formality = "formal" if formal else "informal"
    context = f">>cs<< <{gender}> <{formality}>"
    input_text = context + " " + text
    translated = model.generate(**tokenizer(input_text, return_tensors="pt", padding=True))
    translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
    
    translated_text = re.sub(r'<[^>]+>', '', translated_text)  
    translated_text = re.sub(r'\b(female|male|neutral|formální|neformální|ženské|mužské)\s*', '', translated_text, flags=re.IGNORECASE)
    

    translated_text = translated_text.strip()
    

    translated_text = translated_text[0].upper() + translated_text[1:]
    
    return translated_text

def translate_ass_file(input_file, output_file, model, tokenizer, formal=True, character_genders=None):
    if character_genders is None:
        character_genders = {}

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    pattern = r'^(Dialogue:[^,]*,[^,]*,[^,]*,[^,]*,([^,]*),.*?,.*?,.*?,.*?,)(.*)$'
    
    def translate_line(line):
        match = re.match(pattern, line)
        if not match:
            return line
        
        prefix = match.group(1)
        character = match.group(2)
        text = match.group(3)
        
        gender = character_genders.get(character, 'neutral')
        
        full_text = ' '.join(text.split('\\N'))
        
        translated_full = translate_text(full_text, model, tokenizer, formal, gender)
        
        translated_parts = split_sentence(translated_full)
        
        translated_text = '\\N'.join(translated_parts)
        
        translated_text = re.sub(r'^' + re.escape(character) + r':\s*', '', translated_text)
        
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
        
        if events_section_found and line.startswith('Dialogue:') and not first_dialogue_found:
            translated_content.append(info_text)
            first_dialogue_found = True
        
        translated_line = translate_line(line)
        translated_content.append(translated_line)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(translated_content)
    
    print(f"Překlad dokončen. Výstup uložen do {output_file}")

# Načtení modelu a tokenizeru
model_name = 'Helsinki-NLP/opus-mt-en-cs'
print("Načítám překladový model...")
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

# Příklad použití
input_file = 'input.ass'
output_file = 'output.ass'

character_genders = {
    "Girl": "female",
    "Woman": "female",
    "Text": "neutral",
    "Lawrence": "male",
    "Knight": "male",
    "Farmer": "male",
    "Villager": "neutral",
    "Yarei": "male",
    "Village Chief": "male",
    "Holo": "female"
}

translate_ass_file(input_file, output_file, model, tokenizer, formal=True, character_genders=character_genders)