try:
    choice = int(input("Enter your choice: "))
except Exception as _:
    choice = "bullshit"

match (choice):
    case 1:
        print("fuck")
    case 2:
        print("something")
    case 3:
        print("anothe rone")
    case _:
        print("Please select 1 or 2.")
