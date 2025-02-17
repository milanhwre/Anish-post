from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp Message Sender</title>
</head>
<body>
    <h1>WhatsApp Message Sender</h1>
    <form method="POST">
        <label>Target Number (with country code):</label>
        <input type="text" name="number" required><br><br>
        <label>Message:</label>
        <textarea name="message" rows="4" required></textarea><br><br>
        <button type="submit">Send Message</button>
    </form>
</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        number = request.form["number"]
        message = request.form["message"]

        # Send data to Node.js server
        response = requests.post("http://localhost:3000/send", json={
            "number": number,
            "message": message
        })

        if response.status_code == 200:
            return f"Message sent to {number}!"
        else:
            return "Failed to send message. Please check the backend."

    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(debug=True)
