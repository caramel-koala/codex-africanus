from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import dask.array as da
import numpy as np
import africanus.opts.tests.helpers_1d as h
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from africanus.opts.primaldual import primal_dual_solver

np.random.seed(111)
da.random.seed(111)

NCPU = 8

sigma = 1.0

# generate u and l data
nrow = 1001

uvw = np.linspace(0.1, 10, nrow).reshape(nrow, 1) # 1 + np.random.random(size=(nrow,1))*10
# uvw = 0.1 + 10 * np.random.random(size=(nrow, 1))

delta_l = 1.0/(3*uvw.max())
# npix = int(np.ceil(01.0/(uvw.min()*delta_l)))
# if npix % 2 == 0:
#     npix += 1

npix = 1001

lm_stop = delta_l*(npix//2)
lm = da.linspace(-lm_stop, lm_stop, npix, chunks=npix)
lm = lm.reshape([npix, 1])

uvw = da.from_array(uvw, chunks=[nrow//NCPU, 1])
weights = sigma**2 * da.ones_like(uvw, chunks=nrow//NCPU)
wsum = sum(weights)

# make matrix covariance
FFT_mat = h.make_fft_matrix(lm, npix)
iFFT_mat = FFT_mat.conj().T

Phi_mat = h.make_dft_matrix(uvw, lm)
Phi_mat_adj = Phi_mat.conj().T

Inner_mat = Phi_mat_adj.dot(weights*Phi_mat)
Cov_mat = FFT_mat.dot(Phi_mat_adj.dot(weights*Phi_mat.dot(iFFT_mat)))

Inner_mat, Cov_mat, lm, uvw, weights, Phi_mat_adj, Phi_mat, wsum = da.compute(Inner_mat, Cov_mat, lm, uvw, weights, Phi_mat_adj, Phi_mat, wsum)

cov_diag = np.diagonal(Cov_mat)

weights = weights.flatten()

# plt.figure('FFT')
# plt.imshow(FFT_mat.real)
# plt.colorbar()
#
# plt.figure('DFT')
# plt.imshow(Phi_mat.real)
# plt.colorbar()
#
#
# plt.figure('RER')
# plt.imshow(Inner_mat.real)
# plt.colorbar()
#
# plt.figure("FRERF")
# plt.imshow(Cov_mat.real)
# plt.colorbar()

# make psf hat

psf = Phi_mat_adj.dot(weights)

# plt.figure("PSF")
# plt.plot(lm, psf.real)

psf_hat = FFT_mat.dot(psf)
# psf_hat[psf_hat<0] = 0

# plt.figure("PSf_hat vs Diagonal")
# plt.plot(lm, psf_hat, 'b')
# plt.plot(lm, cov_diag.real, 'r')
# plt.plot(lm, abs(psf_hat - cov_diag).real, 'g')

# make an image to convolve
nsource = 5
sources = np.random.randint(npix//4, 3*npix//4, nsource)
image = np.zeros_like(lm)
for pix in sources:
    image[pix] = np.random.random()*10

plt.figure('True image')
plt.plot(lm, image)

noise = (np.zeros(nrow) + 0.1*sigma*(np.random.randn(nrow) + 1.0j * np.random.randn(nrow))).flatten()

vis = Phi_mat.dot(image) #+ noise

# plt.figure("Visibility")
# plt.plot(uvw, vis.real)

dirty_image = Phi_mat_adj.dot(weights*vis.flatten()).real.reshape([-1, 1])
# dirty_image[dirty_image<0] = 0

# plt.figure('Dirty image')
# plt.plot(lm, dirty_image/npix)

grid_vis = FFT_mat.dot(dirty_image).reshape([-1, 1])

sigma_1 = 1/np.sqrt(psf_hat)
# sigma_1[np.isnan(sigma_1)] = 0

# plt.figure('Sigma Hat')
# plt.plot(lm, sigma_1)

white_vis = (sigma_1.flatten()*grid_vis.flatten()).reshape([-1, 1])

white_psf_hat = (sigma_1.flatten()*psf_hat.flatten()).reshape([-1, 1])

# plt.figure('white psf hat')
# plt.plot(lm, white_psf_hat.real)
# plt.plot(lm, white_psf_hat.imag, 'r')

# plt.figure('grid vis')
# plt.plot(lm, grid_vis.real)
# plt.plot(lm, grid_vis.imag, 'r')

# plt.figure('white vis')
# plt.plot(lm, white_vis.real)
# plt.plot(lm, white_vis.imag, 'r')

start = np.zeros([npix, 1])
start[npix//2] = 10

# operator = lambda img: (white_psf_hat.flatten()*h.FFT(img.flatten())).reshape([-1, 1])
# adjoint = lambda vis: (h.iFFT(white_psf_hat.flatten()*vis.flatten()).real/npix).reshape([-1, 1])/sum(weights)
#
# full_clean = primal_dual_solver(start, white_vis, operator, adjoint, maxiter=2000)

operator = lambda img: (psf_hat.flatten()*FFT_mat.dot(img.flatten())).reshape([-1, 1])
adjoint = lambda vis: iFFT_mat.dot(psf_hat.flatten()*vis.flatten()).real.reshape([-1, 1])/wsum

full_clean = primal_dual_solver(dirty_image, grid_vis, operator, adjoint, maxiter=2000)/np.sqrt(wsum)

# full_op = lambda x: Phi_mat.dot(x)
# full_adj = lambda y: Phi_mat_adj.dot(y)/wsum
#
# full_clean = abs(primal_dual_solver(start, vis, full_op, full_adj, maxiter=2000, tol=1e-8))

plt.figure("Full Clean")
plt.plot(lm, full_clean)

print(full_clean.max()/image.max())

plt.figure("Compare")
plt.plot(lm, full_clean-image)

plt.show()