@app.route('/chatFT2', methods=['POST'])
def chatFT2():
    try:
        data = request.json
        print("Received data:", data)  # Debugging output
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
            model=finetuned_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to converse on business administration topics, providing suggestions and engaging users with motivational talks in German. Speak directly and encourage questioning to prompt further thinking.use Emojis sometimes"},
                {"role": "user", "content": user_input}
            ]
        )

        # Die Antwort des Modells extrahieren
        chat_response = response.choices[0].message.content

        return jsonify({"response": chat_response}), 200

    except Exception as e:
        print("Ein Fehler ist aufgetreten:", str(e))
        return jsonify({"error": str(e)}), 500


