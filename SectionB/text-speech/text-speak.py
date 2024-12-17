from dotenv import load_dotenv
import os
import requests
import azure.cognitiveservices.speech as speechsdk

# Import namespaces
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

 #Convert text to speech using Azure Speech Service.
def text_to_speech(text):

    speech_key = os.getenv('SPEECH_KEY')
    speech_region = os.getenv('SPEECH_REGION')

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    result = speech_synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesis completed.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")

def main():
    try:
        # Get Configuration Settings
        load_dotenv()
        ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        ai_key = os.getenv('AI_SERVICE_KEY')
        ai_project_name = os.getenv('QA_PROJECT_NAME')
        ai_deployment_name = os.getenv('QA_DEPLOYMENT_NAME')

        # Create client using endpoint and key
        credential = AzureKeyCredential(ai_key)
        ai_client = QuestionAnsweringClient(endpoint=ai_endpoint, credential=credential)

        # Submit a question and display the answer
        user_question = ''
        while user_question.lower() != 'quit':
            user_question = input("\nYour question (type 'quit' to exit): ")

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
                    print(f"[listen please myAnswer]: {candidate.answer}")
                    print("Confidence: {}".format(candidate.confidence))
                    print("Source: {}".format(candidate.source))

                    # Convert the answer to speech
                    text_to_speech(candidate.answer)
            else:
                print("No suitable answer found.")

    except Exception as ex:
        print(f"Error: {ex}")

if __name__ == "__main__":
    main()
