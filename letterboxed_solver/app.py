from flask import Flask, render_template, request
from english_words import get_english_words_set
from collections import defaultdict
import string

app = Flask(__name__)

def load_words(min_length=3):
    words = get_english_words_set(['web2'], lower=False)
    return set(word.upper() for word in words if len(word) >= min_length and word.isalpha())

def build_letter_map(letters):
    return {letter: i // 3 for i, letter in enumerate(letters)}

def valid_word(word, letter_map):
    if any(c not in letter_map for c in word):
        return False
    for a, b in zip(word, word[1:]):
        if letter_map[a] == letter_map[b]:
            return False
    return True

def build_word_dict(words, letter_map):
    valid = [word for word in words if valid_word(word, letter_map)]
    starts = defaultdict(list)
    for word in valid:
        starts[word[0]].append(word)
    return valid, starts

def uses_all_letters(words, letters):
    used = set("".join(words))
    return all(letter in used for letter in letters)

def find_solutions(valid_words, start_dict, letters):
    solutions = []
    for word1 in valid_words:
        end1 = word1[-1]
        for word2 in start_dict.get(end1, []):
            if word1 != word2:
                combo = [word1, word2]
                if uses_all_letters(combo, letters):
                    solutions.append(combo)
    return solutions

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    input_letters = ""
    if request.method == "POST":
        input_letters = request.form.get("letters", "").strip().upper()
        if len(input_letters) == 12 and all(c in string.ascii_uppercase for c in input_letters):
            flat_letters = list(input_letters)
            letter_map = build_letter_map(flat_letters)
            words = load_words()
            valid, start_dict = build_word_dict(words, letter_map)
            solutions = find_solutions(valid, start_dict, flat_letters)
            results = sorted(solutions, key=lambda x: len("".join(x)))[:10]
    return render_template("index.html", results=results, letters=input_letters)

if __name__ == "__main__":
    app.run(debug=True)