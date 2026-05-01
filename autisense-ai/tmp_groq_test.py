from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
print('GROQ_API_KEY set:', api_key is not None)
client = Groq(api_key=api_key)
print('client type:', type(client))
print('dir client contains model:', any('model' in n.lower() for n in dir(client)))
print('chat completions available:', hasattr(client.chat, 'completions'))
print('chat completions type:', type(client.chat.completions))

# If the client has a models listing endpoint, print it
if hasattr(client, 'models'):
    print('client.models exists')
    print('models attrs:', [n for n in dir(client.models) if not n.startswith('_')])
try:
    print('attempting sample usage introspection:')
    comp = client.chat.completions
    print('completions attrs:', [n for n in dir(comp) if not n.startswith('_')])
except Exception as e:
    print('introspection failed:', type(e).__name__, e)
