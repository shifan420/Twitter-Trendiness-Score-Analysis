with open("tweets.txt", "r") as file:
    lines = file.read().splitlines()
    unique_word = set()
    for line in lines:
        unique_word |= set(line.split())
    print(f"Unique words: {len(unique_word)-len(lines)}")
