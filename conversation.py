class Conversation:
    """
        Conversation class will hold methods and data pertaining to a conversation
        Fields:
            id (int)
            participants (list)
            messages (list)

        Methods:
            add_message(Participant, Message)
            add_participant
    """
    def __init__(self, id=0):
        self.id = id
        self.participants = []
        self.messages = []


    def add_message(self, message):
        self.participants.append(message.get_speaker())
        self.messages.append(message)
        message.send_message(self.id)


    def add_participant(self, participant):
        self.participants.append(participant)

    
    def is_participant(self, participant):
        return participant in self.participants



    