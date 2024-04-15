def levenshtein_distance(str1: str, str2: str):
    n_m = len(str1) + 1
    dp = [[0 for _ in range(n_m)] for _ in range(len(str2) + 1)]
    for i in range(1, len(str2) + 1):
        dp[i][0] = i
    for j in range(1, n_m):
        dp[0][j] = j
    for i in range(1, len(str2) + 1):
        for j in range(1, n_m):
            if str1[j - 1] == str2[i - 1]:
                cost = 0
            else:
                cost = 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return dp[len(str2)][n_m - 1]


def compare_plates(num1: str, num2: str, threshold: int = 0.7):
    similarity = 1 - (levenshtein_distance(num1, num2) / max(len(num1), len(num2)))
    result_trust = similarity >= threshold
    if not result_trust:
        print("Low lever of similarity")
    return result_trust, similarity


if __name__ == "__main__":
    pairs = [
        ("ZNF2656", "INF2656"),
        ("NF2656", "INF2656"),
        ("ZNF2656", "INF265"),
        ("ZNF2656", "NF265"),
        ("ZNF2656", "ZNF2656"),
        ("ZNF2656", "2656"),
    ]

    for string1, string2 in pairs:
        result, sim = compare_plates(string1, string2)
        print(f"Similarity between '{string1}' and '{string2}': {sim:.2f}", result)
