TrueCondition = True
FalseCondition = False

# if else
if FalseCondition == False:
  print("im false")

if not FalseCondition:
  print("im false")

if TrueCondition:
  print("im true")
else:
  print("im false")

# for loops
employee1 = ["Arpita_t",716,12,1996,[[]]]
employee2 = ["Supreet_t",716,12,1996,[[]]]
employee3 = ["Vandana_t",716,12,1996,[[]]]
# for(int i=0;i<len(employee1);i++)
# {
#   print(employee1[i]);
#   print(employee2[i]);
# }

for myElement in employee1:
  print(myElement)

for myElement1,myElement2,myElement3 in zip(employee1,employee2,employee3):
  print(myElement)

for counter in range(5):
  print(counter)

for counter in range(len(employee1)):
  print(counter)
# while loops