import os

print("MAdif.scv: files that save the signals short or long")
x = input("Do you would remove this file? <yes/no>")

while x != 'yes' or x != 'no':
    if x == 'yes':
        if os.path.exists('static/MAdif.csv'):
            os.remove('static/MAdif.csv')
            print("the file has been success removed")
        else:
            print('file not found or removed')
        break

    elif x == 'no':
        print('bye!')
        break
    print('Entry not valid. Please indicate a valid option')
    x = input("Do you would remove this file? <yes/no>")

print('\n')
# for advice.scv file
print("advice.scv: files that save advice and date of second backtest!")
x = input("Do you would remove this file? <yes/no>")

while x != 'yes' or x != 'no':
    if x == 'yes':
        if os.path.exists('static/advice.csv'):
            os.remove('static/advice.csv')
            print("the file has been success removed")
        else:
            print('file not found or removed')
        break

    elif x == 'no':
        print('bye!')
        break
    print('Entry not valid. Please indicate a valid option')
    x = input("Do you would remove this file? <yes/no>")