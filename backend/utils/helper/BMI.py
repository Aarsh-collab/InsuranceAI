def calculate_BMI(height_f, height_i, weight):
    
    total_inches = (height_f * 12) + height_i

    total_meters = total_inches * 0.0254

    kg = weight * 0.453592

    BMI = kg / (total_meters ** 2)

    return round(BMI, 1)