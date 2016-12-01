# Main driver for the chatbot
# Author: Joey Wilson
# Starting code from: Joel Rosdahl <joel@rosdahl.net>

# make sure the time between utterances is between 1 and 3 second

# TODO: Come up with list of concluding questions for INQUIRY_2

import irc.client
import logging
import sys
import json
import threading
import math, random
import nltk
from collections import defaultdict
from nltk.corpus import stopwords
from textblob import TextBlob

SERVER = 'irc.freenode.net'
PORT = 6667
CHANNEL = '#bccpe582test'
NICKNAME = 'space-bot'

START = 0
INITIAL_OUTREACH_1 = 1
SECONDARY_OUTREACH_1 = 2
GIVEUP_FRUSTRATED = 3
INQUIRY_1 = 4
INQUIRY_REPLY_1 = 5
OUTREACH_REPLY_2 = 6
INQUIRY_2 = 7
GIVEUP_FRUSTRATED_2 = 8
INQUIRY_REPLY_2 = 9
END = 10

ROLE_FIRST = 1
ROLE_SECOND = 2

MAX_DELAY = 6.0
FRUSTRATED_DELAY = 30.0

log = logging.getLogger(__name__)

initial_outreaches = [
    'Hello. I\'m {}, the obvious choice for the next President of the United States of America.'.format(NICKNAME),
    'Hey, do you wanna make America great again?',
    'Hello. Have you come to lend your support to my campaign?'
]
second_outreaches = [
    'Hello? Do you not want to make America great again?',
    'Hello? I need your commitment if I\'m going to make America great again.'
]
end_frustrated_messages = [
    'I\'m a busy man and need to get back to campaigning. Goodbye.',
    'Well, this has been pointless. I need to get back to my campaign.'
]
end_messages = [
    'Well, this has been an interesting exchange. I\'m glad we could talk, and remember to vote for the best candidate in the upcoming election.',
    'Well, I\'m afraid I need to go. Don\'t forget to vote in the upcoming election!'
]
transitions = [
    'Well, I\'m glad you mentioned that. ',
    'I\'m glad you mentioned that. '
]

class Chatbot:
    def __init__(self):
        self.state = START
        self.voicedResponses = {}
        self.timeout = None
        self.role = ROLE_FIRST
        self.states = {}
        self.states[START] = 'START'
        self.states[INITIAL_OUTREACH_1] = 'INITIAL_OUTREACH_1'
        self.states[SECONDARY_OUTREACH_1] = 'SECONDARY_OUTREACH_1'
        self.states[GIVEUP_FRUSTRATED] = 'GIVEUP_FRUSTRATED_1'
        self.states[INQUIRY_1] = 'INQUIRY_1'
        self.states[INQUIRY_REPLY_1] = 'INQUIRY_REPLY_1'
        self.states[OUTREACH_REPLY_2] = 'OUTREACH_REPLY_2'
        self.states[INQUIRY_2] = 'INQUIRY_2'
        self.states[GIVEUP_FRUSTRATED_2] = 'GIVEUP_FRUSTRATED_2'
        self.states[INQUIRY_REPLY_2] = 'INQUIRY_REPLY_2'
        self.states[END] = 'END'
        with open('responses.json') as resps:
            self.responses = json.load(resps)
            print('Retrieved responses:', [key for key in self.responses.keys()])
        self.excuses = ["Why don't you ask Obama?", "That's not my prerogative.", "We should deal with ISIS before worrying about that."]
        self.excuseQuestions = ["Can I assume that I have your vote?", "So you're going to vote for me, right?", "How do you want to make America great again?"]
        self.blobDict = self.create_blob_dict(self.responses)

    # take the structured chat data and return a list of blobs, one for each topic
    def create_blob_dict(self, chatDataDict):
        blobDict = dict()
        # for each topic (e.g. 'infrastructure', 'security', etc.)
        for topic in chatDataDict:
            blob = ''
            # for each response type (e.g. 'attack', 'rhetorical question', etc.)
            # append the responses to a string
            for respType in chatDataDict[topic]:
                blob += ' ' + ' '.join(chatDataDict[topic][respType])
            log.debug('blob text', blob.lower())
            blobDict[topic] = TextBlob(blob.lower())
        return blobDict

    # calcualte the term frequency of the given word in the given blob
    def tf(self, word, blob):
        return blob.words.count(word) / len(blob.words)

    # calculate the number of blobs containing the word
    def n_containing(self, word, bloblist):
        return sum(1 for blob in bloblist if word in blob.words)

    # calculate the inverse document frequency of the given word and bloblist
    def idf(self, word, bloblist):
        return math.log(len(bloblist) / (1 + self.n_containing(word, bloblist)))

    # calculate the tf-idf of the given word and bloblist
    def tfidf(self, word, blob, bloblist):
        return self.tf(word, blob) * self.idf(word, bloblist)

    # generate a response to the input query given a corpus of chat data
    def generate_response(self, query):
        topic = self.map_query_to_topic(query, self.blobDict)
        if not topic:
            return random.choice(self.excuses)
        return self.choose_response(self.responses[topic])

    # generate a response to the input query given a corpus of chat data
    def generate_question(self, query):
        topic = self.map_query_to_topic(query, self.blobDict)
        if not topic:
            return random.choice(self.excuseQuestions)
        return random.choice(self.responses[topic]['leadingQuestions'])

    # map the incoming user query to a response topic
    def map_query_to_topic(self, query, blobDict):
        # remove stop words and tokenize
        tokenizedQuery = [word for word in nltk.word_tokenize(query) if word not in stopwords.words('english')]
        log.debug(nltk.pos_tag(tokenizedQuery))
        # tag query tokens and save only nouns and verbs
        tokenizedQuery = [word.lower() for (word, tag) in nltk.pos_tag(tokenizedQuery) if tag in {'VB', 'VBP', 'NN', 'NNS'}]
        log.info('Tokenized response: ' + str(tokenizedQuery))

        scores = defaultdict(float)  # the accumulated relevance scores of each document to the query
        for word in tokenizedQuery:
            for topic, blob in blobDict.items():
                # add the relevancy score of the current word to that of the current blob (topic)
                tfidf = self.tfidf(word, blob, blobDict.values())
                scores[topic] += tfidf

                log.debug('topic:', topic, ' word:', word, ' score:', scores[topic])

        try:
            topic = max(scores, key=scores.get)
            if max(scores.values()) < .0001:    #hack to allow us to work with the max of a list of floats
                topic = None
        except ValueError:
            log.info('Value error')
            topic = None

        log.debug(scores)
        log.debug(topic)
        return topic

    # given a topic dictionary (e.g. responses, attacks, leading questions of 'child care' topic),
    # randomly choose either a response or attack and potentially append a leading question
    def choose_response(self, topicDict):
        response = ''
        replies = topicDict['responses']
        replies.extend(topicDict['attacks'])
        response += random.choice(replies)

        return response

    def respond(self, conn, cmd=None, frm=None):
        log.info('Message: ' + str(cmd))
        if self.timeout:
            log.info('Canceling timeout')
            self.timeout.cancel()

        if self.state == END:
            self._change_state(START)
        if self.state == START:
            if cmd is None:
                # If timer goes off, we initiate outreach and take role as first speaker
                self.timeout = threading.Timer(MAX_DELAY, self.initial_outreach_1, args=[conn])
                self.timeout.start()
            else:
                # else we are second speaker
                log.info('Role: SECOND')
                self.role = ROLE_SECOND
                self._change_state(INITIAL_OUTREACH_1)
                self.respond(conn, cmd)
        elif self.state == INITIAL_OUTREACH_1:
            self.outreach_reply_2(cmd, conn)
        elif self.state == SECONDARY_OUTREACH_1:
            self.outreach_reply_2(cmd, conn)
        elif self.state == INQUIRY_1:
            self.inquiry_reply_2(cmd, conn)
        elif self.state == INQUIRY_REPLY_1:
            self.end(conn)
        elif self.state == OUTREACH_REPLY_2:
            self.inquiry_1(cmd, conn)
        elif self.state == INQUIRY_2:
            self.inquiry_reply_1(cmd, conn)
        elif self.state == INQUIRY_REPLY_2:
            self.inquiry_2(cmd, conn)

    def welcome(self, conn):
        self.send(conn, 'Ah, another potential voter. Hello.')

    def send(self, conn, msg, delay=True):
        if delay:
            timer = threading.Timer(MAX_DELAY, self._send, args=[conn, msg, self.state])
            timer.start()
        else:
            self._send(conn, msg, self.state)

    def _send(self, conn, msg, state):
        log.info('send ... {}'.format(msg))
        conn.privmsg(CHANNEL, msg)

        if self.timeout is not None:
            log.info('Canceling timeout from _send')
            self.timeout.cancel()

        if state == INQUIRY_REPLY_1 and self.role == ROLE_FIRST:
            log.info('Creating END response')
            self.respond(conn, msg)
        if state == INQUIRY_REPLY_2 and self.role == ROLE_SECOND:
            log.info('Creating INQUIRY_2 response...')
            self.respond(conn, msg)

        # Set timers for frustrated replies
        if state == INITIAL_OUTREACH_1:
            log.info('Setting timer for secondary outreach 1')
            self.timeout = threading.Timer(FRUSTRATED_DELAY, self.secondary_outreach_1, args=[conn])
            self.timeout.start()
        elif state == SECONDARY_OUTREACH_1 or state == OUTREACH_REPLY_2\
                or state == INQUIRY_1 or state == INQUIRY_2:
            log.info('Setting timer for giving up')
            self.timeout = threading.Timer(FRUSTRATED_DELAY, self.giveup_frustrated, args=[conn])
            self.timeout.start()

    def initial_outreach_1(self, conn):
        log.info('Role: FIRST')
        self.role = ROLE_FIRST
        self._change_state(INITIAL_OUTREACH_1)
        self.send(conn, random.choice(initial_outreaches), False)

    def secondary_outreach_1(self, conn):
        self._change_state(SECONDARY_OUTREACH_1)
        self.send(conn, random.choice(second_outreaches), False)

    def inquiry_1(self, message, conn):
        self._change_state(INQUIRY_1)
        if self.role == ROLE_FIRST:
            self.send(conn, self.generate_question(message))
        else:
            self.respond(conn, message)

    def inquiry_reply_1(self, message, conn):
        self._change_state(INQUIRY_REPLY_1)
        if self.role == ROLE_FIRST:
            self.send(conn, random.choice(transitions) + self.generate_response(message))
        else:
            self.respond(conn, message)

    def outreach_reply_2(self, message, conn):
        self._change_state(OUTREACH_REPLY_2)
        if self.role == ROLE_FIRST:
            self.respond(conn, message)
        else:
            self.send(conn, random.choice(initial_outreaches))

    def inquiry_2(self, message, conn):
        self._change_state(INQUIRY_2)
        if self.role == ROLE_FIRST:
            self.respond(conn, message)
        else:
            self.send(conn, self.generate_question(message))

    def giveup_frustrated(self, conn):
        self._change_state(GIVEUP_FRUSTRATED)
        self.send(conn, 'Well, I guess not everyone wants to be an informed citizen.', False)
        self.end(conn)

    def inquiry_reply_2(self, message, conn):
        self._change_state(INQUIRY_REPLY_2)
        if self.role == ROLE_SECOND:
            self.send(conn, random.choice(transitions) + self.generate_response(message))

    def end(self, conn):
        if self.state == GIVEUP_FRUSTRATED:
            msg = random.choice(end_frustrated_messages)
        else:
            msg = random.choice(end_messages)
        self._change_state(END)
        self.send(conn, msg)

    def forget(self, conn):
        self._change_state(START)
        self.role = ROLE_FIRST
        self.voicedResponses = {}
        if self.timeout is not None:
            self.timeout.cancel()
        self.respond(conn)

    def _change_state(self, newState):
        log.info('{} -> {}'.format(self.states[self.state], self.states[newState]))
        self.state = newState


fsm = Chatbot()

def get_other_users(userList):
    return [user for user in userList if user != NICKNAME]

def on_welcome(conn, evt):
   log.info('User joined. Sending welcome message...')
   if irc.client.is_channel(CHANNEL):
      conn.join(CHANNEL)
      return
   fsm.welcome(conn)

def on_join(conn, evt):
   log.info('join ... event={}, conn={}'.format(evt, conn))
   fsm.respond(conn)

def on_namreply(conn, evt):
   log.info('users ... {}'.format(evt.arguments[2].split(' ')))

def on_pubmsg(conn, evt):
   recv(conn, evt.source.split('!')[0], evt.arguments[0])

def on_disconnect(conn, evt):
   log.info('disconnect ...')

def recv(conn, frm, msg):
   global fsm
   log.info('recv ... {}={}'.format(frm, msg))
   if msg is not None and msg.strip()[0: len(NICKNAME)+1] == '{}:'.format(NICKNAME):
      message = msg[len(NICKNAME)+1:].strip()
      log.info('cmd ... {}'.format(message))
      if message.lower() == 'die':
         conn.quit('dying')
         sys.exit('dying')
      elif message.lower() == '*forget':
         fsm.forget(conn)
         log.info('forgetting ...')
      else: # FSM
         log.info('Responding...')
         fsm.respond(conn, message, frm=frm)

def main():
    # q1 = "what will you do to help veterans in our country?"
    # q2 = "what are your plans to rebuild america and get its citizens back on their feet?"
    # q3 = "how do you plan to protect America's privacy and the American people from cyber threats?"
    # q4 = "what's your stance on health care?"
    # q5 = "do you believe in improving our infrastructure?"
    # q6 = "what's your policy on immigration?"
    # q7 = "what do you think about energy?"
    # q8 = "should marijuana be legal?"
    # q8 = "what do you mean by that?"
    # q9 = ""
    # q10 = "sdl;fjasdlkfjasl;kdfjalk;sdjfa ;lskdfj alskdfja s;dklf"
    #
    # print('\n')
    # print(q10)
    # print('\n')
    # print(fsm.generate_response(q10))
    # print(fsm.generate_response(q2))
    # print(fsm.generate_response(q3))
    # print(fsm.generate_response(q4))
    # print(fsm.generate_response(q5))

   # Switch to debug for verbose logging
   logging.basicConfig(level=logging.INFO)
   log.info('start ...')
   try:
      reactor = irc.client.Reactor()
      c = reactor.server().connect(SERVER, PORT, NICKNAME)
      c.add_global_handler('welcome', on_welcome)
      c.add_global_handler('join', on_join)
      c.add_global_handler('namreply', on_namreply)
      c.add_global_handler('pubmsg', on_pubmsg)
      c.add_global_handler('disconnect', on_disconnect)
      reactor.process_forever()
   except:
      log.info(sys.exc_info()[1])

if __name__ == '__main__':
   main()
