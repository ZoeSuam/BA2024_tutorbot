import os

from openai import OpenAI
import os
def upload_file_and_finetune(file_path, model_name, api_key):

    openai_api_key = os.getenv("OPENAI_API_KEY")

    client = OpenAI(api_key=openai_api_key)

    try:
        # Upload the .jsonl file
        upload_response = client.files.create(
            file=open(file_path, "rb"),
            purpose="fine-tune"
        )
        print(f"File uploaded successfully. File ID: {upload_response.id}")

        # Create a fine-tuning job using the uploaded file
        fine_tune_response = client.fine_tuning.jobs.create(
            training_file=upload_response.id,
            model=model_name
        )
        print(f"Fine-tuning job created successfully. Job ID: {fine_tune_response.id}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

        

if __name__ == '__main__':
    # Make sure to replace the following placeholders with your actual data and API key
    upload_file_and_finetune("ParsedConversations3.jsonl", "gpt-3.5-turbo-0125", api_key)

