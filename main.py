import numpy as np
import logging
import csv

logging.basicConfig(level=logging.INFO,
                    format='- %(message)s',
                    # format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()])

def sum_columns(numpy_array):
    return np.sum(numpy_array, axis=0)

def iterate_and_print(matrix):
    num_rows, num_cols = matrix.shape
    for i in range(num_rows):
        row_string = ""
        for j in range(num_cols):
            row_string += f"{matrix[i, j]:>4}\t"
        print(row_string)

def create_corcondance_matrix(data, weights):
    num_rows = len(data)
    comparison_matrix = np.zeros((num_rows, num_rows))

    for i in range(num_rows):
        for j in range(num_rows):
            if i == j:
                continue
            else:
                comparison_result = np.array(data[i]) - np.array(data[j])
                result = np.where(comparison_result < 0, 0, weights)
                sum_result = np.sum(result)
                comparison_matrix[i, j] = sum_result

    return comparison_matrix

def create_max_matrix(data):
    num_rows = len(data)
    comparison_matrix = np.zeros((num_rows, num_rows))
    for i in range(num_rows):
        for j in range(num_rows):
            if i == j:
                continue
            else:
                comparison_result = data[i] - data[j]
                positive = np.abs(comparison_result)
                max = np.max(positive)
                comparison_matrix[i, j] = max
    return comparison_matrix

def create_discordance(data):
    num_rows = len(data)
    result_list = []
    for i in range(num_rows):
        inside = []
        for j in range(num_rows):
            # if i == j:
            #     continue
            # else:
            comparison_result = data[i] - data[j]
            result = np.where(comparison_result >= 0, 0, data[i])
            inside.append(result)
        result_list.append(inside)
    return result_list

def create_discordance_matrix(data, weight, max_matrix):
    num_rows = len(data)
    discordance_matrix = np.zeros((num_rows, num_rows))
    for i in range(num_rows):
        for j in range(len(data[i])):
            # if(i==j):
            #     continue
            # else:
            result = data[i][j] - weight[j]
            result = np.where(data[i][j] != 0, result, 0)
            positive = np.abs(result)
            # logging.info(f'Pengurangan {data[i][j]} - {weight[j]}')
            # logging.info(f'Hasil Absolute: {positive}')
            # logging.info(f'Max: {np.max(positive)} / {max_matrix[i][j]}')
            if(max_matrix[i][j]!=0):
                final_result = np.max(positive)/max_matrix[i][j]
            else:
                final_result = 0
            # logging.info(f'Hasil: {final_result}')
            # logging.info("++++++++++++++++++++++++++++++++++")
            discordance_matrix[i, j] = final_result
    return np.nan_to_num(discordance_matrix)
                
def matrix_to_csv(matrix, filename):
    # Replace NaN values with 0
    matrix = np.nan_to_num(matrix)

    # Write the matrix to a CSV file
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(matrix)


def create_matrix_dominance_concordance(concordance):
    treshold = np.sum(concordance)/(concordance.shape[0]*(concordance.shape[0]-1))
    num_rows = len(concordance)
    matrix = np.zeros((num_rows, num_rows))
    for i in range(num_rows):
        for j in range(num_rows):
            value = concordance[i][j] - treshold
            result = np.where(value >=0, 1, 0)
            matrix[i,j] = result
    return matrix


def create_matrix_dominance_discordance(discordance):
    treshold = np.sum(discordance)/(discordance.shape[0]*(discordance.shape[0]-1))
    num_rows = len(discordance)
    matrix = np.zeros((num_rows, num_rows))
    for i in range(num_rows):
        for j in range(num_rows):
            value = discordance[i][j] - treshold
            result = np.where(value >=0, 1, 0)
            matrix[i,j] = result
    return matrix


def start():
    data = [
    [1, 1, 1, 5, 5],
    [5, 4, 2, 1, 3],
    [4, 2, 5, 5, 3],
    [4, 4, 4, 1, 3],
    [1, 1, 1, 5, 1],
    [4, 4, 5, 1, 5],
    [5, 5, 3, 3, 4],
    [3, 4, 3, 1, 5],
    [5, 4, 2, 4, 2],
    [4, 3, 2, 5, 4],
    [4, 3, 3, 1, 5],
    [3, 3, 3, 2, 3],
    [4, 3, 3, 5, 4],
    [5, 5, 3, 3, 5],
    [4, 3, 3, 2, 2],
    [4, 3, 2, 5, 3],
    [4, 3, 3, 1, 5],
    [2, 1, 5, 5, 4],
    [1, 1, 3, 3, 4]
]

    weights = [5, 3, 4, 3, 3]

    numpy_array = np.array(data)
    # print(numpy_array)
    #Normalisasi
    squared_array = np.square(numpy_array)
    # print(squared_array)

    column_sums = sum_columns(squared_array)
    # print("Column Sums:")
    # print(column_sums)

    rooted_sums = np.sqrt(column_sums)
    # print("Square Root of Column Sums:")
    # print(rooted_sums)

    normalized_array = numpy_array / rooted_sums
    # print("Normalized Array:")
    # print(normalized_array)

    weighted_array = normalized_array * weights
    concordance = create_corcondance_matrix(data, weights)
    dominance_concordance = create_matrix_dominance_concordance(concordance)


    max_matrix = create_max_matrix(weighted_array)
    # iterate_and_print(max_matrix)
    # Perbandingan antar baris
    comparison_matrix = create_discordance(weighted_array)
    discordance_matrix = create_discordance_matrix(comparison_matrix, weighted_array, max_matrix)
    dominance_discordance = create_matrix_dominance_discordance(discordance_matrix)
    aggregate = dominance_concordance * dominance_discordance
    row_sums = np.sum(aggregate, axis=1)
    print(row_sums)
    # csv_filename = 'discordance.csv'
    # matrix_to_csv(discordance_matrix, csv_filename)

if __name__ == "__main__":
    start()