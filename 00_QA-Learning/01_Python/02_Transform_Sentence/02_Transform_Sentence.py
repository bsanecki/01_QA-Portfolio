# Program transforms a sentence based on alphabetical order of letters.
#
# Rules:
# -The first letter of each word stays unchanged.
# -Compare each letter with the previous letter, ignoring case.
# - If the current letter is alphabetically greater -> uppercase.
# -If it is alphabetically smaller -> lowercase.
# -If it is the same -> keep its original case.
# -Spaces remain unchanged.


def transform_sentence(sentence):
    new_sentence = []
    new_sentence.append(sentence[0])

    for count in range(1, len(sentence)):
        if sentence[count] == " ":
            new_sentence.append(" ")

        elif sentence[count - 1].lower() > sentence[count].lower():
            new_sentence.append(sentence[count].lower())

        elif sentence[count - 1].lower() < sentence[count].lower():
            new_sentence.append(sentence[count].upper())

        elif sentence[count - 1].lower() == sentence[count].lower():
            new_sentence.append(sentence[count])


    return "".join(new_sentence)


sentence = input("Enter sentence: ")

print(transform_sentence(sentence))
