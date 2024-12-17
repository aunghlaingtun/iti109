from dotenv import load_dotenv
import os
import requests
import azure.cognitiveservices.speech as speechsdk

# Import namespaces
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

# Convert speech input to text parts added  using Azure Speech Service
def speech_to_text():

    speech_key = os.getenv('SPEECH_KEY')
    speech_region = os.getenv('SPEECH_REGION')
    
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    print("Speak into your microphone...")
    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"Recognized: {result.text}")
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech recognized. Please try again.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech Recognition canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")
    return ""

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

        # Create client using endpoint and key
        credential = AzureKeyCredential(ai_key)
        ai_client = QuestionAnsweringClient(endpoint=ai_endpoint, credential=credential)

        # Submit a question and display the answer
        user_question = ''
        while user_question.lower() != 'quit':
            print("\nSay your question (or type 'quit' to exit):")
            user_question = speech_to_text()

            if not user_question or user_question.lower() == 'quit':
                print("Goodbye!")
                break

            # Get response from the QA service
            response = ai_client.get_answers(
                question=user_question,
                project_name=ai_project_name,
                deployment_name=ai_deployment_name
            )

            # Process the response
            if response.answers:
                for candidate in response.answers:
                    print(f"[Answer]: {candidate.answer}")
                    print("Confidence: {}".format(candidate.confidence))
                    print("Source: {}".format(candidate.source))
            else:
                print("No suitable answer found.")

    except Exception as ex:
        print(f"Error: {ex}")

if __name__ == "__main__":
    main()

