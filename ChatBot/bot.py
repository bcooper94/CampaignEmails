# Main driver for the chatbot
# Author: Joey Wilson
# Starting code from: Joel Rosdahl <joel@rosdahl.net>

# TODO
# make sure the time between utterances is between 1 and 3 second

import irc.client
import logging
import sys
import threading

import fsm

SERVER = 'irc.freenode.net'
PORT = 6667
CHANNEL = '#joeycpe582test'
NICKNAME = 'space-bot'

log = logging.getLogger(__name__)

timeout = None

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
         fsm.state = fsm.START
         log.info('forgetting ...')
      else: # FSM
         fsm_driver(conn, frm, cmd)

def no_reply(conn):
   if fsm.state == fsm.INITIAL_OUTREACH_1: 
      msg = fsm.initial_outreach_1('TIMEOUT') 
      timeout = threading.Timer(10.0, no_reply, args=[conn])
      timeout.start()
   else:
      msg = fsm.giveup_frustrated(None)
   send(conn, msg)

def fsm_driver(conn, frm, cmd):
   global timeout

   msg = None  

   if timeout:
      timeout.cancel()

   if fsm.state == fsm.START:
      msg = fsm.start(cmd)
      timeout = threading.Timer(10.0, no_reply, args=[conn])
      timeout.start()
   elif fsm.state == fsm.INITIAL_OUTREACH_1:
      msg = fsm.initial_outreach_1(cmd)
      timeout = threading.Timer(10.0, no_reply, args=[conn])
      timeout.start()
   elif fsm.state == fsm.SECONDARY_OUTREACH_1:
      msg = fsm.secondary_outreach_1(cmd)
   elif fsm.state == fsm.GIVEUP_FRUSTRATED_1:
      msg = fsm.giveup_frustrated_1(cmd)
   elif fsm.state == fsm.INQUIRY_1:
      msg = fsm.inquiry_1(cmd)
   elif fsm.state == fsm.INQUIRY_REPLY_1:
      msg = fsm.inquiry_reply_1(cmd)
   elif fsm.state == fsm.OUTREACH_REPLY_2:
      msg = fsm.outreach_reply_2(cmd)
      if msg == '':
         return
      send(conn, msg)
      msg = fsm.inquiry_reply_2(cmd)
      timeout = threading.Timer(10.0, no_reply, args=[conn])
      timeout.start()
   elif fsm.state == fsm.INQUIRY_2:
      msg = fsm.inquiry_2(cmd)
   elif fsm.state == fsm.GIVEUP_FRUSTRATED_2:
      msg = fsm.giveup_frustrated_2(cmd)
   elif fsm.state == fsm.INQUIRY_REPLY_2:
      msg = fsm.inquiry_reply_2(cmd)
   if fsm.state == fsm.END:
      msg = fsm.end(cmd)
   
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
