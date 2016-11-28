# Main driver for the chatbot
# Author: Joey Wilson
# Starting code from: Joel Rosdahl <joel@rosdahl.net>

# TODO
# make sure the time between utterances is between 1 and 3 second

import irc.client
import logging
import sys

import fsm

SERVER = 'irc.freenode.net'
PORT = 6667
CHANNEL = '#joeycpe582test'
NICKNAME = 'space-bot'

state = fsm.START # global state for fsm

log = logging.getLogger(__name__)

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
   global state
   log.info('recv ... {}:{}'.format(frm, msg))   
   if msg[0: len(NICKNAME)+1] == '{}:'.format(NICKNAME):
      cmd = msg[len(NICKNAME)+1:].upper().strip()
      log.info('cmd ... {}'.format(cmd))
      if cmd == 'DIE':
         conn.quit('dying')
         sys.exit('dying')
      elif cmd == '*FORGET':
         state = fsm.START
         log.info('forgetting ...')
      else: # FSM
         fsm_driver(conn, frm, cmd)

def fsm_driver(conn, frm, cmd):
   global state
   msg = None
   
   if state == fsm.START:
      state, msg = fsm.start(cmd)
   elif state == fsm.INITIAL_OUTREACH_1:
      state, msg = fsm.initial_outreach_1(cmd)
   elif state == fsm.SECONDARY_OUTREACH_1:
      state, msg = fsm.secondary_outreach_1(cmd)
   elif state == fsm.GIVEUP_FRUSTRATED_1:
      state, msg = fsm.giveup_frustrated_1(cmd)
   elif state == fsm.INQUIRY_1:
      state, msg = fsm.inquiry_1(cmd)
   elif state == fsm.INQUIRY_REPLY_1:
      state, msg = fsm.inquiry_reply_1(cmd)
   elif state == fsm.OUTREACH_REPLY_2:
      state, msg = fsm.outreach_reply_2(cmd)
   elif state == fsm.INQUIRY_2:
      state, msg = fsm.inquiry_2(cmd)
   elif state == fsm.GIVEUP_FRUSTRATED_2:
      state, msg = fsm.giveup_frustrated_2(cmd)
   elif state == fsm.INQUIRY_REPLY_2:
      state, msg = fsm.inquiry_reply_2(cmd)
   if state == fsm.END:
      state, msg = fsm.end(cmd)
   
   if msg:
      send(conn, msg)

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
