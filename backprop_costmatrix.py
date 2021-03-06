# This code has been modified to accommadate the misclassification cost matrix, which will be used to train the neural network
# Original Source of this code was from the link https://machinelearningmastery.com/implement-backpropagation-algorithm-scratch-python/
# The updated code is used as part of a homework assignment.
# Course : CIS 731 Artificial Neural Networks
# Backprop on the Seeds Dataset
from random import seed
from random import randrange
from random import random
from csv import reader
import csv
import math
import numpy as np
from math import exp

# Load a CSV file
def load_csv(filename):
	dataset = list()
	with open(filename, 'r') as file:
		csv_reader = reader(file)
		for row in csv_reader:
			if not row:
				continue
			dataset.append(row)
	return dataset
# Convert string column to float
def str_column_to_float(dataset, column):
	for row in dataset:
		row[column] = float(row[column].strip())
# Convert string column to integer
def str_column_to_int(dataset, column):
	class_values = [row[column] for row in dataset]
	unique = set(class_values)
	lookup = dict()
	for i, value in enumerate(unique):
		lookup[value] = i
	for row in dataset:
		row[column] = lookup[row[column]]
	return lookup
# Find the min and max values for each column
def dataset_minmax(dataset):
	minmax = list()
	stats = [[min(column), max(column)] for column in zip(*dataset)]
	return stats
# Rescale dataset columns to the range 0-1
def normalize_dataset(dataset, minmax):
	for row in dataset:
		for i in range(len(row)-1):
			row[i] = (row[i] - minmax[i][0]) / (minmax[i][1] - minmax[i][0])
# Split a dataset into k folds
def cross_validation_split(dataset, n_folds):
	dataset_split = list()
	dataset_copy = list(dataset)
	fold_size = int(len(dataset) / n_folds)
	for i in range(n_folds):
		fold = list()
		while len(fold) < fold_size:
			index = randrange(len(dataset_copy))
			fold.append(dataset_copy.pop(index))
		dataset_split.append(fold)
	return dataset_split
# Calculate accuracy percentage
def accuracy_metric(actual, predicted):
	correct = 0
	for i in range(len(actual)):
		if actual[i] == predicted[i]:
			correct += 1
		else:
			global actual_misclassification_count
			actual_misclassification_count = actual_misclassification_count + 1
	return correct / float(len(actual)) * 100.0

# Evaluate an algorithm using a cross validation split
def evaluate_algorithm(dataset, algorithm, n_folds, *args):
	folds = cross_validation_split(dataset, n_folds)
	scores = list()
	for fold in folds:
		train_set = list(folds)
		train_set.remove(fold)
		train_set = sum(train_set, [])
		test_set = list()
		for row in fold:
			row_copy = list(row)
			test_set.append(row_copy)
			row_copy[-1] = None
		actual = [row[-1] for row in fold]
		predicted = algorithm(train_set, test_set, *args)
		actual = [row[-1] for row in fold]
		accuracy = accuracy_metric(actual, predicted)
		scores.append(accuracy)
	return scores

# Calculate neuron activation for an input
def activate(weights, inputs):
	activation = weights[-1]
	for i in range(len(weights)-1):
		activation += weights[i] * inputs[i]
	return activation
# Transfer neuron activation
def transfer(activation):
	return 1.0 / (1.0 + exp(-activation))
# Forward propagate input to a network output
def forward_propagate(network, row):
	inputs = row
	for layer in network:
		new_inputs = []
		for neuron in layer:
			activation = activate(neuron['weights'], inputs)
			neuron['output'] = transfer(activation)
			new_inputs.append(neuron['output'])
		inputs = new_inputs
	return inputs
# Calculate the derivative of an neuron output
def transfer_derivative(output):
	return output * (1.0 - output)
# Backpropagate error and store in neurons
def backward_propagate_error(network, expected, res):
	count_error=0
	for i in reversed(range(len(network))):
		layer = network[i]
		errors = list()
		if i != len(network)-1:
			for j in range(len(layer)):
				error = 0.0
				for neuron in network[i + 1]:
					error += (neuron['weights'][j] * neuron['delta'])
				errors.append(error)
		else:
			for j in range(len(layer)):
				neuron = layer[j]
				if expected[j] == res:
					errors.append((expected[j] - neuron['output']))
				else:
					global cost_matrix
					cost_matrix[expected[j]][res] = cost_matrix[expected[j]][res] + 1
					global misclassification_cost
					misclassification_cost = misclassification_cost + (cost[expected[j]][res]*cost[expected[j]][res])
					global misclassification_count
					misclassification_count = misclassification_count + 1
					errors.append((expected[j] - neuron['output'])*cost[expected[j]][res]*cost[expected[j]][res])
		for j in range(len(layer)):
			neuron = layer[j]
			 #print(cost[expected[j]][neuron['output']])   ,((-1)*int(math.log(neuron['output'])))
			neuron['delta'] = errors[j] * transfer_derivative(neuron['output'])
		count_error += sum(errors)
	#print(count_error)
	writer.writerow([count_error])
			
#writer.writerow(['Error'])
# Update network weights with error
def update_weights(network, row, l_rate,expected):
	for i in range(len(network)):
		inputs = row[:-1]
		if i != 0:
			inputs = [neuron['output'] for neuron in network[i - 1]]
		for neuron in network[i]:
			for j in range(len(inputs)):
				#print(inputs[j])
				neuron['weights'][j] += l_rate * neuron['delta'] * inputs[j] #* cost[expected[j]][((-1)*int(math.log(neuron['output'])))]
				#print(neuron['output'])
			neuron['weights'][-1] += l_rate * neuron['delta']

# Train a network for a fixed number of epochs
def train_network(network, train, l_rate, n_epoch, n_outputs):
	#print(misclassification_count)
	for epoch in range(n_epoch):
		for row in train:
			outputs = forward_propagate(network, row)
			res = outputs.index(max(outputs))
			
			expected = [0 for i in range(n_outputs)]
			expected[row[-1]] = 1
			#print(row[-1])
			backward_propagate_error(network, expected, res)
			update_weights(network, row, l_rate, expected)

# Initialize a network
def initialize_network(n_inputs, n_hidden, n_outputs):
	network = list()
	hidden_layer = [{'weights':[random() for i in range(n_inputs + 1)]} for i in range(n_hidden)]
	network.append(hidden_layer)
	output_layer = [{'weights':[random() for i in range(n_hidden + 1)]} for i in range(n_outputs)]
	network.append(output_layer)
	return network

# Make a prediction with a network
def predict(network, row):
	outputs = forward_propagate(network, row)
	return outputs.index(max(outputs))

# Backpropagation Algorithm With Stochastic Gradient Descent
def back_propagation(train, test, l_rate, n_epoch, n_hidden):
	n_inputs = len(train[0]) - 1
	n_outputs = len(set([row[-1] for row in train]))
	#print(len(train))
	network = initialize_network(n_inputs, n_hidden, n_outputs)
	#print(len(test))
	train_network(network, train, l_rate, n_epoch, n_outputs)
	predictions = list()
	for row in test:
		prediction = predict(network, row)
		#print(prediction)
		predictions.append(prediction)
	#print(predictions)
	return(predictions)

# Test Backprop on Seeds dataset
seed(1)
# load and prepare data
#filename = 'cardio_nsp.csv'
#filename = 'pages-blocks.csv'
error_filename = 'error_ep1_activity_FSsqcost.csv'
filename = 'featureSelected_activitydata.csv'
#error_filename = 'error_ep1_activity_FSsqcost.csv'
oFile = open(error_filename, "w")
writer = csv.writer(oFile, delimiter=',', dialect='excel', lineterminator='\n')
#cost = ((0, 1, 2), (4, 0, 4), (8, 6, 0)) # misclassification cost matrix for cardio
#cost = ((0,2,5,6,18),(1,0,3,2,6),(1,3,0,1,4),(1,4,2,0,3),(1,1,2,2,0)) # misclassification cost matrix for page blocks
cost = ((0,1,1,3,2,3),(1,0,2,2,3,4),(1,2,0,2,3,4),(2,3,3,0,1,1),(1,2,2,1,0,2),(4,5,5,1,2,0)) # misclassification cost matrix for HAR
dataset = load_csv(filename)
for i in range(len(dataset[0])-1):
	str_column_to_float(dataset, i)
# convert class column to integers
str_column_to_int(dataset, len(dataset[0])-1)
# normalize input variables
minmax = dataset_minmax(dataset)
normalize_dataset(dataset, minmax)
# evaluate algorithm
misclassification_count = 0
misclassification_cost = 0
actual_misclassification_count = 0
n_folds = 2
l_rate = 0.1
n_epoch = 10
n_hidden = 10
#cost_matrix = [[0,0,0],[0,0,0],[0,0,0]] # cost matrix for cardio
#cost_matrix = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]] # cost matrix for page blocks
cost_matrix = [[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]] # cost matrix for HAR
scores = evaluate_algorithm(dataset, back_propagation, n_folds, l_rate, n_epoch, n_hidden)
#print('Scores: %s' % scores)
print('Mean Accuracy: %.3f%%' % (sum(scores)/float(len(scores))))
print("This is overall cost (square of cost) during training "+ str(misclassification_cost))
print("this is misclassification count during training. Includes all folds(=2) and iterations "+str(misclassification_count))
print("this is misclassification during test "+str(actual_misclassification_count))
print(cost_matrix)
oFile.close()
