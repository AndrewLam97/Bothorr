import random


def get_phrase(s):
    clown = """1.
Terry Bard
Toobles/Brian
Kent Scouter
Eric SS

2.
Matteo Bard
Andrew DB
Mike Scouter
Eric Sorc

3.
Mike Bard
Eric DB
Andrew GS
Matteo Arty

4.
Andrew Bard
Eric Zerk
Mike Arty
Matteo Sorc

5.
Eric Pally
Matteo Destro
Mike GS
Andrew Arty

6.
Matteo Pally
Andrew LM
Terry Sorc
Mike SS

7.
Pug Support
Eric Destro
Mike Sorc
Terry SS"""

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
