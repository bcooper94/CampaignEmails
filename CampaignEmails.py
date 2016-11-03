import sys
import os
import mailbox


class CandidateMailbox:
    def __init__(self, fileName: str):
        candidateParty = extractName(fileName)
        self.party = candidateParty[0]
        self.candidate = candidateParty[1]
        self._mailbox = mailbox.mbox(fileName)
        self.messages = [Message(message) for message in self._mailbox]

    def __str__(self):
        return '<CandidateMailbox candidate={}, party={}'.format(self.candidate, self.party)


class Message:
    def __init__(self, message: mailbox.mboxMessage):
        self.body = message.get_payload()
        self._mboxMessage = message
        self.headers = {}

        for header, value in message.items():
            self.headers[header] = value


def extractName(fileName: str):
    if '/' in fileName:
        names = fileName.split('/')[-1]
    else:
        names = fileName
    names = names.split('-')
    return names[0], names[1].split('.mbox')[0]


def extractMboxes(targetDir: str):
    return [CandidateMailbox('{}/{}'.format(path, file))
            for (path, dirs, allFiles)
            in os.walk(targetDir) for file in allFiles if
            file.endswith('.mbox')]


def main():
    if len(sys.argv) > 1:
        mboxes = extractMboxes(sys.argv[1])
    else:
        mboxes = extractMboxes('Takeout/Mail/')
    for mbox in mboxes:
        print(mbox)


if __name__ == '__main__':
    main()
