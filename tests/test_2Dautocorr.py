import numpy as np
import matplotlib.pyplot as plt
from autocorrelation_zeropadding import acorr2D_zp
# Parameters of the 2D plane wave
A = 1           # Amplitude of the wave
wavelength = 10  # Wavelength (in arbitrary units)
k = 2 * np.pi / wavelength  # Wave number
omega = 2       # Angular frequency
t = 0           # Snapshot at time t

# Create a grid of x, y points
x = np.linspace(0, 40, 400)  # X-axis points
y = np.linspace(0, 40, 400)  # Y-axis points
X, Y = np.meshgrid(x, y)       # Create a meshgrid

# Define wave propagation direction (kx and ky)
kx = k * np.cos(np.pi / 4)  # Wave propagating at a 45-degree angle
ky = k * np.sin(np.pi / 4)

# Compute the 2D plane wave at time t
Z = A * np.sin(kx * X + ky * Y - omega * t)


fig, axes = plt.subplots(2, 2, figsize=(10, 8))  # 2 rows, 2 columns

# Define contour levels to control colormap limits
#levels = np.linspace(-1, 1, 100)  # 100 levels between -1 and 1

# Plot the wave snapshot
cont=axes[0,0].contourf(X, Y, Z, levels=100, cmap='gray')
#axes[0,0].set_xlim([0,20])
#axes[0,0].set_ylim([0,20])
plt.colorbar(cont)

# get 2D autocorrelation of wave
mask = np.ones_like(Z)

autocorr1 = acorr2D_zp(Z,mask=mask)

cont=axes[0,1].contourf(X, Y, autocorr1, levels=100, cmap='gray')
#axes[0,1].set_xlim([0,20])
#axes[0,1].set_ylim([0,20])
plt.colorbar(cont)

# choose randomly missing values and set to 0 (=average)
# Choose 10000 random row indices random column indices
row_indices = np.random.choice(400, size=100, replace=True)
col_indices = np.random.choice(400, size=100, replace=True)

# Combine row and column indices into pairs (10000 random index pairs)
random_indices = list(zip(row_indices, col_indices))

# Access values from the array at these random indices
Z[random_indices] = 0

cont=axes[1, 0].contourf(X, Y, Z, levels=100, cmap='gray')
plt.colorbar(cont)

mask = np.ones_like(Z)
mask[random_indices] = 0
autocorr1 = acorr2D_zp(Z,mask=mask)
cont=axes[1,1].contourf(X, Y, autocorr1, levels=100, cmap='gray')
plt.colorbar(cont)



plt.show()
# plot a snapshot of a 2D wave



