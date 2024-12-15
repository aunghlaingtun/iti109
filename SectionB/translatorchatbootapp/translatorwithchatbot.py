from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
import requests
import os
from dotenv import load_dotenv

# Detect the language of the input text
def detect_language(text, translator_key, translator_endpoint):
    url = f"{translator_endpoint}/detect?api-version=3.0"
    headers = {
        'Ocp-Apim-Subscription-Key': translator_key,
        'Content-Type': 'application/json'
    }
    body = [{'text': text}]
    response = requests.post(url, headers=headers, json=body)
    response_data = response.json()
    return response_data[0]['language']

# Translate text to a target language
def translate_text(text, target_lang, translator_key, translator_endpoint):
    url = f"{translator_endpoint}/translate?api-version=3.0&to={target_lang}"
    headers = {
        'Ocp-Apim-Subscription-Key': translator_key,
        'Content-Type': 'application/json'
    }
    body = [{'text': text}]
    response = requests.post(url, headers=headers, json=body)
    response_data = response.json()
    return response_data[0]['translations'][0]['text']

def main():
    try:
        # Load configuration settings
        load_dotenv()
        ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        ai_key = os.getenv('AI_SERVICE_KEY')
        ai_project_name = os.getenv('QA_PROJECT_NAME')
        ai_deployment_name = os.getenv('QA_DEPLOYMENT_NAME')
        
        # Translator API settings
        translator_key = os.getenv('TRANSLATOR_KEY')
        translator_endpoint = os.getenv('TRANSLATOR_ENDPOINT')

        # Create client using endpoint and key
        credential = AzureKeyCredential(ai_key)
        ai_client = QuestionAnsweringClient(endpoint=ai_endpoint, credential=credential)

        # Chatbot loop
        user_question = ''
        while user_question.lower() != 'quit':
            user_question = input('\nQuestion (or type "quit" to exit):\n')
            if user_question.lower() == 'quit':
                break
            
            # Step 1: Detect language
            detected_language = detect_language(user_question, translator_key, translator_endpoint)
            print(f"Detected language: {detected_language}")
            
            # Step 2: Translate input to English (if needed)
            if detected_language != 'en':
                user_question_en = translate_text(user_question, 'en', translator_key, translator_endpoint)
                print(f"Translated to English: {user_question_en}")
            else:
                user_question_en = user_question

            # Step 3: Query the Question Answering service
            response = ai_client.get_answers(
                question=user_question_en,
                project_name=ai_project_name,
                deployment_name=ai_deployment_name
            )

            # Step 4: Process and translate the response back
            for candidate in response.answers:
                answer = candidate.answer
                confidence = candidate.confidence
                print(f"\nBot (English): {answer} (Confidence: {confidence})")

                # Translate the answer back to the detected language
                if detected_language != 'en':
                    answer_translated = translate_text(answer, detected_language, translator_key, translator_endpoint)
                    print(f"Bot ({detected_language}): {answer_translated}")
                else:
                    print(f"Bot: {answer}")

    except Exception as ex:
        print(ex)
