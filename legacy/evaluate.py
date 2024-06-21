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
