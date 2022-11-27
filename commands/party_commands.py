import random


def get_phrase(s):
    clown = """1.
Andrew Bard
Terry SS
Kent Zerk
Eric Sorc

2.
Matteo Bard
Andrew DB
Mike GS
Toobles WD

3.
Mike Bard
Eric DB
Andrew GS
Matteo Arty

4.
Terry Bard
Eric Zerk
Mike Arty
Matteo Sorc

5.
Eric Pally
Matteo Destro
Mike Scouter
Andrew Arty

6.
Matteo Pally
Andrew LM
Eric SS
Mike Sorc

7.
Pug Support
Eric Destro
Mike SS
Terry Sorc"""

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