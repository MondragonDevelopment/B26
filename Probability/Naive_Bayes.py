def naiveBayesBernoulli(X, Y, x):
    # Paso 1: Calculamos las probabilidades previas
    clases = set(Y)               # Deals with any number of classes
    prev = {_: 0 for _ in clases}               # These are the priors
    carac = [{c: 0 for c in clases} for _ in X]  # Conditional
                                                 # probabilities for
                                                 # each characteristic
    ocurr = len(Y)                               # Number of rows in
                                                 # training data

    for i in range(ocurr):
        prev[Y[i]] += 1         # Counting each ocurrence for that class
        for j in range(len(carac)):  
            if X[j][i] == x[j]:
                carac[j][Y[i]] += 1  # Count the ocurrences both Y[i]
                                     # and x[i] happened simultaneously

    # ---------- Step 2 ----------
    # Naive Bayes Bernoulli
    for car in carac:
        for clase in clases:
            car[clase] = (car[clase] + 1)/(prev[clase] + 2)

    # ---------- Step 1 ----------
    # We compute the actual priors here because we needed the counting
    # for step 2 first
    for clase in prev:
        prev[clase] = prev[clase]/ocurr

    pred = prev.copy()

    # ---------- Step 3 ----------
    for clase in pred:
        for car in carac:
            pred[clase] *= car[clase]

    # We normalize
    factor = sum(pred.values())
    for clase in pred:
        pred[clase] = pred[clase]/factor

    return (max(pred, key=pred.get), max(pred.values()))


if __name__ == "__main__":
    X_1 = [1, 0, 1, 0, 1]
    X_2 = [1, 1, 0, 0, 1]
    X = [X_1, X_2]  # np.column_stack((X_1, X_2))
    Y = [0, 1, 0, 1, 1]
    cond = [1, 1]

    pred = naiveBayesBernoulli(X, Y, cond)
    print(f"Given the conditions {cond}, the prediction is {pred[0]}, with a {pred[1]*100}% of confidence.")
