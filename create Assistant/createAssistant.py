import os
import json
import openai
from openai import OpenAI

def create_assistant(client, name, instructions, model="gpt-3.5-turbo-0125"):
    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        model=model,
        tools=[{"type": "file_search"}]
    )
    return assistant

def create_and_populate_vector_store(client, name, file_paths):
    # Create a vector store
    vector_store = client.beta.vector_stores.create(name=name)

    # Prepare the file streams for upload
    file_streams = [open(path, "rb") for path in file_paths]

    # Use the upload and poll SDK helper to upload the files, add them to the vector store,
    # and poll the status of the file batch for completion.
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    # Print the status and the file counts of the batch to see the result of this operation.
    print(file_batch.status)
    print(file_batch.file_counts)

    return vector_store

def update_assistant_with_vector_store(client, assistant_id, vector_store_id):
    updated_assistant = client.beta.assistants.update(
        assistant_id=assistant_id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
    )
    return updated_assistant

def main():
    openai.api_key = os.getenv('OPENAI_API_KEY')
    openai.api_version = "beta"
    client = OpenAI(api_key=openai.api_key)

    # File paths for lesson-specific files
    lesson_file_paths = [
        "data/1_bilanzierung.docx",
        "data/2_UnternehmenszieleKennzahlen.docx",
        "data/3_Kostenrechnung.docx",
        "data/4_Investitionsrechnung.docx",
        "data/5_Wirtschaftsrecht.docx",
        "data/6_Finanzwesen.docx"
    ]

    # Comprehensive file for calculations and evaluations
    comprehensive_file_path = ["data/document.pdf"]

    # Create assistant for lesson questions
    assistant_lessons = create_assistant(
        client,
        name='Ebc*l Coach Clara for Lessons',
        instructions="You are a business administration tutor for students studying an online ebc*l course to get a license. Answer questions about the course materials for lessons 1-6."
    )
    print(f"Created Assistant for Lessons with ID: {assistant_lessons.id}")

    # Create and populate vector store for lesson-specific files
    vector_store_lessons = create_and_populate_vector_store(client, "Lesson Materials", lesson_file_paths)
    print(f"Created Vector Store for Lessons with ID: {vector_store_lessons.id}")

    # Update assistant with vector store for lessons
    updated_assistant_lessons = update_assistant_with_vector_store(client, assistant_lessons.id, vector_store_lessons.id)
    print(f"Updated Assistant for Lessons with ID: {updated_assistant_lessons.id}")

    # Create assistant for calculations and evaluations
    assistant_evaluations = create_assistant(
        client,
        name='Ebc*l Coach Clara for Evaluations',
        instructions="You are a business administration tutor for students studying an online ebc*l course to get a license. Help with calculations and evaluate student answers to exam questions."
    )
    print(f"Created Assistant for Evaluations with ID: {assistant_evaluations.id}")

    # Create and populate vector store for comprehensive document
    vector_store_evaluations = create_and_populate_vector_store(client, "Evaluation Materials", comprehensive_file_path)
    print(f"Created Vector Store for Evaluations with ID: {vector_store_evaluations.id}")

    # Update assistant with vector store for evaluations
    updated_assistant_evaluations = update_assistant_with_vector_store(client, assistant_evaluations.id, vector_store_evaluations.id)
    print(f"Updated Assistant for Evaluations with ID: {updated_assistant_evaluations.id}")

if __name__ == '__main__':
    main()
