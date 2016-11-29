# FSM functions for chatbot
# Author: Joey Wilson

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

import logging
log = logging.getLogger(__name__)

state = START

# DONE
def start(cmd):
   global state
   log.info('START {}'.format(cmd))
   if cmd == 'HELLO':
      state = OUTREACH_REPLY_2
      return 'HELLO BACK AT YOU!'
   elif '_START_' in cmd:
      state = INITIAL_OUTREACH_1
      return 'HELLO'
   return ''

# DONE
def initial_outreach_1(cmd):
   global state
   log.info('INITIAL_OUTREACH_1 {}'.format(cmd))
   if cmd == 'HELLO BACK AT YOU!':
      state = INQUIRY_1
      return 'WHAT\'S HAPPENING?'
   elif cmd == 'TIMEOUT': 
      state = SECONDARY_OUTREACH_1
      return 'EXCUSE ME, HELLO?'
   return ''

def secondary_outreach_1(cmd):
   global state
   log.info('SECONDARY_OUTREACH_1 {}'.format(cmd))
   if cmd == 'HELLO BACK AT YOU!':
      state = INQUIRY_1
      return 'WHAT\'S HAPPENING?'
   return ''

# DONE
def inquiry_1(cmd):
   global state
   log.info('INQUIRY_1 {}'.format(cmd))
   if cmd == 'AND YOURSELF?':
      state = INQUIRY_REPLY_1
      return 'I\'M FINE THANKS FOR ASKING'   
   return ''

# DONE      
def inquiry_reply_1(cmd):
   global state
   log.info('INQUIRY_REPLY_1 {}'.format(cmd))
   state = END
   return ''

# DONE
def outreach_reply_2(cmd):
   global state
   log.info('OUTREACH_REPLY_2 {}'.format(cmd))
   if cmd == 'WHAT\'S HAPPENING?':
      state = INQUIRY_REPLY_2
      return 'I\'M FINE'
   return ''

# DONE
def inquiry_2(cmd):
   global state
   log.info('INQUIRY_2 {}'.format(cmd))
   state = END
   return ''

# DONE
def giveup_frustrated(cmd):
   global state
   log.info('GIVEUP_FRUSTRATED_2 {}'.format(cmd))
   state = END
   return 'WHATEVER'

# DONE
def inquiry_reply_2(cmd):
   global state
   log.info('INQUIRY_REPLY_2 {}'.format(cmd))
   state = INQUIRY_2
   return 'AND YOURSELF?'

# DONE
def end(cmd):
   global state
   log.info('END {}'.format(cmd))
   return 'END'
