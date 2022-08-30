import pickle
import nltk
import numpy as np
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
import re
import collections


lemmatizer = WordNetLemmatizer()
lemmatizer.lemmatize('test')
#from transformers import  GPT2Tokenizer, GPT2LMHeadModel, pipeline, BertTokenizer, BertLMHeadModel

def get_pos_tags(tokens):
    tags = None
    try:
        tags = nltk.pos_tag(tokens)
    except LookupError:
        nltk.download('average_perceptron_tagger')
        tags = nltk.pos_tag(tokens)
    return tags

def get_feminine(words):
    tags = get_pos_tags(words)
    result = []
    for word, tag in tags:
        if tag == 'PRP' and word.lower() == 'him':
            new_word = 'Her' if word[0].isupper() else 'her'
        elif tag == 'PRP' and word.lower() == 'himself' or word.lower() == 'hisself':
            new_word = 'Herself' if word[0].isupper() else 'herself'
        elif tag == 'PRP' and word.lower() == 'he':                          
            new_word = 'She' if word[0].isupper() else 'she'
        elif tag == 'PRP$' and word.lower() == 'his':
            new_word = 'Her' if word[0].isupper() else 'her'
        elif tag == 'PRP' and word.lower() == 'him.':
            new_word = 'Her.' if word[0].isupper() else 'her.'
        elif tag == 'PRP' and word.lower() == 'himself.' or word.lower() == 'hisself.':
            new_word = 'Herself.' if word[0].isupper() else 'herself.'
        elif tag == 'PRP' and word.lower() == 'he.':                          
            new_word = 'She.' if word[0].isupper() else 'she.'
        elif tag == 'PRP$' and word.lower() == 'his.':
            new_word = 'Her.' if word[0].isupper() else 'her.'
        else:
            new_word = word
        result.append(new_word)
    return result

def get_masculine(words):
    tags = get_pos_tags(words)
    result = []
    for word, tag in tags:
        if tag == 'PRP' and word.lower() == 'her':
            new_word = 'Him' if word[0].isupper() else 'him'
        elif tag == 'PRP' and word.lower() == 'herself':
            new_word = 'Himself' if word[0].isupper() else 'himself'
        elif tag == 'PRP' and word.lower() == 'she':                          
            new_word = 'He' if word[0].isupper() else 'he'
        elif tag == 'PRP$' and word.lower() == 'hers':
            new_word = 'His' if word[0].isupper() else 'his'
        elif tag == 'PRP$' and word.lower() == 'her':
            new_word = 'His' if word[0].isupper() else 'his'
        elif tag == 'PRP' and word.lower() == 'her.':
            new_word = 'Him.' if word[0].isupper() else 'him.'
        elif tag == 'PRP' and word.lower() == 'herself.':
            new_word = 'Himself.' if word[0].isupper() else 'himself.'
        elif tag == 'PRP' and word.lower() == 'she':                          
            new_word = 'He.' if word[0].isupper() else 'he.'
        elif tag == 'PRP$' and word.lower() == 'hers':
            new_word = 'His.' if word[0].isupper() else 'his.'
        else:
            new_word = word
        result.append(new_word)
    return result

def syllables_in_verse(verse):
    syllables = 0
    tokens = verse.split()
    for word in tokens:
        syllables += count_syllables(word)
    return syllables

    """def check_end_of_sentence(input_text, length_input_text, model, tokenizer):
    if len(tokenizer(input_text)['input_ids']) != length_input_text:
        return False
    inputs = tokenizer.encode("There was " + input_text, return_tensors = 'pt')
    outputs = model.generate(inputs, pad_token_id=tokenizer.eos_token_id, max_length = length_input_text+3, do_sample = True, num_return_sequences = 10)
    for output in outputs:
        text = tokenizer.decode(output, skip_special_tokens = True)
        words = text.split()
        if words[-1][-1] == '.':
            return True
    return False"""

def check_end_of_sentence(text, model):
    result = model("There was " + text,
        max_new_tokens=1,
        pad_token_id = 50256,
        num_return_sequences=10)
    result = [r['generated_text'].split() for r in result]
    last_words = list(set([r[-1] for r in result]))
    if any(lw[-1] == '.' for lw in last_words):
        return True
    return False

def load_model(filename):
    """ 
    Utility function to load ngram
    """
    with open(filename, 'rb') as target:
        model = pickle.load(target)
    return model
    
"""def get_three_highest(text, model, tokenizer, exceptions = []):
    exceptions.extend(['wasn','couldn','hadn','wouldn','weren','shouldn','haven','hasn','isn','aren','didn'])
    inpts = tokenizer("There was " + text, return_tensors="pt")

    with torch.no_grad():
        logits = model(**inpts).logits[:, -1, :]

    resulting_words = []
    n = 3
    while len(resulting_words) < 3:
        values,indices = torch.topk(logits, n)
        results = tokenizer.decode(indices.tolist()[0])
        words = [w for w in results.split() if w.isalpha() and w not in exceptions and w not in resulting_words]
        resulting_words.extend(words)
        n += 1
    return resulting_words"""

def get_three_highest(text, model, exceptions = []):
    if exceptions:
        exceptions = model.tokenizer(exceptions).input_ids
        exceptions.extend([[2492], [3521], [8020], [3636], [6304], [6584], [4398], [5818], [2125], [3588], [1422]])
    else:
        exceptions = [[2492], [3521], [8020], [3636], [6304], [6584], [4398], [5818], [2125], [3588], [1422]]
    result = model("There was " + text,
        max_new_tokens=1,
        pad_token_id = 50256,
        num_return_sequences=5,
        repetition_penalty = 1.5,
        bad_words_ids = exceptions)
    result = [r['generated_text'].split() for r in result]
    last_words = list(set([r[-1] for r in result if r[-1].isalpha()]))
    return last_words[:3]


def return_verses(limerick):
    remaining = limerick[3:].copy()
    verse2 = []; verse3 = []; verse4 = []
    v2 = ''; v3 = ''; v4 = ''; v5 = ''
    for i, word in enumerate(remaining):
        if word[-1] == '.':
            verse2.append(word[:-1])
        else:
            verse2.append(word)
        if syllables_in_verse(' '.join(verse2)) == 9:
            v2 = ' '.join(verse2)+"."
            remaining = remaining[i+1:].copy()
            break
    for i, word in enumerate(remaining):
        verse3.append(word)
        if syllables_in_verse(' '.join(verse3)) == 6:
            v3 = ' '.join(verse3)
            remaining = remaining[i+1:].copy()
            break
    for i, word in enumerate(remaining):
        if word[-1] == ',':
            verse4.append(word[:-1])
        else:
            verse4.append(word)
        if syllables_in_verse(' '.join(verse4)) == 6:
            v4 = ' '.join(verse4)+','
            v5 = ' '.join(remaining[i+1:])+"."
            break
    return [v2,v3,v4,v5]

def get_ten_highest_verbs(text, model, exceptions = []):
    if exceptions:
        exceptions = model.tokenizer(exceptions).input_ids
        exceptions.extend([[2492], [3521], [8020], [3636], [6304], [6584], [4398], [5818], [2125], [3588], [1422]])
    else:
        exceptions = [[2492], [3521], [8020], [3636], [6304], [6584], [4398], [5818], [2125], [3588], [1422]]

    past_verbs = []
    result = model("There was " + text,
        max_new_tokens=1,
        pad_token_id = 50256,
        num_return_sequences=30,
        temperature = 1.6,
        repetition_penalty = 1.5,
        bad_words_ids = exceptions,
        top_k = 50)
    result = [r['generated_text'] for r in result]
    result = [r.split() for r in list(set(result))]
    for res in result:
        tags = get_pos_tags(res)
        last_word_tag = tags[-1][1]
        if last_word_tag == 'VBD' and res[-1] not in past_verbs:
                past_verbs.append(res[-1])
    return past_verbs[:10]

"""def get_ten_highest_verbs_old(text, model, tokenizer, exceptions = []):
    exceptions.extend(['wasn','couldn','hadn','wouldn','weren','shouldn','haven','hasn','isn','aren','didn'])
    tokens = text.split()
    inpts = tokenizer("There was " + text, return_tensors="pt")

    with torch.no_grad():
        logits = model(**inpts).logits[:, -1, :]

    resulting_words = []
    n = 10
    while len(resulting_words) < 10:
        values,indices = torch.topk(logits, n)
        results = tokenizer.decode(indices.tolist()[0])
        words = [w for w in results.split() if w.isalpha() and w not in exceptions and w not in resulting_words]
        past_verbs = []
        for w in words:
            tags = get_pos_tags(tokens+[w])
            tag = tags[-1][1]
            if tag == 'VBD':
                past_verbs.append(w)
        resulting_words.extend(past_verbs)
        n += 1
    return resulting_words"""

def score_individual(model, tokens_tensor):#perplexity
    loss=model(tokens_tensor, labels=tokens_tensor)[0]
    return np.exp(loss.cpu().detach().numpy())

def get_scores(texts, model, tokenizer):
    lemmatizer = WordNetLemmatizer()
    result = []
    scored_texts = []
    for text in texts:
        tokens_tensor = tokenizer.encode(text, add_special_tokens=False, return_tensors="pt")           
        scored_texts.append((text, score_individual(model, tokens_tensor)))
    for (text,score) in scored_texts:
        lemmas = []
        tokens = []
        for w in text.split():
            if w.isalpha():
                tokens.append(w)
            else:
                tokens.append(w[:-1])
        tags = get_pos_tags(tokens)
        interesting_words = [t[0] for t in tags if t[1][0] in ['N','V','A']]
        for iw in interesting_words:
            lemmas.append(lemmatizer.lemmatize(iw))
        lemma_counter=collections.Counter(lemmas)
        if any(value >  1 for value in lemma_counter.values()):
            score *= 1.25
        result.append((text, score))
    return result

    
def get_masked_word(text, unmasker):
    masked_words = []
    result = unmasker("There was " + text,top_k=5)
    masked_words = [r["token_str"] for r in result]
    return masked_words

def count_syllables(word):
    word = word.lower()

    # exception_add are words that need extra syllables
    # exception_del are words that need less syllables

    exception_add = ['serious','crucial']
    exception_del = ['fortunately','unfortunately']

    co_one = ['cool','coach','coat','coal','count','coin','coarse','coup','coif','cook','coign','coiffe','coof','court']
    co_two = ['coapt','coed','coinci']

    pre_one = ['preach']

    syls = 0 #added syllable number
    disc = 0 #discarded syllable number

    #1) if letters < 3 : return 1
    if len(word) <= 3 :
        syls = 1
        return syls

    #2) if doesn't end with "ted" or "tes" or "ses" or "ied" or "ies", discard "es" and "ed" at the end.
    # if it has only 1 vowel or 1 set of consecutive vowels, discard. (like "speed", "fled" etc.)

    if word[-2:] == "es" or word[-2:] == "ed" :
        doubleAndtripple_1 = len(re.findall(r'[eaoui][eaoui]',word))
        if doubleAndtripple_1 > 1 or len(re.findall(r'[eaoui][^eaoui]',word)) > 1 :
            if word[-3:] == "ted" or word[-3:] == "tes" or word[-3:] == "ses" or word[-3:] == "ied" or word[-3:] == "ies" :
                pass
            else :
                disc+=1

    #3) discard trailing "e", except where ending is "le"  

    le_except = ['whole','mobile','pole','male','female','hale','pale','tale','sale','aisle','whale','while']

    if word[-1:] == "e" :
        if word[-2:] == "le" and word not in le_except :
            pass

        else :
            disc+=1

    #4) check if consecutive vowels exists, triplets or pairs, count them as one.

    doubleAndtripple = len(re.findall(r'[eaoui][eaoui]',word))
    tripple = len(re.findall(r'[eaoui][eaoui][eaoui]',word))
    disc+=doubleAndtripple + tripple

    #5) count remaining vowels in word.
    numVowels = len(re.findall(r'[eaoui]',word))

    #6) add one if starts with "mc"
    if word[:2] == "mc" :
        syls+=1

    #7) add one if ends with "y" but is not surrouned by vowel
    if word[-1:] == "y" and word[-2] not in "aeoui" :
        syls +=1
    #8) add one if "y" is surrounded by non-vowels and is not in the last word.

    for i,j in enumerate(word) :
        if j == "y" :
            if (i != 0) and (i != len(word)-1) :
                if word[i-1] not in "aeoui" and word[i+1] not in "aeoui" :
                    syls+=1
    #9) if starts with "tri-" or "bi-" and is followed by a vowel, add one.

    if word[:3] == "tri" and word[3] in "aeoui" :
        syls+=1

    if word[:2] == "bi" and word[2] in "aeoui" :
        syls+=1
    #10) if ends with "-ian", should be counted as two syllables, except for "-tian" and "-cian"

    if word[-3:] == "ian" : 
    #and (word[-4:] != "cian" or word[-4:] != "tian") :
        if word[-4:] == "cian" or word[-4:] == "tian" :
            pass
        else :
            syls+=1

    #11) if starts with "co-" and is followed by a vowel, check if exists in the double syllable dictionary, if not, check if in single dictionary and act accordingly.

    if word[:2] == "co" and word[2] in 'eaoui' and not word in ['could']:

        if word[:4] in co_two or word[:5] in co_two or word[:6] in co_two :
            syls+=1
        elif word[:4] in co_one or word[:5] in co_one or word[:6] in co_one :
            pass
        else :
            syls+=1

    #12) if starts with "pre-" and is followed by a vowel, check if exists in the double syllable dictionary, if not, check if in single dictionary and act accordingly.

    if word[:3] == "pre" and word[3] in 'eaoui' :
        if word[:6] in pre_one :
            pass
        else :
            syls+=1

    #13) check for "-n't" and cross match with dictionary to add syllable.

    negative = ["doesn't", "isn't", "shouldn't", "couldn't","wouldn't"]

    if word[-3:] == "n't" :
        if word in negative :
            syls+=1
        else :
            pass   
    #14) Handling the exceptional words.

    if word in exception_del :
        disc+=1

    if word in exception_add :
        syls+=1     

    # calculate the output
    return numVowels - disc + syls


def create_dictionary():
    embeddings_dict = {}
    with open("limerines/my_data/glove.6B.50d.txt", 'r') as f:
        for line in f:
            values = line.split()
            word = values[0]
            vector = np.asarray(values[1:], "float32")
            embeddings_dict[word] = vector
    return embeddings_dict

