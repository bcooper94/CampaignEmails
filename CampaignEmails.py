import sys
import os
import mailbox


def extractName(fileName: str):
    names = fileName.split('-')
    return names[0], names[1].split('.mbox')[0]


def extractMboxes(targetDir: str):
    return [(extractName(file), mailbox.mbox('{}/{}'.format(path, file)))
            for (path, dirs, allFiles)
            in os.walk(targetDir) for file in allFiles if
            file.endswith('.mbox')]


def main():
    if len(sys.argv) > 1:
        mboxes = extractMboxes(sys.argv[1])
    else:
        mboxes = extractMboxes('Takeout/Mail/')
    print(mboxes)
    # All headers:
    print(mboxes[0][1][0].items())
    # Message body:
    print(str(mboxes[0][1][0].get_payload()[0]))


if __name__ == '__main__':
    main()
