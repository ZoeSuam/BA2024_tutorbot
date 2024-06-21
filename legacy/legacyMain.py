
from time import sleep
from packaging import version
from flask import Flask, request, jsonify, session, render_template, send_from_directory, url_for
import openai
from openai import OpenAI
import functions
import eventhandler
import time
import logging




# Check OpenAI version is correct
required_version = version.parse("1.1.1")

current_version = version.parse(openai.__version__)
#OPENAI_API_KEY = secret_key
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

#NeuerTRYYY
assEvaStor = 'asst_BjtlSBuEQDMSB4wF1PSYVt7r'
assQues = 'asst_d1jPqqA3K8xbZ8LhotKUytfX'
vecQues = 'vs_panLZQs98el10obR2WaZFYaX'
vecEva = 'vs_lbnMK3bQ7nRe3KaraogLWNsj'


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

        # Get the file ID for the selected lesson
        file_id = lesson_file_map.get(lesson_choice)
        if not file_id:
            logging.error(f"No document found for lesson {lesson_choice}")
            return jsonify({"error": "Document not found"}), 404

        # Add the user's message to the thread and attach the file
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
            instructions=f"Please answer the user's question ({user_input}) about the topic for {lesson_choice} . Use emojis occasionally.",
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

        # Retrieve and return the latest message from the assistant
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

        # Start the Assistant with dynamic instructions
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistantAI_id,
            instructions="Führe das Gespräch zum Thema Betriebswirtschaft  fort und gehe dabei auf die vorherige Frage ein: {user_input}. Du sprichst mit dem Schüler direkt und auf augenhöhe.Deine Funktion ist en bisschen chitchat über BWL zu betreiben, gebe dem User auch gerne neue Anregungen oder Ideen mit welchen betriebswirtschaftlichen themen er sich beschäftigen könnte. Sei motivierend und Überzeugt von der Materie.Nimm dem User die Langeweile und stelle auch gerne Gegenfragen um das weitere Auseinandersetzen mit den Inhalten zu fördern."
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

        # Retrieve and return the latest message from the assistant
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        response = messages.data[0].content[0].text.value

        return jsonify({"response": response})

    except Exception as e:
        logging.exception("An error occurred: %s", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/chatFT2', methods=['POST'])
def chatFT2():
    try:
        data = request.json
        thread_id = data.get('thread_id')
        user_input = data.get('message', '')

        if not user_input:
            return jsonify({"error": "Missing user input"}), 400

        # Debugging: Ausgabe der verfügbaren Methoden und Attribute des client-Objekts
        print("Debugging: Ausgabe der verfügbaren Methoden und Attribute des client-Objekts")
        print(dir(client))
        print("Ist 'chat' im client verfügbar?:", 'chat' in dir(client))
        print("Ist 'ChatCompletion' im client verfügbar?:", 'ChatCompletion' in dir(client))

        # Rufe die Chat Completion API mit einer Sequenz von Nachrichten auf
        response = client.chat.completions.create(
            model="ft:gpt-3.5-turbo-0125:personal::97QirxUL",
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to converse on business administration topics, providing suggestions and engaging users with motivational talks in German. Speak directly and encourage questioning to prompt further thinking."},
                {"role": "user", "content": user_input}
            ]
        )

        # Die Antwort des Modells extrahieren
        chat_response = response.choices[0].message.content

        return jsonify({"response": chat_response}), 200

    except Exception as e:
        print("Ein Fehler ist aufgetreten:", str(e))
        return jsonify({"error": str(e)}), 500





@app.route('/chatStory', methods=['POST'])
def chatStory():
    try:
        data = request.json
        thread_id = data.get('thread_id')
        user_input = data.get('message', '')
        file_id2 = 'file-bAiOG4a6ZvhT4E3IjB0nmrrF'
        file_rechnungen = 'file-3kH5IN8YAniHDpMEiqkoZCpR'


        if not thread_id:
            logging.error("Missing thread_id")
            return jsonify({"error": "Missing thread_id"}), 400

        # Add user input as a message and attach document
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input,
            file_ids = [file_id2, file_rechnungen]
        )

        # Start the Assistant run
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assEvaStor,
            instructions="Du bist ein Lerntutor für einen Betriebswirtschafts-Kurs. Nutze das Knowledge retrieval, um eine Rechenaufgabe zu stellen. Dafür guckst du bitte in die angehängte file_id2 und suchst nach den blau gedruckten passagen. Diese beschreiben praxisbeispiele für Rechnungen der BWL am Bespiel der Pizzeria Bossi. Gebe dem User eine entsprechende anwendungsbezogene rechenaufgabe aus der File und bewerte die Antwort anschließend.Sprich immer deutsch und sei cool , verwende auch gerne hier und da emojis. Wenn du kein passendes Rechenbeispiel zu der Anfrage findest dann denk dir bitte eine logische Rechnung am Anwendungsbeispiel der Pizzeria mit selbst gewählten werten aus. Oder guck in die andere File, da stehen weitere Rechnungen.Wenn die User dir keine Antwort geben wollen versuche nicht direkt die lösung vorweg zu nehmen sondern vielmehr mit tipps (zb. dem vorgeben der Formel oder so) beiseite zu stehen",
            tools=[{"type": "retrieval"}],

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

        # Retrieve and return the latest message from the Assistant
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        response = messages.data[-1].content[0].text.value

        return jsonify({"response": response})

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
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

        # Remove evaluation from response to get the explanation
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