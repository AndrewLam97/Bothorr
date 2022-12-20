import random


def get_phrase(s):
    clown = """1.
Terry Bard
Kent Scouter/Zerk
Mike Arty
Toobles/Brian

2.
Eric Pally
Andrew GS
Matteo DB
Mike Sorc

3.
Matteo Pally
Eric SS
Andrew Sorc
Mike Scouter

4.
Mike Bard
Andrew LM
Eric Sorc
Matteo Arty

5.
Andrew Bard
Eric DB/DE
Mike SS
Matteo Destroyer

6.
Matteo Bard
Mike GS
Eric Zerk
Andrew Arty

7.
Pug Support
Terry SS
Eric Destro
Andrew DB """

    kunge = """1. Mangopoo Aithe Arcdiez Thecoolcannon
2. Thecoolguy Tinywang FeliciT Arcquattro
3. ArcZero Exa Thecoolblade Gigawang
4. PuriT Thecoolhammer Pilfmorn Arcseis
5. Thecoolmusician LucidiT Dilfporn Arcocho
6. ArcDos Stry Wangaroo Thecoolgirl"""

    phrases = [
        "smh",
        "starcraft?",
        "nah sus",
        "pain",
        "I'm gonna pity this aren't I",
        "I don't know why my character doesn't do damage",
        "I enjoy breaking Andrew's mental"
    ]
    
    if s == "clown":
        return clown
    elif s == "kunge":
        return kunge
    elif s == "matteo":
        return random.choice((phrases))
