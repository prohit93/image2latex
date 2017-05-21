from collections import Counter
import numpy as np
import nltk
from utils.data_utils import reconstruct_formula


def write_answers(prediction, ground_truth, path, rev_vocab):
    """ 
    Write answers in file, the format is
        truth
        prediction
        new line
        ...
    """
    with open(path, "a") as f:
        for t, p in zip(ground_truth, prediction):
            t = [rev_vocab[idx] for idx in t]
            p = [rev_vocab[idx] for idx in p]
            f.write(" ".join(t) + "\n")
            f.write(" ".join(p) + "\n\n")


def f1_score(prediction, ground_truth):
    # prediction_tokens = prediction.split()
    # ground_truth_tokens = ground_truth.split()
    prediction_tokens = prediction[:len(ground_truth)]
    ground_truth_tokens = ground_truth

    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)

    return f1


def exact_match_score(prediction, ground_truth):
    prediction = prediction[:len(ground_truth)]
    return np.array_equal(prediction, ground_truth)


def bleu_score(prediction, ground_truth, rev_vocab):
	hypothesis = [rev_vocab[idx] for idx in ground_truth]
	reference = [rev_vocab[idx] for idx in prediction]
	BLEUscore = nltk.translate.bleu_score.sentence_bleu([reference], hypothesis)

	return BLEUscore


def evaluate(predictions, ground_truths, rev_vocab):
    f1 = exact_match = bleu = 0
    for k, pred in enumerate(predictions):
    	truth = ground_truths[k]
    	exact_match += exact_match_score(pred, truth)
    	f1 += f1_score(pred, truth)
    	bleu += bleu_score(pred, truth, rev_vocab)

    # macro average
    exact_match = 100.0 * exact_match / len(predictions)
    f1 = 100.0 * f1 / len(predictions)
    bleu = 100.0 * bleu / len(predictions)

    return f1, exact_match, bleu