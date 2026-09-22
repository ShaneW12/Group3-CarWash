from service import (
    standard_wash,
    triple_foam,
    undercarriage,
    interior_detailing,
    vacuum,
    additional_cleaning,
    calculate_total,
    Rewards
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

#here come the rewards part
rewards = Rewards()

rewards.add_tokens(total)

print("Tokens: " + str(rewards.tokens))
print("Can redeem: " + str(rewards.can_redeem()))

rewards.add_tokens(9)

print("Tokens after spending another $9: " + str(rewards.tokens))
print("Can redeem: " + str(rewards.can_redeem()))

rewards.redeem_wash()

print("Tokens after redeeming free wash: " + str(rewards.tokens))