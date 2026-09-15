from service import (
    standard_wash,
    triple_foam,
    undercarriage,
    interior_detailing,
    vacuum,
    additional_cleaning,
    calculate_total
)


print(standard_wash)
print(triple_foam)
print(undercarriage)
print(interior_detailing)
print(vacuum)
print(additional_cleaning)


selected_services = [
    standard_wash,
    triple_foam,
    undercarriage,
    interior_detailing,
    vacuum,
    additional_cleaning
]

total = calculate_total(selected_services)

print("Total: $" + str(total))