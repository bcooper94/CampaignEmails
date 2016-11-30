# Main driver for the chatbot
# Author: Joey Wilson
# Starting code from: Joel Rosdahl <joel@rosdahl.net>

# TODO
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

log = logging.getLogger(__name__)

class Chatbot:
    def __init__(self):
        self.state = START
        self.voicedResponses = {}
        self.timeout = None
        with open('responses.json') as responses:
            self.responses = json.load(responses)
            print('Retrieved responses:', [key for key in self.responses.keys()])

    def send_message(self, conn, frm, cmd):
        msg = None

        if self.timeout:
            self.timeout.cancel()

        if self.state == START:
            msg = self.start(cmd)
            self.timeout = threading.Timer(MAX_DELAY, self.no_reply, args=[conn])
            self.timeout.start()
        elif self.state == INITIAL_OUTREACH_1:
            msg = self.initial_outreach_1(cmd)
            self.timeout = threading.Timer(MAX_DELAY, self.no_reply, args=[conn])
            self.timeout.start()
        elif self.state == SECONDARY_OUTREACH_1:
            msg = self.secondary_outreach_1(cmd)
        elif self.state == GIVEUP_FRUSTRATED_1:
            msg = self.giveup_frustrated_1(cmd)
        elif self.state == INQUIRY_1:
            msg = self.inquiry_1(cmd)
        elif self.state == INQUIRY_REPLY_1:
            msg = self.inquiry_reply_1(cmd)
        elif self.state == OUTREACH_REPLY_2:
            msg = self.outreach_reply_2(cmd)
            if msg == '':
                return
            send(conn, msg)
            msg = self.inquiry_reply_2(cmd)
            self.timeout = threading.Timer(MAX_DELAY, self.no_reply, args=[conn])
            self.timeout.start()
        elif self.state == INQUIRY_2:
            msg = self.inquiry_2(cmd)
        elif self.state == GIVEUP_FRUSTRATED_2:
            msg = self.giveup_frustrated_2(cmd)
        elif self.state == INQUIRY_REPLY_2:
            msg = self.inquiry_reply_2(cmd)
        if self.state == END:
            msg = self.end(cmd)

        if msg is None:
            msg = 'Couldn\'t match a response.'

        return msg

    # DONE
    def start(self, cmd):
        log.info('START {}'.format(cmd))
        if cmd == 'HELLO':
            self.state = OUTREACH_REPLY_2
            return 'HELLO BACK AT YOU!'
        elif '_START_' in cmd:
            self.state = INITIAL_OUTREACH_1
            return 'HELLO'
        return ''

    # DONE
    def initial_outreach_1(self, cmd):
        log.info('INITIAL_OUTREACH_1 {}'.format(cmd))
        if cmd == 'HELLO BACK AT YOU!':
            self.state = INQUIRY_1
            return 'WHAT\'S HAPPENING?'
        elif cmd == 'TIMEOUT':
            self.state = SECONDARY_OUTREACH_1
            return 'EXCUSE ME, HELLO?'
        return ''

    def secondary_outreach_1(self, cmd):
        log.info('SECONDARY_OUTREACH_1 {}'.format(cmd))
        if cmd == 'HELLO BACK AT YOU!':
            self.state = INQUIRY_1
            return 'WHAT\'S HAPPENING?'
        return ''

    # DONE
    def inquiry_1(self, cmd):
        log.info('INQUIRY_1 {}'.format(cmd))
        if cmd == 'AND YOURSELF?':
            self.state = INQUIRY_REPLY_1
            return 'I\'M FINE THANKS FOR ASKING'
        return ''

    # DONE
    def inquiry_reply_1(self, cmd):
        log.info('INQUIRY_REPLY_1 {}'.format(cmd))
        self.state = END
        return ''

    # DONE
    def outreach_reply_2(self, cmd):
        log.info('OUTREACH_REPLY_2 {}'.format(cmd))
        if cmd == 'WHAT\'S HAPPENING?':
            self.state = INQUIRY_REPLY_2
            return 'I\'M FINE'
        return ''

    # DONE
    def inquiry_2(self, cmd):
        log.info('INQUIRY_2 {}'.format(cmd))
        self.state = END
        return ''

    # DONE
    def giveup_frustrated_1(self, cmd):
        log.info('GIVEUP_FRUSTRATED_1 {}'.format(cmd))
        self.state = END
        return 'Giving up 1'

    def giveup_frustrated_2(self, cmd):
        log.info('GIVEUP_FRUSTRATED_2 {}'.format(cmd))
        self.state = END
        return 'Giving up 2'

    # DONE
    def inquiry_reply_2(self, cmd):
        log.info('INQUIRY_REPLY_2 {}'.format(cmd))
        self.state = INQUIRY_2
        return 'AND YOURSELF?'

    # DONE
    def end(self, cmd):
        log.info('END {}'.format(cmd))
        return 'END'

    def no_reply(self, conn):
        if self.state == INITIAL_OUTREACH_1:
            msg = self.initial_outreach_1('TIMEOUT')
            self.timeout = threading.Timer(MAX_DELAY, self.no_reply, args=[conn])
            self.timeout.start()
        else:
            msg = self.giveup_frustrated_1(None)
        send(conn, msg)

    def forget(self):
        self.state = START
        self.voicedResponses = {}


fsm = Chatbot()

def on_welcome(conn, evt):
   if irc.client.is_channel(CHANNEL):
      conn.join(CHANNEL)
      return
   send(conn, 'space-bot welcome')

def on_join(conn, evt):
   log.info('join ...')
   send(conn, 'space-bot join')

def on_namreply(conn, evt):
   log.info('users ... {}'.format(evt.arguments[2].split(' ')))

def on_pubmsg(conn, evt):
   recv(conn, evt.source.split('!')[0], evt.arguments[0])

def on_disconnect(conn, evt):
   log.info('disconnect ...')

def send(conn, msg):
   log.info('send ... {}'.format(msg))
   conn.privmsg(CHANNEL, msg)

def recv(conn, frm, msg):
   global fsm
   log.info('recv ... {}:{}'.format(frm, msg))
   if msg[0: len(NICKNAME)+1] == '{}:'.format(NICKNAME):
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
         send(conn, fsm.send_message(conn, frm, cmd))





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
