import re
import yaml
import sys
import os
import cmudict

cd = cmudict.dict()

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)


def lookup_word(word):
    return cd.get(word)

def sylcoOneWord(word):
    count = 0
    phones = lookup_word(word) # this returns a list of matching phonetic rep's
    if phones:                   # if the list isn't empty (the word was found)
        phones0 = phones[0]      #     process the first
        count = len([p for p in phones0 if p[-1].isdigit()]) # count the vowels
    return count

def sylco(words):
    res = sum([sylcoOneWord(re.sub(r'[^\w\s]', '', w).lower()) for w in words.split()])
    print(words, ":", res)
    return res



def popNumSyl(syl, words):
    res = []
    while syl > 0 and len(words) > 0:
        word = words.pop()
        res.append(word)
        syl -= sylco(word)

    return (syl == 0, res, words)

class HaikuDetector:
    async def checkForHaiku(self, message):
        text = message.content
        words = text.split()[::-1]
        poem = []
        if sylco(text) == 17:
            print("Might be a haiku")
            lines = [5, 7, 5]
            for syl in lines:
                res = popNumSyl(syl, words)
                words = res[2].copy()
                poem.append(res)
            print([i[1] for i in poem])
            if all([i[0] for i in poem]):
                res = "You're a poet!\n\n"
                for line in [i[1] for i in poem]:
                    res += "*" + " ".join(line) + "*\n"
                res += "\n -" + message.author.mention
                await message.reply(res)