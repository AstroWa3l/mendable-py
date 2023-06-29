import os
import requests
import time

class ChatApp:
    def __init__(self):
        self.api_key = os.getenv('MENDABLE_API_KEY')
        self.conversation_id = self._get_new_conversation_id()
        self.history = []

    def _get_new_conversation_id(self):
        new_conversation_response = requests.post("https://api.mendable.ai/v0/newConversation", json={"api_key": self.api_key}).json()
        if new_conversation_response.get('conversation_id'):
            return new_conversation_response['conversation_id']
        else:
            raise Exception('Failed to create a new conversation')

    def add(self, _type, url):
        task_id = self._start_ingestion(_type, url)
        while True:
            status = self._check_ingestion_status(task_id)
            if status == 'completed':
                print('Ingestion completed.')
                break
            elif status in ['queued', 'processing', 'pending']:
                print(f'Ingestion status: {status}')
                time.sleep(2.5)
            else:
                raise Exception('Unknown ingestion status')


    def _start_ingestion(self, _type, url):
        response = requests.post("https://api.mendable.ai/v0/ingestData", json={"api_key": self.api_key, "url": url, "type": _type}).json()
        if response.get('task_id'):
            return response['task_id']
        else:
            raise Exception('Failed to start data ingestion')
        

    def _check_ingestion_status(self, task_id):
        response = requests.post("https://api.mendable.ai/v0/ingestionStatus", json={"task_id": task_id, "api_key": self.api_key}).json()
        status = response.get('status')
        if status:
            if status in ['completed', 'queued', 'processing', 'pending']:
                return status
            else:
                print(f'Unexpected ingestion status: {status}')
                raise Exception('Unknown ingestion status')
        else:
            raise Exception('Failed to check ingestion status')



    def query(self, question):
        response = requests.post("https://api.mendable.ai/v0/mendableChat", json={
            "api_key": self.api_key,
            "question": question,
            "history": self.history,
            "conversation_id": self.conversation_id,
            "shouldStream": False
        }).json()
        if response.get('answer') and response['answer'].get('text'):
            return response['answer']['text']
        else:
            raise Exception('Failed to send the question or receive an answer')