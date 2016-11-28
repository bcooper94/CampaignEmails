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

def start(cmd):
   log.info('START {}'.format(cmd))
   return INITIAL_OUTREACH_1, 's state' 

def initial_outreach_1(cmd):
   log.info('INITIAL_OUTREACH_1 {}'.format(cmd))
   return SECONDARY_OUTREACH_1, 'io1 state' 

def secondary_outreach_1(cmd):
   log.info('SECONDARY_OUTREACH_1 {}'.format(cmd))
   return GIVEUP_FRUSTRATED_1, 'so1 state'

def giveup_frustrated_1(cmd):
   log.info('GIVEUP_FRUSTRATED_1 {}'.format(cmd))
   return INQUIRY_1, 'gf1 state'

def inquiry_1(cmd):
   log.info('INQUIRY_1 {}'.format(cmd))
   return INQUIRY_REPLY_1, 'i1 state'

def inquiry_reply_1(cmd):
   log.info('INQUIRY_REPLY_1 {}'.format(cmd))
   return OUTREACH_REPLY_2, 'ir1 state'

def outreach_reply_2(cmd):
   log.info('OUTREACH_REPLY_2 {}'.format(cmd))
   return INQUIRY_2, 'or2 state'

def inquiry_2(cmd):
   log.info('INQUIRY_2 {}'.format(cmd))
   return GIVEUP_FRUSTRATED_2, 'i2 state'

def giveup_frustrated_2(cmd):
   log.info('GIVEUP_FRUSTRATED_2 {}'.format(cmd))
   return INQUIRY_REPLY_2, 'gf2 state'

def inquiry_reply_2(cmd):
   log.info('INQUIRY_REPLY_2 {}'.format(cmd))
   return END, 'ir2 state' 

def end(cmd):
   log.info('END {}'.format(cmd))
   return END, 'e state' 
