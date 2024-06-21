import os

def generateSet(filepath_output):
    """Generates a Set file which can be taken over by EvoCheker. Equates the values for Baseline"""

    baseline = []
    decision_line = ""

    # #Decision Lines
    # for i in range(0,10):
    #     for a in range(0,10):
    #         decision_line = decision_line + f"decision_{i}_{a} "
    # decision_line = decision_line.strip()

    #baseline.append(decision_line)

    #Empty Line
    baseline.append("\n")

    #Baseline Values Line
    for i in range(0,11):
        for a in range(0,100):
            if a == 0:
                decision_line = f"{i}"
            else:
                decision_line = decision_line + f" {i}"
        
        baseline.append(decision_line)
            
    for line in baseline:
        print(line)

    #Write to file
    with open(filepath_output, 'w') as f:
        for line in baseline:
            f.write(f"{line}\n")