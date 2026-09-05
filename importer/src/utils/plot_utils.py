import matplotlib.pyplot as plt

def safe_show():
    plt.show(block=False)
    plt.pause(0.1)