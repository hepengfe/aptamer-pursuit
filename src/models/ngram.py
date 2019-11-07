# A bigram predicts the likelihood of the current element based on the previous element.
import json
import random
import numpy as np
import math
from sklearn import linear_model, metrics

# Construct a training dataset:
dataset_file = "../data/ngram_dataset.json"

with open(dataset_file, 'r') as f:
    ngram_dataset = json.load(f)

# k = k-gram value, d = number of features
k = 3
d = 200
lr = 0.01
'''
Generate and evaluate the performance of features to predict whether a protein will bind to a specific allele. 
'''
def predict_proteins():
    for allele in ngram_dataset:
        # These are protein/binding affinity pairs
        proteins = ngram_dataset[allele]

        # Divide them into train/test sets
        num_samples = len(proteins)
        if num_samples < 20:
            continue
        training_set = proteins[:int(num_samples*0.8)]
        testing_set = proteins[int(num_samples*0.8):]

        # Generate features using ngram structure
        training_peptides = [p for (p,b) in training_set]
        train_y = [np.log10(float(b)) for (p, b) in training_set]
        testing_peptides = [p for (p,b) in testing_set]
        test_y = [np.log10(float(b)) for (p, b) in testing_set]
        features = []
        for i in range(d):
            # Find a random sequence in the training set
            seq = random.choice(training_peptides)

            # Find a random subsection of k elements from this sequence
            start = random.randint(0, len(seq) - k)
            feature = seq[start:start+k]

            # Add it to the list of features here
            features.append(feature)

        # Generate train and test matrices
        train_features = np.zeros((len(training_peptides), d))
        test_features = np.zeros((len(testing_set), d))

        train_ones = 0
        for i in range(len(training_peptides)):
            sequence = training_peptides[i]
            for j in range(len(features)):
                feature = features[j]
                train_features[i, j] = 1 if str(feature) in str(sequence) else 0
                if train_features[i, j] == 1:
                    train_ones += 1

        for i in range(len(testing_peptides)):
            sequence = testing_peptides[i]
            for j in range(len(features)):
                feature = features[j]
                test_features[i, j] = 1 if feature in sequence else 0

        # Use a linear model here to calculate the best parameters for the linear regression model
        regularization_params = [0.02, 0.03, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
        lowest_train_MSE = None
        best_alpha = None
        for a in regularization_params:
            lasso_model = linear_model.Lasso(alpha=a, max_iter=100)
            lasso_model.fit(train_features, train_y)

            lasso_predict = lasso_model.predict(train_features)
            lasso_true = train_y
            mse = metrics.mean_squared_error(lasso_true, lasso_predict)
            if lowest_train_MSE is None or mse < lowest_train_MSE:
                lowest_train_MSE = mse
                best_alpha = a

        # Calculate the train MSE
        lasso_model = linear_model.Lasso(alpha=best_alpha)
        lasso_model.fit(train_features, train_y)
        lasso_predict = lasso_model.predict(test_features)
        lasso_true = test_y
        test_mse = metrics.mean_squared_error(lasso_true, lasso_predict)

        print("Allele: " + str(allele) + ", Train MSE: " + str(lowest_train_MSE) + ", Test MSE: " + str(test_mse) + ", Num Samples: " + str(num_samples))

'''
Generate statistics about the proteins that I predicted.
TODO: Understand motifs, right now it just looks at length
@param: predicted_proteins = a list of predicted proteins (for all alleles)
@param: seq_length = the length of peptide sequence to generate. 
'''
def generate_stats(predicted_proteins, seq_length):
    # Shortest Length
    shortest_length = seq_length
    longest_length = 0
    for i in range(len(predicted_proteins)):
        shortest_length = min(shortest_length, len(predicted_proteins[i]))
        longest_length = max(longest_length, len(predicted_proteins[i]))

    print("-----Stats-----")
    print("Shortest Length Peptide: ", shortest_length)
    print("Longest Length Peptide: ", longest_length)


predicted_proteins = predict_proteins()
#generate_stats(predicted_proteins, seq_length=8)





