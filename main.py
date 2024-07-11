
from time import sleep
from packaging import version
from flask import Flask, request, jsonify, session, render_template, send_from_directory, url_for
import openai
from openai import OpenAI
import functions
import eventhandler
import time
import logging
import instructions



required_version = version.parse("1.1.1")

current_version = version.parse(openai.__version__)
OPENAI_API_KEY = secret
if current_version < required_version:
  raise ValueError(f"Error: OpenAI version {openai.__version__}"
                   " is less than the required version 1.1.1")
else:
  print("OpenAI version is compatible.")

# Start Flask app
app = Flask(__name__)

app.secret_key = "secret"

# Init client
client = OpenAI(api_key=OPENAI_API_KEY)

# Create new assistant or load existing
#assistant_id = functions.create_assistant(client)
assistant_id = 'asst_tcnHUpUG0h9z8C0lziOGpEkX'  #alles zsm
assistantAI_id = 'asst_I8gIfnJDs2cMBF9Lfzb9a3BC' #alles zsm
assistantFT_id = 'asst_X5BBdIvtoumlOxpgzdAjuZu9' #ft , lehrbuch
assistantStory_id ='asst_tsdxN5yV92SP8zYNLMQSVc9b' #storline.docx
ass_bilanz_id = 'asst_toRJn9qKBiR4V4oNM7nKU5kK' #1_bilanzierung
finetuned_model = 'ft:gpt-3.5-turbo-0125:personal::97QirxUL"'

#NeuerTRYYY
assEvaStor = 'asst_BjtlSBuEQDMSB4wF1PSYVt7r'
assQues = 'asst_d1jPqqA3K8xbZ8LhotKUytfX'
vecQues = 'vs_panLZQs98el10obR2WaZFYaX'
vecEva = 'vs_lbnMK3bQ7nRe3KaraogLWNsj'
muster = 'file-mGxoLUri64NKDfY5LqureW26'

lesson_file_map = {
    "Bilanzierung": "file-eZ9HL7sf0bp49XP7fjn2BQpK",
    "Unternehmensziele Kennzahlen": "file-KOnhzJtSnDyse0R8WmJVdted",
    "Kostenrechnung": "file-DETWoOPkbEWl7DhV10sToHh5",
    "Investitionsrechnung": "file-uFW6bA2cnu1lI48JZazBRFj4",
    "Wirtschaftsrecht": "file-K2aUaNvccZXsxLD5dyv284Ul",
    "Finanzwesen": "file-t49PnIdN4jrLE7Zdqsmh9UgX"
}



@app.route('/')
def index():
    return render_template('testing_prototype.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('.', path)

# Start conversation thread
@app.route('/start', methods=['GET'])
def start_conversation():
  print("Starting a new conversation...")  # Debugging line
  thread = client.beta.threads.create()
  print(f"New thread created with ID: {thread.id}")  # Debugging line
  return jsonify({"thread_id": thread.id})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        thread_id = data.get('thread_id')
        user_input = data.get('message', '')
        lesson_choice = data.get('lesson', '')

        if not thread_id or not lesson_choice:
            logging.error("Error: Missing thread_id or lesson_choice")
            return jsonify({"error": "Missing thread_id or lesson_choice"}), 400

        # Get ID for lesson-choice
        file_id = lesson_file_map.get(lesson_choice)
        if not file_id:
            logging.error(f"No document found for lesson {lesson_choice}")
            return jsonify({"error": "Document not found"}), 404

        # Add the user's message to the thread 
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input,
            file_ids =[file_id]
        )

        # Run the Assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assQues,
            instructions = instructions.question_answer_instruction.format(user_input=user_input, lesson_choice=lesson_choice),
            tools=[{"type": "retrieval"}]  # Use 'retrieval' instead of 'file_search'
        )
        print("Thread ID:", thread_id)
        print("Assistant ID:", assistant_id)

        # Wait for completion
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if run_status.status == 'completed':
                break
            elif run_status.status == 'failed':
                logging.error("Run failed")
                return jsonify({"error": "Assistant run failed"}), 500
            time.sleep(1)

        # Retrieve and return the latest message 
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        response = messages.data[0].content[-1].text.value
        return jsonify({"response": response})
    except Exception as e:
        logging.exception("An error occurred: ")
        return jsonify({"error": str(e)}), 500

@app.route('/chatFT', methods=['POST'])
def chatFT():
    try:
        data = request.json
        print("Received data:", data)  # Debugging output
        thread_id = data.get('thread_id')
        user_input = data.get('message', '')

        if not thread_id:
            logging.error("Error: Missing thread_id")
            return jsonify({"error": "Missing thread_id"}), 400

        # Send user input to the Assistant
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )

        # Start the Assistant 
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistantFT_id,
            instructions = instructions.chitchat_instruction.format(user_input = user_input)
        )

        # Wait for the run to complete
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if run_status.status == 'completed':
                break
            elif run_status.status == 'failed':
                logging.error("Assistant run failed")
                return jsonify({"error": "Assistant run failed"}), 500
            time.sleep(1)

        # Retrieve and return the latest message 
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        response = messages.data[0].content[0].text.value

        return jsonify({"response": response})

    except Exception as e:
        logging.exception("An error occurred: %s", str(e))
        return jsonify({"error": str(e)}), 500



@app.route('/chatStory', methods=['POST'])
def chatStory():
    try:
        data = request.json
        thread_id = data.get('thread_id')
        calc_choice = data.get('calculation', '')
        user_input = data.get('user_input','')

        # Mapping function to get the file ID based on calculation choice
        calculation_file_map = {
            "1": "file-TAboqnFLBv21FrXL6Ro6Mnwy",
            "2": "file-ZBpjoawpmCJI3YzBYlTIQrMy",
            "3": "file-LCSh8q29p2u5i8mX3E17DYEQ",
            "4": "file-JiVjUxuF29qML5U3f1q7HP3J",
            "5": "file-fQpNh4oP6ConoUzwTFzmj8D0"
        }

        datasource = calculation_file_map.get(calc_choice)
        if not datasource:
            logging.error("Invalid calculation choice")
            return jsonify({"error": "Invalid calculation choice"}), 400

        if not thread_id:
            logging.error("Missing thread_id")
            return jsonify({"error": "Missing thread_id"}), 400

        # Add the calculation choice as a message 
        message_response = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input,
            file_ids=[datasource]
        )
        print(f"Message created: {message_response}")

        # Start the Assistant run
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assEvaStor,
            instructions=instructions.calculation2_instruction.format(datasource=datasource),
            tools=[{"type": "retrieval"}]
        )
        print(f"Run created: {run}")

        # Wait for the run to complete
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            print(f"Run status: {run_status.status}")
            if run_status.status == 'completed':
                break
            elif run_status.status == 'failed':
                logging.error("Assistant run failed")
                return jsonify({"error": "Assistant run failed"}), 500
            time.sleep(1)

        # Retrieve and return the latest message from the Assistant
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        if not messages.data:
            logging.error("No messages returned from the assistant")
            return jsonify({"error": "No messages returned from the assistant"}), 500

        response = messages.data[0].content[-1].text.value

        return jsonify({"response": response})
    except Exception as e:
        logging.exception("An error occurred: ")
        return jsonify({"error": str(e)}), 500



@app.route('/exam', methods=['GET', 'POST'])
def exam():
    if request.method == 'POST':
        data = request.json
        session['count'] = int(data.get('count', 0))
        session['score'] = float(data.get('score', 0.0))
        session['tax'] = int(data.get('tax', session.get('tax', 2)))

        if session['count'] <= 4:
            session['count'] += 1  # Erhöhe den Zähler hier # mit tax: question = functions.ask_question(session['count'], session['tax'])
            question = functions.ask_question(session['count'])  # Pass the count and tax to function
            return jsonify({"question": question, "count": session['count'], "score": session['score'], "tax": session['tax']}), 200
        else:
            return functions.evaluate_performance()  # Evaluate and return the result when done

    elif request.method == 'GET':
        session['score'] = 0
        session['count'] = 0
        if 'tax' not in session:
            session['tax'] = 2
        session['count'] += 1  # Start by incrementing count
        question = functions.ask_question(session['count'])  # Start with first question
        print(f"GET Request - Count: {session['count']}, Score: {session['score']}, Tax: {session['tax']}")
        return jsonify({"question": question, "count": session['count'], "score": session['score'], "tax": session['tax']}), 200



#evaluation mit Musterlösung da retrieval nicht kontinuierlich funktioniert...
@app.route('/evaluate2', methods=['POST'])
def evaluate2():
    try:
        data = request.json
        user_answer = data.get('user_answer')
        exam_question = data.get('exam_question')
        thread_id = data.get('thread_id')

        # Initialize session variables if not already done
        session['count'] = int(data.get('count', 0))
        session['score'] = float(data.get('score', 0.0))
        session['tax'] = int(data.get('tax', 2))

        print(f"Received data: {data}")

        if not user_answer or not exam_question or not thread_id:
            print(f"Missing data: user_answer={user_answer}, exam_question={exam_question}, thread_id={thread_id}")
            return jsonify({"error": "Missing data"}), 400

        model_answer = functions.get_exam_answer(exam_question)
        print(f'Musterlösung: {model_answer}')

        input_text = f"Prüfungsfrage: {exam_question}\nMusterlösung: {model_answer}\nNutzerantwort: {user_answer}\nBitte bewerte diese Antwort auf ihre Richtigkeit und Vollständigkeit auf Basis der  Musterlösung. Die Antwort muss nicht wortwörtlich der Musterlösung entsprechen, sollte aber inhaltlich übereinstimmen und alle wesentlichen Punkte der Frage beantworten.Sprich per 'Du' anstatt zu sagen 'Der Nutzer..' sage 'Du...' "

        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=input_text,
            file_ids=[muster]
        )


        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assEvaStor,
            instructions=instructions.evaluation_instruction
        )

        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            print(f"Run status: {run_status.status}")
            if run_status.status == 'completed':
                break
            elif run_status.status == 'failed':
                print("Assistant run failed")
                return jsonify({"error": "Assistant run failed"}), 500
            time.sleep(2)


        messages = client.beta.threads.messages.list(thread_id=thread_id)
        evaluation_response = messages.data[0].content[0].text.value

        evaluation = "Die Antwort ist nicht korrekt."
        if "Die Antwort ist korrekt" in evaluation_response:
            evaluation = "Die Antwort ist korrekt."
            session['score'] += 1
        elif "Die Antwort ist teilweise korrekt" in evaluation_response:
            evaluation = "Die Antwort ist teilweise korrekt."
            session['score'] += 0.5

        explanation = evaluation_response.replace(evaluation, "").strip()


        session['count'] += 1

        return jsonify({
            "evaluation_response": evaluation_response,
            "evaluation": evaluation,
            "explanation": explanation,
            "score": f"{session['score']:.1f}",
            "count": f"{session['count']}",
            "tax": f"{session['tax']}"
        }), 200

    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({"error": str(e)}), 500





#evaluation mit Knowledgebase anstatt Musterlösung -> wenn retrieval funktioniert ist dies die bessere option, da hier die evaluationen meist korrekt sind.

@app.route('/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.json
        file_id2 = 'file-bAiOG4a6ZvhT4E3IjB0nmrrF'
        user_answer = data.get('user_answer')
        exam_question = data.get('exam_question')
        thread_id = data.get('thread_id')
        session['count'] = int(data.get('count', 0))
        session['score'] = float(data.get('score', 0.0))
        session['tax'] = int(data.get('tax', session.get('tax', 2)))

        print(f"Received data: {data}")
        print(f"Session count after update: {session['count']}, Session score after update: {session['score']}")

        if not user_answer or not exam_question or not thread_id:
            print(f"Missing data: user_answer={user_answer}, exam_question={exam_question}, thread_id={thread_id}")
            return jsonify({"error": "Missing data"}), 400

        # Combining question and answer for context
        input_text = f"Question: {exam_question}\nAnswer: {user_answer}\nEvaluate this answer."
        client.beta.threads.messages.create(thread_id=thread_id, role="user", content=input_text, file_ids=[file_id2])

        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assEvaStor,
            instructions="""Evaluate the answer in german based on the attached document and either start your sentence with the words "Die Antwort ist korrekt" or "Die Antwort ist teilweise korrekt" or if its totally wrong "Die Antwort ist nicht korrekt". Gebe anschließend eine Erklärung wieso du diese Bewertung vorgenommen hast.""",
            tools=[{"type": "retrieval"}]
        )

        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            print(f"Run status: {run_status.status}")
            if run_status.status == 'completed':
                break
            elif run_status.status == 'failed':
                print("Assistant run failed")
                return jsonify({"error": "Assistant run failed"}), 500
            time.sleep(2)

        messages = client.beta.threads.messages.list(thread_id=thread_id)
        evaluation_response = messages.data[0].content[0].text.value

        # Initialize evaluation to avoid uninitialized variable reference
        evaluation = None

        # Extract evaluation and explanation
        if "Die Antwort ist korrekt" in evaluation_response:
            evaluation = "Die Antwort ist korrekt"
            session['score'] += 1
        elif "Die Antwort ist teilweise korrekt" in evaluation_response:
            evaluation = "Die Antwort ist teilweise korrekt"
            session['score'] += 0.5
        elif "Die Antwort ist nicht korrekt" in evaluation_response:
            evaluation = "Die Antwort ist nicht korrekt"
            session['score'] += 0
        else:
            print("Unexpected evaluation response")
            return jsonify({"error": "Unexpected evaluation response", "response": evaluation_response}), 500


        explanation = evaluation_response.replace(evaluation, "").strip()

        formatted_score = f"{session['score']:.1f}"
        formatted_count = f"{session['count']}"
        formatted_tax = f"{session['tax']}"

        return jsonify({
            "evaluation": evaluation,
            "explanation": explanation,
            "score": formatted_score,
            "count": formatted_count,
            "tax": formatted_tax
        }), 200

    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
