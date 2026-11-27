# Steering NotaGen toward Strozzi without training (27 November 2026): the test, written before it was run

**Why:** on the open list, "forking NotaGen to write in one composer's manner". Fine-tuning needs a GPU with 24 GB (NotaGen's README); Philip's Mac has none. Claude offered a free way first, Composer Vector (Jiang and Xu, 2025, arXiv 2604.03333): a composer's style as one direction in NotaGen's hidden states, added while it writes, with no training. Philip, 27 November 2026: "Let's try the free option".

**What the paper does** (its text, its code at github.com/JiangXunyi/Composer-Vector read here, not run): the vector is the mean, over a composer's pieces, of the patch-level decoder's state at the piece's last patch (the last layer for NotaGen). While writing, the state of the newest patch, from which the character decoder writes the next patch, becomes h + α·v, scaled back to h's length. The paper used α from 0.1 to 0.8, and judged by a classifier of composers on 11 composers NotaGen knows, with no listening. **It did not test a composer the model was not trained on.**

**Here:** NotaGen-X; the vector taken from the same state it is added to (the decoder's last hidden state, after its final layer norm), where the paper's collector reads the last block. The composer is **Barbara Strozzi**, one of Philip's favourites and not among NotaGen's 111 prompts, chosen over Rameau because her 28 works in score-reader's catalogue are MusicXML (CPDL), which NotaGen's own converter reads; Rameau's 108 are LilyPond. The prompt for every reading and every piece written: **Baroque / Handel, George Frideric / Vocal-Orchestral**, the nearest NotaGen knows to a Venetian voice with its bass.

**The split** (`composer-vector-2026-11-27/split.json`, seed 731916304, drawn with `secrets` before any work was read): 20 of Strozzi's works make the vector, 8 are held out. The control: **Francesca Caccini's 20 works** (CPDL, the same archive), voice and continuo, Italian, of the generation before hers, none in the vector; most of both are one editor's (André Vierendeels: 19 of Strozzi's 28, 18 of Caccini's 20), so the editions' habits of notation are alike and cannot alone tell them apart.

**The test** (`study/notagen_steer.py score`, on Philip's Mac): NotaGen-X's bits per character on each held-out work, as it reads it under the prompt, with no steering and with α 0.1, 0.3 and 0.5 (every patch's state steered, as each would be when written). At **α 0.3**, the paper's middle:
1. at least 6 of the 8 held-out Strozzi works cost fewer bits than with no steering;
2. their mean saving is larger than the mean saving on Caccini's 20.

If both hold, the vector is taken to have learnt something of Strozzi and not only of Venetian song, and pieces are written with it for Philip to hear (the test that counts): the same seeds with and without the vector, named, not hidden. If either fails, it is not used, and the paid way (fine-tuning) is the one left.

**What it cannot see.** Bits per character also pay for NotaGen's spelling of the notes and its layout; 8 works are few; NotaGen may already lean toward these pieces (its 1.6 million training scores may hold some CPDL editions). A vector that lowers the bits of her own pieces may still write music that does not sound like her: only listening shows that.

**The inputs** (`composer-vector-2026-11-27/inputs.jsonl`, made here with `notagen_steer.py prepare`): each work as NotaGen reads it under the prompt, from score-reader's copy of the CPDL archive. NotaGen's converter could not read 9 of the 48 files as they are; written out again by music21 first, 6 of those were read (marked `via` in each line). Not read at all: two of the vector's (*Il silentio nocivo*, *Che si può fare* in its modernized edition) and one of Caccini's (*S'io men vò*). So the vector is made of 18 works, all 8 held out are tested, and 19 of Caccini's: the rule above is unchanged.

## Result (27 November 2026; the vector and the scores made on Philip's Mac and pushed the same day)

```
python3 study/notagen_steer.py test checks/composer-vector-2026-11-27/scores.jsonl checks/composer-vector-2026-11-27/split.json
```

The vector: 18 works (the two the converter could not read left out), length 26.69.

| | works | bits a character, no steering | saving at α 0.1 | at α 0.3 | at α 0.5 |
|---|---|---|---|---|---|
| Strozzi, the vector's own | 18 | 0.620 | +0.0020 (0.33%) | +0.0047 (0.78%) | +0.0059 (1.01%) |
| Strozzi, held out | 8 | 0.677 | +0.0021 (0.31%) | +0.0047 (0.69%) | +0.0055 (0.81%) |
| Caccini, the control | 19 | 0.951 | +0.0047 (0.49%) | +0.0126 (1.29%) | +0.0184 (1.88%) |

**It fails the second condition, and it is not used.** Every held-out work of Strozzi's is cheaper with the vector (8 of 8 at every α), but every one of Caccini's is too (19 of 19), and by more: at α 0.3, 0.0126 bits a character against 0.0047, more even as a share (1.29% against 0.69%), and more than her own 18 works that made the vector gain (0.78%). So the direction is not Strozzi's: it helps NotaGen most where it was most surprised (Caccini's editions, 0.95 bits a character against Strozzi's 0.62 to 0.68), whatever it holds of the kind of score the two share. And the savings are small, under 2% at most.

**What is left of the NotaGen fork:** fine-tuning, on a rented GPU. Against it, found here: the favourites NotaGen does not know have few scores it can read (Strozzi 28, of which 26 converted; Buxtehude 17 and Weber 17, Borodin 8; Rameau's 108 are LilyPond, Pachelbel's mostly MIDI), so a fine-tuned model would learn from a few dozen pieces at best.
