# phrase_extractor.py
import pandas as pd
import time
import os
import csv
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def extract_phrases(review, sentiment):
    prompt = f"""
You are a genuine homebuyer sharing your experience and opinions about a residential property.
 
Task:
Extract short, meaningful phrases from the review that clearly express either positive or negative sentiment about specific aspects of the property.
 
Instructions:
- Focus strictly on property-related aspects only (e.g., layout, amenities, materials, ventilation, maintenance, safety, etc.).
- Ignore phrases related to the builder, possession delays, sales team, pricing, or construction status.
- Only include phrases that express **clear opinions** (positive or negative). Do not include factual statements.
- Avoid vague or generic language like "very good", "nice", "bad", or "amazing" unless the phrase specifies **why** it is good or bad.
- Skip overly promotional or emotionally extreme language that doesn’t provide actionable insight.
- Ensure both **positive and negative** sentiments are captured fairly. If the review includes negative experiences, do not overlook them.
- Do not include personal names, locations, or other personal identifiers.
- If the project is under construction, ignore any mention of incomplete or ongoing development.
 
Review: "{review}"
Overall Sentiment: {sentiment}
 
Return a bullet-point list of short phrases  each labeled with 'positive' or 'negative', depending on the expressed sentiment.
"""
 
    try:
        response = model.generate_content(prompt)
        time.sleep(8)
        phrases = []
        for line in response.text.strip().split('\n'):
            line = line.strip('-•* ')
            if '(' in line and ')' in line:
                phrase_part = line[:line.rfind('(')].strip()
                sentiment_part = line[line.rfind('(')+1:line.rfind(')')].strip().lower()
                if 3 <= len(phrase_part.split()) <= 6 and sentiment_part in ['positive', 'negative']:
                    phrases.append({
                        'Phrase': phrase_part,
                        'Sentiment': sentiment_part
                    })
        return phrases
    except Exception as e:
        print(f"Phrase extraction error: {e}")
        return []

def process_phrases(classified_file, phrase_output):
    df = pd.read_csv(classified_file)
    results = []

    for _, row in df.iterrows():
        phrases = extract_phrases(str(row['Review']), row['Sentiment'])
        print(f"Extracted phrases: {phrases} for review: {row['Review']}")
        for phrase_data in phrases:
            results.append({
                'xid': row['xid'],
                'Project name': row['Project name'],
                'Phrase': phrase_data['Phrase'],
                'Sentiment': phrase_data['Sentiment']
            })

    with open(phrase_output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['xid', 'Project name', 'Phrase', 'Sentiment'])
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved phrases to {phrase_output}")

# Usage
classified_reviews_path = 'reviews.csv'
phrases_output_path = 'phrases.csv'
process_phrases(classified_reviews_path, phrases_output_path)
