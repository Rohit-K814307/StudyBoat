from flask import Flask, jsonify, request
from flask_cors import CORS
import openai
import json
import re
import random
import requests
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import sent_tokenize

nltk.download('stopwords')
nltk.download('punkt')
key = "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"



app = Flask(__name__)
CORS(app)

app.route("/")
def home():
    return jsonify({"hello": "welcome to the api"})

@app.route("/essay", methods=['POST'])
#json form = {"essay":___essay____}
def essay():
    content_type = request.headers.get('Content-Type')
    print(content_type)
    if(content_type == "application/json"):

        jso = request.get_json()
        print(jso)

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + key,
            }

        json_data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'user',
                    'content': "give me feedback on this essay, and a score out of 100 (be harsh). what can I change in my overallm essage, and can you address grammatical errors and how to fix them. Correct any spelling errors and let me know what they are. After reviewing the essay, rewrite it in another section and fix errors. /n " + jso.get("essay"),
                },
            ],
            'temperature': 0.7,
        }
        response = requests.post('https://api.openai.com/v1/chat/completions',headers=headers,json=json_data)
        response = json.loads(response.text)

        t = response.get("choices")[0].get("message").get("content")
        return jsonify({"comments":t})
        
    else:
        return "error"

@app.route("/flashcard", methods=['POST'])
def flashcard():
    content_type = request.headers.get('Content-Type')
    if(content_type == "application/json"):

        jso = request.get_json()
        print(jso)

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + key,
            }

        json_data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'user',
                    'content': "Based on this topic, make flashcards in the form of json code, using front and back as the two labels of the json card, something that I could create an in depth quizlet set on. Make the json have a list of json outputs which can be looped through to create actual flashcards. Include the major subtopics, as well as smaller ones. For the flashcards, add terms and definitions. Correct any spelling errors you encounter. /n " + jso.get("topic"),
                },
            ],
            'temperature': 0.7,
        }
        response = requests.post('https://api.openai.com/v1/chat/completions',headers=headers,json=json_data)
        response = json.loads(response.text)

        t = response.get("choices")[0].get("message").get("content").replace("\n","").replace("  ","").replace("\\","")
        
        return jsonify(json.loads(t))
    else:
        return "error"



#{excerpt: -____}
@app.route("/notes", methods=['POST'])
def notes():
    content_type = request.headers.get('Content-Type')
    if(content_type == 'application/json'):
        jso = request.get_json()
        sentence = jso.get("excerpt")
        

        # Preprocess sentence
        stop_words = set(nltk.corpus.stopwords.words('english'))
        stemmer = nltk.stem.porter.PorterStemmer()

        def preprocess(text):
            words = [stemmer.stem(word.lower()) for word in nltk.word_tokenize(text) if word.lower() not in stop_words and word.isalpha()]
            return ' '.join(words)


        preprocessed_sentence = preprocess(sentence)

        # Calculate TF-IDF scores
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform([preprocessed_sentence])

        # Summarize sentence
        scores = {j: tfidf[0, j] for j in range(tfidf.shape[1])}
        summary_sentences = sorted(scores, key=lambda x: scores[x], reverse=True)[:1]

        if summary_sentences:
            max_index = len(sent_tokenize(sentence)) - 1
            summary_sentences = [min(idx, max_index) for idx in summary_sentences] # Ensure the indexes are within range
            
            summary = ' '.join([sent_tokenize(sentence)[j] for j in summary_sentences])
            return jsonify({"sentence":summary})
        else:
            return jsonify({"sentence":"unable to retrieve summary, the application reached an error"})
                
    else:
        return "error"

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=random.randint(2000, 9000))