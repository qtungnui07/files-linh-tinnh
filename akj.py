import os
import pandas as pd
import pickle
import torch  # To check for GPU availability
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from tqdm import tqdm

# General function to translate an array of texts using a specified model and language codes
def translate_texts(model_name: str, src_lang: str, tgt_lang: str, texts: list) -> list:
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name, src_lang=src_lang)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    
    # Move model to GPU if available
    if torch.cuda.is_available():
        model = model.cuda()
        print("Using GPU for translation.")
    else:
        print("GPU not available, using CPU.")

    # Translate texts
    translated_texts = []
    for text in tqdm(texts, desc="Translating"):
        # Tokenize input text and move to GPU if available
        input_ids = tokenizer(text, return_tensors="pt").input_ids
        if torch.cuda.is_available():
            input_ids = input_ids.cuda()
        
        output_ids = model.generate(
            input_ids,
            decoder_start_token_id=tokenizer.lang_code_to_id[tgt_lang],
            num_return_sequences=1,
            num_beams=5,
            early_stopping=True
        )
        
        translated_text = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        translated_texts.append(" ".join(translated_text))
    
    return translated_texts

# Load Excel file, assuming the texts are in the first column with English texts
def load_excel_column(file_path: str, column_name: str) -> list:
    df = pd.read_excel(file_path)
    return df[column_name].tolist()

# Save translated texts to a pickle file
def save_to_pickle(data: list, file_path: str):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)

# Function to check and create a .pkl file if it doesn't exist
def ensure_pickle_file(file_path: str):
    if not os.path.exists(file_path):
        print(f"Pickle file '{file_path}' does not exist. Creating new file...")
        with open(file_path, 'wb') as f:
            pickle.dump([], f)  # Initialize an empty list in the pickle file

# Example usage
if __name__ == "__main__":
    model_name = "vinai/vinai-translate-en2vi-v2"
    src_lang = "en_XX"
    tgt_lang = "vi_VN"
    input_file = "2.xlsx"  # Input Excel file
    output_file = "translated_texts.pkl"  # Output pickle file
    column_name = "English"  # Column name in Excel with English texts
    
    # Check if the output pickle file exists, if not, create it
    ensure_pickle_file(output_file)
    
    # Load texts from Excel
    texts = load_excel_column(input_file, column_name)
    
    # Translate texts
    vi_texts = translate_texts(model_name, src_lang, tgt_lang, texts)
    
    # Save the translated texts to a pickle file
    save_to_pickle(vi_texts, output_file)
    
    print(f"Translation completed and saved to {output_file}")
