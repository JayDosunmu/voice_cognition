import random
import cognitive_sr
import os

from Identification.IdentificationServiceHttpClientHelper import IdentificationServiceHttpClientHelper

from api_clients import ChatClient, GoogleClient, SpeechToTextThread
from conversation import Conversation
from message import Message
from recorder import Recorder
from user import User, Users


class Controller:
    def __init__(self, file_name='speech.wav'):
        self.file_name = file_name
        self.running = True

        self.users = Users()
        self.msg = Message()
        self.conversation = None
        self.sr = IdentificationServiceHttpClientHelper(os.environ.get('MSKEY1', ''))
        self.recorder = Recorder()
        self.commands = {
            'enroll new profile': self.enroll,
            'start conversation': self.start_conversation,
            'sign into conversation': self.sign_into_conversation,
            'stop conversation': self.close_conversation,
            'close application': self.stop_running,
            'clear profiles': self.clear_profiles
        }


    def run_command(self, text):
        print('running command')
        if text in self.commands:
            self.commands[text]()

        else:
            words = text.split()
            command = ' '.join(words[:3])
            self.commands[command](' '.join(words[3:]))
        print('command completed\n')


    def is_command(self, text):
        is_command = False

        if text in self.commands:
            is_command = True
        elif ' '.join(text.split()[:3]) in self.commands:
            is_command = True

        if is_command:
            print('command detected')

        return is_command


    def enroll(self):
        g_client = GoogleClient()
        print('Starting speaker enrollment process')

        print('What is your name?')
        self.recorder.record_to_file('enroll.wav')
        # self.recorder.downsample('enroll.wav', 'enroll16k.wav')

        name = ''
        while not name:
            name = g_client.speech_to_text('enroll.wav')
            if name:
                user = self.users.new_user(name)
                profile = self.sr.create_profile('en-us')
                user.set_v_id(profile.get_profile_id())

                time = 60
                print('Ok %s please speak continously for %ds. The prompt below is a guide' % (user.get_name(), time))
                print(
                    "Did you ever hear the tragedy of Darth Plagueis the Wise?"
                    "I thought not. It's not a story the Jedi would tell you."
                    "It's a Sith legend. Darth Plagueis was a Dark Lord of the"
                    "Sith, so powerful and so wise he could use the Force to"
                    "influence the midichlorians to create life... He had such a"
                    "knowledge of the dark side that he could even keep the ones"
                    "he cared about from dying. The dark side of the Force is a"
                    "pathway to many abilities some consider to be unnatural."
                    "He became so powerful... the only thing he was afraid of was"
                    "losing his power, which eventually, of course, he did."
                    "Unfortunately, he taught his apprentice everything he knew,"
                    "then his apprentice killed him in his sleep. It's ironic"
                    "he could save others from death, but not himself."
                )

                transcript = ''
                while not transcript:
                    self.recorder.record_to_file('enroll.wav', time)
                    transcript = g_client.speech_to_text('enroll.wav')

                enrolled = self.sr.enroll_profile(user.get_v_id(), 'enroll.wav')
                print('%s, you were enrolled successfully!' % user.get_name())
            
    
    def clear_profiles(self):
        print("clearing profiles...")
        profiles = self.sr.get_all_profiles()

        for profile in profiles:
            self.sr.delete_profile(profile.get_profile_id())


    def start_conversation(self):
        print('starting a new conversation...')
        self.conversation = Conversation()

    
    def sign_into_conversation(self, participant):
        print('signing %s into conversation...' % participant)
        if not self.conversation.is_participant(participant):
            self.conversation.add_participant(participant)
        else:
            print("individual already in conversation!")


    def add_to_conversation(self):
        if self.conversation and self.msg.has_message():
            self.conversation.add_message(self.msg)
        else:
            print('You must start a conversation first: Say "start conversation"')

    
    def close_conversation(self):
        self.conversation = None


    def set_running(self, running):
        self.running = running


    def is_running(self):
        return self.running


    def stop_running(self):
        self.set_running(False)
        print('stopping controller')


    def run(self):
        self.recorder.record_to_file(self.file_name)

        if not self.msg.is_processing():
            self.msg = Message()

            self.msg.set_processing(True)
            speech_to_text_thread = SpeechToTextThread(msg=self.msg)
            
            speech_to_text_thread.start()
            speech_to_text_thread.join()

            if self.msg.get_text():
                if self.is_command(self.msg.get_text()):
                    self.run_command(self.msg.get_text())
                else:
                    if self.conversation:
                        result = self.sr.identify_file(
                            self.file_name,
                            self.users.all_users_v_ids(),
                            force_short_audio=True
                        )

                        speaker = ''
                        try:
                            if self.users.get_user_by_v_id(result.get_identified_profile_id()):
                                speaker = self.users.get_user_by_v_id(result.get_identified_profile_id()).get_name()
                        except:
                            speaker = 'Unknown'

                        self.msg.set_speaker(speaker);
                        self.add_to_conversation()
                    else:
                        print('\nPlease start a new conversation, or enroll voice ids\n')
                    
            self.msg.set_processing(False)
