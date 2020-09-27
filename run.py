# Create a Flask App (app.py)¶
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from credentials_watson_discovery import watson_discovery, apikey_discovery
from credentials_watson_speech import whatson_speech, apikey_speech

from twilio.rest import Client

import requests
import unicodedata
import json
import requests

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, World!"


def send_media_twilio(output_file: str, to_number: str):
    client = Client(username="ACf47c27768333a71fba64a1046fcb3270", password="7ee298e457787578499cc5f2d48e38da")
    from_whatsapp_number = "whatsapp:+14155238886"  # Bot number
    to_whatsapp_number = f"whatsapp:{to_number}"
    message = client.messages.create(body="Check out",
                                     media_url=output_file,
                                     from_=from_whatsapp_number,
                                     to=to_whatsapp_number)
    print(message.sid)


def data_remove_char(text: str):
    text = text.replace("ç", "ss").replace("x", "ss")
    string_nova = ''.join(ch for ch in unicodedata.normalize('NFKD', text)
                          if not unicodedata.combining(ch))
    string_nova = string_nova.replace(".", "").replace(",", "")
    return string_nova


def watson_request_audio(text: str):
    text = data_remove_char(text)
    headers = {'Content-Type': 'application/json',
               'Accept': 'audio/wav'}

    params = (('voice', 'pt-BR_IsabelaVoice'),)
    data = '{"text":"' + text + '"}'
    response = requests.post(whatson_speech, headers=headers, params=params,
                             data=data, auth=('apikey', apikey_speech))

    if response:
        with open("whatsapp.ogg", "wb") as fb:
            fb.write(response.content)


def watson_request(text: str):
    params = (('version', '2019-04-30'),
              ('query', text),)
    try:
        response = requests.get(watson_discovery, params=params, auth=('apikey', apikey_discovery))
        if response:
            get_query = json.loads(response.content)

        score_current = 0
        index_score = 0
        for index, current in enumerate(get_query['results']):
            score = current['result_metadata']['score']
            if score >= score_current:
                score_current = score
                index_score = index
        text_body = get_query['results'][index_score]['descricao']
        watson_request_audio(text_body)
        return text_body
    except:
        return 'documento não encontrado!'


@app.route("/sms", methods=['POST'])
def sms_reply():
    msg = request.form.get('Body')
    resp = MessagingResponse()
    resp.message(watson_request(msg))

    print(str(resp))
    return str(resp)


if __name__ == "__main__":
    app.run(debug=False)
