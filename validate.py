import os, sys
sys.path.append('../')

import torch
import torch.nn as nn
from torch.autograd import Variable
from nltk.translate.bleu_score import corpus_bleu
use_gpu = torch.cuda.is_available()

from utils import AverageMeter

def validate(val_iter_pos, val_iter_neg, model, POS, NEG):
    model.eval()

    # Iterate over words in validation batch.
    bleu = AverageMeter()
    sents_out = [] # list of sentences from decoder
    sents_ref = [] # list of target sentences
    num_batches = max(len(val_iter_pos), len(val_iter_neg))
    iterval_pos = iter(val_iter_pos)
    iterval_neg = iter(val_iter_neg)
    # Try 50 sentences
    for i in range(50):

        # POS RECONSTRUCTION LOSS
        pos_batch = next(iterval_pos)
        pos_text = pos_batch.text.cuda() if use_gpu else pos_batch.text

        # Get model prediction (from beam search)
        out = model.predict(pos_text, 0, 1, beam_size=1) # list of ints (word indices) from greedy search
        ref = list(pos_text.data.squeeze())
        # Prepare sentence for bleu script
        remove_tokens = [NEG.vocab.stoi['<pad>'], NEG.vocab.stoi['<s>'], NEG.vocab.stoi['</s>']]
        out = [w for w in out if w not in remove_tokens]
        ref = [w for w in ref if w not in remove_tokens]
        sent_out = ' '.join(NEG.vocab.itos[j] for j in out)
        sent_ref = ' '.join(POS.vocab.itos[j] for j in ref)

        sents_out.append(sent_out)
        sents_ref.append(sent_ref)
    # Run moses bleu script
    bleu = corpus_bleu(sents_out, sents_ref)
    # Log information after validation
    print(bleu)
    origfile = open('original.txt', 'w')
    transfile = open('transferred.txt', 'w')
    for sentence in sents_ref:
        print(sentence, file=origfile)
    for sentence in sents_out:
        print(sentence, file=transfile)
    for i in range(10):
        print(sents_ref[i], sents_out[i])
    return(bleu)
