import random
import numpy as np
import matplotlib.pyplot as plt

random.seed(10)
X = np.array([[random.randint(1, 10), random.randint(1, 10)] for _ in range(10)])
center = X.mean(axis=0)
X_new = X - center

fig, ax = plt.subplots(1, 2, figsize=(11, 4))

ax[0].scatter(X[:, 0], X[:, 1])
ax[0].scatter(*center, color="red", marker="X", s=110)
ax[0].set_title("Початкові дані")

ax[1].scatter(X_new[:, 0], X_new[:, 1])
ax[1].scatter(0, 0, color="red", marker="X", s=110)
ax[1].axhline(0, color="gray", linewidth=0.8)
ax[1].axvline(0, color="gray", linewidth=0.8)
ax[1].set_title("Після центрування")

for a in ax:
    a.set_xlabel("Ознака X")
    a.set_ylabel("Ознака Y")
    a.grid(alpha=0.3)

plt.tight_layout()
plt.show()

print("Центр:", center)
print("Новий центр:", X_new.mean(axis=0))