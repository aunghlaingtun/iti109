
from dotenv import load_dotenv
import os
import requests

# Import namespaces
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

# Translator API Configuration
TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com"
TRANSLATOR_REGION = "eastus"  # that must be match of your Azure translator service region 

#Translate text parts using Microsoft Azure Translator API.
def translate_text(text, to_language, from_language=None):
    
    translator_key = os.getenv('TRANSLATOR_KEY')
    headers = {
        "Ocp-Apim-Subscription-Key": translator_key,
        "Ocp-Apim-Subscription-Region": TRANSLATOR_REGION,
        "Content-Type": "application/json",
    }
    params = {"api-version": "3.0", "to": to_language}
    if from_language:
        params["from"] = from_language
    body = [{"text": text}]
    
    response = requests.post(f"{TRANSLATOR_ENDPOINT}/translate", headers=headers, params=params, json=body)
    response.raise_for_status()  # Raise exception if API call fails
    return response.json()[0]["translations"][0]["text"]

# Detecting parts  the language of the given text using Azure Translator API.
def detect_language(text):
    
    translator_key = os.getenv('TRANSLATOR_KEY')
    headers = {
        "Ocp-Apim-Subscription-Key": translator_key,
        "Ocp-Apim-Subscription-Region": TRANSLATOR_REGION,
        "Content-Type": "application/json",
    }
    params = {"api-version": "3.0"}
    body = [{"text": text}]

    response = requests.post(f"{TRANSLATOR_ENDPOINT}/detect", headers=headers, params=params, json=body)
    response.raise_for_status()  # Raise exception if API call fails
    return response.json()[0]["language"]

def main():
    try:
        # Get Configuration Settings
        load_dotenv()
        ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        ai_key = os.getenv('AI_SERVICE_KEY')
        ai_project_name = os.getenv('QA_PROJECT_NAME')
        ai_deployment_name = os.getenv('QA_DEPLOYMENT_NAME')

        # Translator API Key
        translator_key = os.getenv('TRANSLATOR_KEY')
        if not translator_key:
            raise ValueError("Missing TRANSLATOR_KEY in environment variables.")

        # Create client using endpoint and key
        credential = AzureKeyCredential(ai_key)
        ai_client = QuestionAnsweringClient(endpoint=ai_endpoint, credential=credential)

        # Submit a question and display the answer
        user_question = ''
        while user_question.lower() != 'quit':
            user_question = input('\nYour question (in any language):\n')

            # Step 1: Detect the user's input language
            detected_language = detect_language(user_question)

            # Step 2: Translate user input to English if necessary
            if detected_language != "en":
                translated_question = translate_text(user_question, to_language="en", from_language=detected_language)
            else:
                translated_question = user_question

            # Step 3: Get response from the QA service
            response = ai_client.get_answers(
                question=translated_question,
                project_name=ai_project_name,
                deployment_name=ai_deployment_name
            )

            # Step 4: Process the response and translate it back to the user's language
            if response.answers:
                for candidate in response.answers:
                    if detected_language != "en":
                        translated_answer = translate_text(candidate.answer, to_language=detected_language, from_language="en")
                        print(f"[Answer]: {translated_answer}")
                    else:
                        print(f"[Answer]: {candidate.answer}")
                    print("Confidence: {}".format(candidate.confidence))
                    print("Source: {}".format(candidate.source))
            else:
                print("No suitable answer found.")

    except Exception as ex:
        print(ex)

if __name__ == "__main__":
    main()

