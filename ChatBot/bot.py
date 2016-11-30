# Main driver for the chatbot
# Author: Joey Wilson
# Starting code from: Joel Rosdahl <joel@rosdahl.net>

# make sure the time between utterances is between 1 and 3 second

import irc.client
import logging
import sys
import json
import threading

SERVER = 'irc.freenode.net'
PORT = 6667
CHANNEL = '#joeycpe582test'
NICKNAME = 'space-bot'

START = 0
INITIAL_OUTREACH_1 = 1
SECONDARY_OUTREACH_1 = 2
GIVEUP_FRUSTRATED_1 = 3
INQUIRY_1 = 4
INQUIRY_REPLY_1 = 5
OUTREACH_REPLY_2 = 6
INQUIRY_2 = 7
GIVEUP_FRUSTRATED_2 = 8
INQUIRY_REPLY_2 = 9
END = 10

MAX_DELAY = 10.0
FRUSTRATED_DELAY = 10.0

log = logging.getLogger(__name__)

class Chatbot:
    def __init__(self):
        self.state = START
        self.voicedResponses = {}
        self.timeout = None
        self.states = {}
        self.states[START] = 'START'
        self.states[INITIAL_OUTREACH_1] = 'INITIAL_OUTREACH_1'
        self.states[SECONDARY_OUTREACH_1] = 'SECONDARY_OUTREACH_1'
        self.states[GIVEUP_FRUSTRATED_1] = 'GIVEUP_FRUSTRATED_1'
        self.states[INQUIRY_1] = 'INQUIRY_1'
        self.states[INQUIRY_REPLY_1] = 'INQUIRY_REPLY_1'
        self.states[OUTREACH_REPLY_2] = 'OUTREACH_REPLY_2'
        self.states[INQUIRY_2] = 'INQUIRY_2'
        self.states[GIVEUP_FRUSTRATED_2] = 'GIVEUP_FRUSTRATED_2'
        self.states[INQUIRY_REPLY_2] = 'INQUIRY_REPLY_2'
        self.states[END] = 'END'
        with open('responses.json') as responses:
            self.responses = json.load(responses)
            print('Retrieved responses:', [key for key in self.responses.keys()])

    def respond(self, conn, cmd=None, frm=None):
        if self.timeout:
            log.info('Canceling timeout')
            self.timeout.cancel()

        if self.state == START:
            self.initial_outreach_1(conn)
        elif self.state == INITIAL_OUTREACH_1:
            self.outreach_reply_2(cmd, conn)
        elif self.state == SECONDARY_OUTREACH_1:
            self.outreach_reply_2(cmd, conn)
        # elif self.state == GIVEUP_FRUSTRATED_1:
        #     self.giveup_frustrated_1(conn)
        elif self.state == INQUIRY_1:
            self.inquiry_reply_2(cmd, conn)
        elif self.state == INQUIRY_REPLY_1:
            self.end(conn)
        elif self.state == OUTREACH_REPLY_2:
            self.inquiry_1(cmd, conn)
            # if msg == '':
            #     return
            # self.send(conn, msg)
            # msg = self.inquiry_reply_2(cmd)
            # self.timeout = threading.Timer(FRUSTRATED_DELAY, self.no_reply, args=[conn])
            # self.timeout.start()
        elif self.state == INQUIRY_2:
            self.inquiry_reply_1(cmd, conn)
        # elif self.state == GIVEUP_FRUSTRATED_2:
        #     self.giveup_frustrated_2(cmd, conn)
        elif self.state == INQUIRY_REPLY_2:
            self.inquiry_2(cmd, conn)
        # if self.state == END:
        #     self.end(conn)

    def welcome(self, conn):
        self.send(conn, 'Ah, another potential voter. Hello.')

    def send(self, conn, msg, delay=True):
        if delay:
            timer = threading.Timer(MAX_DELAY, self._send, args=[conn, msg])
            timer.start()
        else:
            self._send(conn, msg)

    def _send(self, conn, msg):
        log.info('send ... {}'.format(msg))
        conn.privmsg(CHANNEL, msg)

        if self.timeout is not None:
            log.info('Canceling timeout from _send')
            self.timeout.cancel()

        # Set timers for frustrated replies
        if self.state == INITIAL_OUTREACH_1:
            log.info('Setting timer for secondary outreach 1')
            self.timeout = threading.Timer(FRUSTRATED_DELAY, self.secondary_outreach_1, args=[conn])
            self.timeout.start()
        elif self.state == SECONDARY_OUTREACH_1 or self.state == OUTREACH_REPLY_2\
                or self.state == INQUIRY_1 or self.state == INQUIRY_2:
            log.info('Setting timer for giving up')
            self.timeout = threading.Timer(FRUSTRATED_DELAY, self.giveup_frustrated_1, args=[conn])
            self.timeout.start()

    # DONE
    def initial_outreach_1(self, conn):
        self._change_state(INITIAL_OUTREACH_1)
        self.send(conn, 'Hello. I\'m {}, the next president of the United States.'.format(NICKNAME))

    def secondary_outreach_1(self, conn):
        log.info('Conn:' + str(conn))
        self._change_state(SECONDARY_OUTREACH_1)
        self.send(conn, 'Excuse me? Don\'t you want to help make America great again?', False)

    # DONE
    def inquiry_1(self, message, conn):
        self._change_state(INQUIRY_1)
        # TODO: Generate INQUIRY_1
        self.send(conn, 'Generating INQUIRY_1...')

    # DONE
    def inquiry_reply_1(self, message, conn):
        self._change_state(INQUIRY_REPLY_1)
        # TODO: Generate INQUIRY_REPLY_1 message
        self.send(conn, 'Generating INQUIRY_REPLY_1')
        self.respond(conn)

    # DONE
    def outreach_reply_2(self, message, conn):
        # if cmd == 'WHAT\'S HAPPENING?':
        self._change_state(OUTREACH_REPLY_2)
        # TODO: Generate INQUIRY_1 response
        self.send(conn, 'Generating OUTREACH_REPLY_2')
        # return 'I\'M FINE'

    # DONE
    def inquiry_2(self, cmd, conn):
        self._change_state(INQUIRY_2)
        # TODO: Generate INQUIRY_2
        self.send(conn, 'Generating INQUIRY_2')

    # DONE
    def giveup_frustrated_1(self, conn):
        self._change_state(GIVEUP_FRUSTRATED_1)
        self.send(conn, 'Well, I guess not everyone wants to be an informed citizen.', False)
        self.end(conn)

    def giveup_frustrated_2(self, message, conn):
        log.info('GIVEUP_FRUSTRATED_2 {}'.format(message))
        self._change_state(GIVEUP_FRUSTRATED_2)
        self.send(conn, 'I don\'t have time for this.', False)

    # DONE
    def inquiry_reply_2(self, message, conn):
        log.info('INQUIRY_REPLY_2 {}'.format(message))
        self._change_state(INQUIRY_REPLY_2)
        # TODO: Generate INQUIRY_REPLY_2
        self.send(conn, 'Generating INQUIRY_REPLY_2')
        self.respond(conn)

    # DONE
    def end(self, conn):
        self._change_state(END)
        # self.send(conn, 'I\'m glad we had the chance to meet, however I\'m a busy man, so I regret I must go. Goodbye, fellow Americans.')
        self.send(conn, 'Goodbye.')

    # def no_reply(self, conn):
    #     log.info('Sending no reply message')
    #     if self.state == INITIAL_OUTREACH_1:
    #         msg = self.initial_outreach_1('TIMEOUT')
    #         self.timeout = threading.Timer(MAX_DELAY, self.no_reply, args=[conn])
    #         self.timeout.start()
    #     else:
    #         msg = self.giveup_frustrated_1(None)
    #     self.send(conn, msg, False)

    def forget(self):
        self.state = START
        self.voicedResponses = {}

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
      cmd = msg[len(NICKNAME)+1:].upper().strip()
      log.info('cmd ... {}'.format(cmd))
      if cmd == 'DIE':
         conn.quit('dying')
         sys.exit('dying')
      elif cmd == '*FORGET':
         # fsm.state = fsm.START
         fsm.forget()
         log.info('forgetting ...')
      else: # FSM
         log.info('Responding...')
         fsm.respond(conn, cmd, frm=frm)

def main():
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
