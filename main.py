from flask import Flask, request, jsonify
import redis
from celery import Celery
import time
from functools import wraps
import os
import re
from transformers import MarianMTModel, MarianTokenizer
from tqdm import tqdm

app = Flask(__name__)

# Konfigurace Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Konfigurace Celery
celery = Celery('tasks', broker='redis://localhost:6379/0')
celery.conf.update(app.config)

# Konfigurace limitu požadavků
RATE_LIMIT = 3
RATE_LIMIT_PERIOD = 3600  # 1 hodina v sekundách

@app.route('/')
def home():
    return '''
    <h1>Překladač ASS souborů</h1>
    <form action="/translate" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept=".ass">
        <input type="checkbox" name="formal" value="true" checked> Formální překlad
        <input type="text" name="character_genders" placeholder='{"Character1": "male", "Character2": "female"}'>
        <input type="submit" value="Přeložit">
    </form>
    '''

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        current_time = int(time.time())
        key = f'rate_limit:{ip}'
        
        pipe = redis_client.pipeline()
        pipe.zremrangebyscore(key, 0, current_time - RATE_LIMIT_PERIOD)
        pipe.zcard(key)
        pipe.zadd(key, {current_time: current_time})
        pipe.expire(key, RATE_LIMIT_PERIOD)
        results = pipe.execute()
        
        request_count = results[1]
        
        if request_count > RATE_LIMIT:
            return jsonify({"error": "Rate limit exceeded"}), 429
        
        return f(*args, **kwargs)
    return decorated_function

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
    context = f">>cs<< <{formality}> <{gender}> "
    input_text = context + text
    translated = model.generate(**tokenizer(input_text, return_tensors="pt", padding=True))
    return tokenizer.decode(translated[0], skip_special_tokens=True)

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

@celery.task(bind=True)
def translate_task(self, input_file, output_file, formal, character_genders):
    try:
        # Načtení modelu a tokenizeru
        model_name = 'Helsinki-NLP/opus-mt-en-cs'
        print("Načítám překladový model...")
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)

        translate_ass_file(input_file, output_file, model, tokenizer, formal, character_genders)
        
        # Odstranění příznaku probíhajícího překladu
        redis_client.delete('translation_in_progress')
        
        return {'status': 'Překlad dokončen', 'output_file': output_file}
    except Exception as e:
        # Odstranění příznaku probíhajícího překladu v případě chyby
        redis_client.delete('translation_in_progress')
        return {'status': 'Chyba', 'error': str(e)}

@app.route('/translate', methods=['POST'])
@rate_limit
def translate():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        input_filename = os.path.join('uploads', file.filename)
        output_filename = os.path.join('outputs', f'translated_{file.filename}')
        file.save(input_filename)
        
        formal = request.form.get('formal', 'true').lower() == 'true'
        character_genders = request.form.get('character_genders', '{}')
        
        # Kontrola, zda již běží nějaká úloha
        if redis_client.get('translation_in_progress'):
            return jsonify({"message": "Translation added to queue"}), 202
        
        # Nastavení příznaku probíhajícího překladu
        redis_client.set('translation_in_progress', 'true', ex=3600)  # Vyprší po hodině
        
        # Spuštění asynchronní úlohy
        task = translate_task.delay(input_filename, output_filename, formal, character_genders)
        
        return jsonify({"message": "Translation started", "task_id": task.id}), 202

@app.route('/status/<task_id>')
def task_status(task_id):
    task = translate_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)