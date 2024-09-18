from flask import Flask, request, render_template_string
import requests
import re
import time
import threading
from requests.exceptions import RequestException

app = Flask(__name__)

class FacebookCommenter:
    def __init__(self):
        self.comment_count = 0

    def comment_on_post(self, cookies, post_id, comment, delay):
        with requests.Session() as r:
            r.headers.update({
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'sec-fetch-site': 'none',
                'accept-language': 'id,en;q=0.9',
                'Host': 'mbasic.facebook.com',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-encoding': 'gzip, deflate',
                'sec-fetch-mode': 'navigate',
                'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.166 Mobile Safari/537.36',
                'connection': 'keep-alive',
            })

            response = r.get(f'https://mbasic.facebook.com/{post_id}', cookies={"cookie": cookies})

            next_action_match = re.search('method="post" action="([^"]+)"', response.text)
            if next_action_match:
                self.next_action = next_action_match.group(1).replace('amp;', '')
            else:
                print("<Error> Next action not found")
                return

            fb_dtsg_match = re.search('name="fb_dtsg" value="([^"]+)"', response.text)
            if fb_dtsg_match:
                self.fb_dtsg = fb_dtsg_match.group(1)
            else:
                print("<Error> fb_dtsg not found")
                return

            jazoest_match = re.search('name="jazoest" value="([^"]+)"', response.text)
            if jazoest_match:
                self.jazoest = jazoest_match.group(1)
            else:
                print("<Error> jazoest not found")
                return

            data = {
                'fb_dtsg': self.fb_dtsg,
                'jazoest': self.jazoest,
                'comment_text': comment,
                'comment': 'Submit',
            }

            r.headers.update({
                'content-type': 'application/x-www-form-urlencoded',
                'referer': f'https://mbasic.facebook.com/{post_id}',
                'origin': 'https://mbasic.facebook.com',
            })

            response2 = r.post(f'https://mbasic.facebook.com{self.next_action}', data=data, cookies={"cookie": cookies})

            if 'comment_success' in str(response2.url) and response2.status_code == 200:
                self.comment_count += 1
                print(f"Comment successfully posted: {comment}")
            else:
                print(f"Failed to post comment: {comment}, URL: {response2.url}, Status Code: {response2.status_code}")

    def handle_inputs(self, cookie_file, post_id, kidx_name, comment_file, delay):
        try:
            your_cookies = cookie_file.read().splitlines()

            if len(your_cookies) == 0:
                print("<Error> The cookies file is empty")
                return

            comments = comment_file.read().splitlines()
            cookie_index = 0

            for comment in comments:
                comment = kidx_name + ' ' + comment.strip()
                if comment:
                    time.sleep(delay)
                    self.comment_on_post(your_cookies[cookie_index], post_id, comment, delay)
                    cookie_index = (cookie_index + 1) % len(your_cookies)
        except RequestException as e:
            print(f"<Error> {str(e).lower()}")
        except Exception as e:
            print(f"<Error> {str(e).lower()}")
        except KeyboardInterrupt:
            pass

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        cookies_file = request.files['cookies_file']
        post_id = request.form['post_id']
        kidx_name = request.form['kidx_name']
        comment_file = request.files['comment_file']
        delay = int(request.form['delay'])

        commenter = FacebookCommenter()
        threading.Thread(target=commenter.handle_inputs, args=(cookies_file, post_id, kidx_name, comment_file, delay)).start()

        return "Commenting started. Check the console for details."

    return render_template_string('''
        <!doctype html>
        <html>
        <head>
            <title>Facebook Commenter</title>
            <style>
                body {
                    background: linear-gradient(to right, #ff9966, #ff5e62);
                    font-family: Arial, sans-serif;
                    color: #ffb6c1;
                }
                .container {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    flex-direction: column;
                }
                form {
                    background-color: #ffffff;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }
                label, input {
                    font-size: 18px;
                    color: pink;
                }
                input[type="text"], input[type="file"] {
                    width: 100%;
                    padding: 10px;
                    margin: 10px 0;
                    box-sizing: border-box;
                    border: 2px solid #3498db;
                    border-radius: 4px;
                }
                input[type="submit"] {
                    background-color: #3498db;
                    color: pink;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                input[type="submit"]:hover {
                    background-color: #2980b9;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Facebook Commenter</h1>
                <form method="POST" enctype="multipart/form-data">
                    <label>Post ID:</label><br>
                    <input type="text" name="post_id" required><br><br>

                    <label>Kidx Name:</label><br>
                    <input type="text" name="kidx_name" required><br><br>

                    <label>Cookies File:</label><br>
                    <input type="file" name="cookies_file" required><br><br>

                    <label>Comments File:</label><br>
                    <input type="file" name="comment_file" required><br><br>

                    <label>Delay (in seconds):</label><br>
                    <input type="text" name="delay" required><br><br>

                    <input type="submit" value="Start Commenting">
                </form>
            </div>
        </body>
        </html>
    ''')

if __name__ == "__main__":
    app.run(port=5000, debug=True)
