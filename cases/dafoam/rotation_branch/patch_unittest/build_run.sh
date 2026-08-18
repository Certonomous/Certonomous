#!/usr/bin/env bash
# Compile the L-26 controlled experiment against the PATCHED clone and run it.
# Everything happens inside the pinned dafoam image; nothing installed is touched.
set -euo pipefail
HERE=/home/ubuntu/certonomous-runs/W5-patch
sudo docker run --rm --cpus=2 --memory=2g \
    -v "$HERE":/mnt -w /mnt/unittest dafoam/opt-packages:latest bash -lc '
set -e
SRC=/mnt/idwarp/src
rm -rf build && mkdir build && cd build
gfortran -c -O2 -fdefault-real-8 $SRC/modules/precision.F90
gfortran -c -O2 -fdefault-real-8 $SRC/modules/constants.F90
gfortran -c -O2 -fdefault-real-8 $SRC/utils/vectorUtils.f90
gfortran -c -O2 -fdefault-real-8 $SRC/adjoint/outputReverse/vectorUtils_b.f90
gfortran -c -O2 -fdefault-real-8 $SRC/adjoint/outputForward/vectorUtils_d.f90
gcc -c -O2 $SRC/adjoint/ADFirstAidKit/adStack.c
gfortran -c -O2 -fdefault-real-8 ../test_rotderiv.f90
gfortran -o test_rotderiv *.o
./test_rotderiv
'
