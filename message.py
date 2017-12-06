
class Message:
    def __init__(self):
        self.text = None
        self.speaker = None
        self.processing = False


    def get_text(self):
        return self.text


    def get_speaker(self):
        return self.speaker


    def is_processing(self):
        return self.processing


    def has_message(self):
        return self.text and self.speaker


    def set_text(self, text):
        self.text = text


    def set_speaker(self, speaker):
        self.speaker = speaker


    def set_processing(self, processing):
        self.processing = processing


    def send_message(self, conversation):
        uri="api/privateChat/addMessage"
        data = {
            'conversation': conversation,
            'speaker': self.speaker,
            'text': self.text
        }
        if self.text and self.speaker:
            print("\nnew message from %s:" % self.speaker)
            print('conversation: %s\ntext: %s\n' % (conversation, self.text))
        elif self.text:
            print('Message: %s\n' % self.text)
        elif self.speaker:
            print('Speaker: %s\n' % self.speaker)
        else:
            print('error processing input')