import numpy as np

def normalize_and_calculate_weights(matrix):
    """Normalize matrix and calculate priority weights."""
    # Add small epsilon to avoid division by zero
    col_sums = np.sum(matrix, axis=0) + 1e-10
    normalized = matrix / col_sums
    weights = np.mean(normalized, axis=1)
    return weights

def determine_consistency(matrix, weights, ri_values):
    """Calculate Consistency Ratio (CR)."""
    n = len(weights)
    if n <= 1:
        return 0  # No inconsistency for 1x1 matrix
    
    # Calculate lambda_max
    weighted_sum = matrix @ weights  # Matrix multiplication is clearer
    lambda_i = weighted_sum / weights
    lambda_max = np.mean(lambda_i)
    
    # Calculate consistency index and ratio
    ci = (lambda_max - n) / (n - 1)
    
    # Check if we have an RI value for this matrix size
    if n-1 >= len(ri_values) or ri_values[n-1] == 0:
        return ci  # Return just CI if no RI available
    
    cr = ci / ri_values[n-1]
    return cr

def compute_alternative_score(specs, criteria_matrix):
    """Compute scores for alternatives based on criteria weights."""
    # Random Index values for consistency check
    ri_values = [0, 0, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]
    
    # Calculate criteria weights
    try:
        weights = normalize_and_calculate_weights(criteria_matrix)
    except Exception as e:
        return None, None, f"Error calculating weights: {str(e)}"
    
    # Check consistency
    cr = determine_consistency(criteria_matrix, weights, ri_values)
    if cr > 0.1:
        return None, None, f"Criteria matrix inconsistent (CR = {cr:.4f})"
    
    # Prepare specs table (skip first row, first column)
    if len(specs) <= 1:
        return None, None, "Not enough specifications provided"
    
    specs_table = [spec[1:] for spec in specs[1:]]
    
    # Calculate alternative scores
    try:
        alternatives_scores = [np.array(spec) * weights for spec in specs_table]
        totals = np.sum(alternatives_scores, axis=1)
        return alternatives_scores, totals, "Success"
    except Exception as e:
        return None, None, f"Error calculating scores: {str(e)}"

# crit_matrix_data = [
#             [1, 5, 3, 3, 7],
#             [0.2, 1, 0.333, 0.333, 5],
#             [0.333, 3, 1, 1, 5],
#             [0.333, 3, 1, 1, 5],
#             [0.143, 0.2, 0.2, 0.2, 1]
#         ]

# memory_specs = [8, 2, 3, 3, 4, 12, 4, 12, 4, 6, 6]  # GB
# storage_specs = [256, 64, 64, 64, 128, 256, 128, 512, 128, 128, 256]  # GB
# cpu_specs = [3.0, 1.5, 1.8, 1.8, 2.0, 3.0, 2.0, 3.2, 2.0, 2.5, 2.8]  # GHz
# price_specs = [800, 150, 200, 200, 300, 700, 300, 1000, 400, 600, 900]  # USD
# brand_scores = [8, 1, 2, 2, 7, 8, 5, 10, 5, 7, 9]

# alternatives = ["iPhone 12", "Itel A56", "Tecno Camon 12", "Infinix Hot 10", 
#                 "Huawei P30", "Google Pixel 7", "Xiaomi Redmi Note 10", 
#                 "Samsung Galaxy S22", "Motorola Razr+", "iPhone XR", 
#                 "Samsung Galaxy Note 10"]
# criteria = ["Memory", "Storage", "CPU Frequency", "Price", "Brand"]

# criteria.insert(0, "Alternatives")

# specs = [criteria]

# for index, alt in enumerate(alternatives):
#     specs.append([alt, memory_specs[index], storage_specs[index], cpu_specs[index], price_specs[index], brand_scores[index]])

# # print(specs)
# print(compute_alternative_score(specs, crit_matrix_data))