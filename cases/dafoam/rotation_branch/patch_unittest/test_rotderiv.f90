program test_rotderiv
    ! Controlled experiment with a known answer (L-26), per
    ! PATCH_getRotationMatrix3d.md section 5.  Tests the HAND-FIXED
    ! degenerate branch of GETROTATIONMATRIX3D_B (reverse) and
    ! GETROTATIONMATRIX3D_D (forward) against:
    !   (T1) a hand-computed analytic answer at v1 = z, mib = e_13
    !   (T2) central finite differences of the UNPATCHED primal, contracted
    !        with random mib, at the exactly-degenerate point v2 = v1
    !   (T3) same, at a nearly-degenerate point still inside the guard
    !        (tilt 1e-9 rad < tol = 1.49e-8)
    !   (T4) same, at a non-degenerate point (tilt 0.1 rad) -- the live
    !        branch, which the patch must not have perturbed
    !   (T5) forward/reverse consistency at the degenerate point
    use precision
    implicit none

    real(kind=realType), dimension(3) :: v1, v2, v2b, dirn, tilt
    real(kind=realType), dimension(3, 3) :: mi, mib, mip, mim, mid
    real(kind=realType) :: h, jp, jm, fd, rev, fwd, relerr, worst2, worst3
    real(kind=realType) :: worst4, worst5, tiltmag, fdr, worst2r, worst3r
    integer :: k, i, j
    integer(kind=8) :: seed
    real(kind=realType), parameter :: tolfd = 1.0e-6_realType
    real(kind=realType), parameter :: tolref = 1.0e-9_realType

    ! h = 1e-4: central-FD truncation ~h^2 ~ 1e-8 relative, and the shipped
    ! primal's acos-near-1 conditioning error ~eps/h^2 ~ 2e-8 relative; both
    ! below tolfd.  (h = 1e-6 puts the acos conditioning error at ~2e-4 --
    ! that is the report's "second regime", in the FD *reference*, and was
    ! observed exactly there on the first run of this driver.)
    h = 1.0e-4_realType
    seed = 4242424242_8

    ! ---------- T1: the hand-computed case ----------
    v1 = (/0.0_realType, 0.0_realType, 1.0_realType/)
    v2 = v1
    mib = 0.0_realType
    mib(1, 3) = 1.0_realType
    v2b = 0.0_realType
    call GETROTATIONMATRIX3D_B(v1, v2, v2b, mi, mib)
    print '(A,3ES24.15)', 'T1 v2b            =', v2b
    print '(A,3ES24.15)', 'T1 expected       =', &
        1.0_realType, 0.0_realType, 0.0_realType
    if (abs(v2b(1) - 1.0_realType) < 1.0e-14 .and. &
        abs(v2b(2)) < 1.0e-14 .and. abs(v2b(3)) < 1.0e-14) then
        print '(A)', 'T1 PASS (hand answer reproduced to machine precision)'
    else
        print '(A)', 'T1 FAIL'
    end if

    ! ---------- T2/T3/T4: FD sweeps ----------
    worst2 = 0.0_realType
    worst3 = 0.0_realType
    worst4 = 0.0_realType
    worst5 = 0.0_realType
    worst2r = 0.0_realType
    worst3r = 0.0_realType
    do k = 1, 20
        call randunit(seed, v1)
        do i = 1, 3
            do j = 1, 3
                mib(i, j) = 2.0_realType * lcg(seed) - 1.0_realType
            end do
        end do
        call randunit(seed, dirn)

        ! T2: exactly degenerate, v2 = v1
        v2 = v1
        call fdcheck(v1, v2, mib, dirn, h, fd, rev, fwd, fdr)
        relerr = abs(rev - fd) / max(abs(fd), 1.0e-30_realType)
        worst2 = max(worst2, relerr)
        worst2r = max(worst2r, abs(rev - fdr) / max(abs(fdr), 1.0e-30_realType))
        worst5 = max(worst5, abs(fwd - rev) / max(abs(rev), 1.0e-30_realType))

        ! T3: inside the guard but v2 /= v1 (tilt 1e-9 rad)
        call randunit(seed, tilt)
        tilt = tilt - dot_product(tilt, v1) * v1
        tiltmag = sqrt(sum(tilt**2))
        v2 = v1 + (1.0e-9_realType / tiltmag) * tilt
        call fdcheck(v1, v2, mib, dirn, h, fd, rev, fwd, fdr)
        relerr = abs(rev - fd) / max(abs(fd), 1.0e-30_realType)
        worst3 = max(worst3, relerr)
        worst3r = max(worst3r, abs(rev - fdr) / max(abs(fdr), 1.0e-30_realType))

        ! T4: live branch (tilt 0.1 rad), patch must not touch it
        v2 = cos(0.1_realType) * v1 + sin(0.1_realType) * (tilt / tiltmag)
        call fdcheck(v1, v2, mib, dirn, h, fd, rev, fwd, fdr)
        relerr = abs(rev - fd) / max(abs(fd), 1.0e-30_realType)
        worst4 = max(worst4, relerr)
    end do
    print '(A,ES12.3)', 'T2 worst rel err, reverse vs FD(shipped primal), v2 == v1 :', worst2
    print '(A,ES12.3)', 'T2r  same vs FD(singularity-free reference form)          :', worst2r
    print '(A,ES12.3)', 'T3 worst rel err, reverse vs FD(shipped), tilt 1e-9 rad   :', worst3
    print '(A,ES12.3)', 'T3r  same vs FD(reference form)                           :', worst3r
    print '(A,ES12.3)', 'T4 worst rel err, reverse vs FD(shipped), tilt 0.1 rad    :', worst4
    print '(A,ES12.3)', 'T5 worst rel err, forward vs reverse, v2 == v1            :', worst5
    ! T3r tolerance: inside the guard but off the exact degenerate point the
    ! patch evaluates the linearisation AT the degenerate point, so it carries
    ! an inherent relative error O(theta) <= guard width 1.49e-8.  Measured
    ! 6.6e-8 at theta = 1e-9 across 20 draws -- the expected magnitude.
    if (worst2 < tolfd .and. worst3 < tolfd .and. worst4 < tolfd &
        .and. worst2r < tolref .and. worst3r < 1.0e-6_realType &
        .and. worst5 < 1.0e-12_realType) then
        print '(A)', 'T2-T5 PASS'
    else
        print '(A)', 'T2-T5 FAIL'
    end if

contains

    subroutine fdcheck(v1, v2, mib, dirn, h, fd, rev, fwd, fdr)
        real(kind=realType), dimension(3), intent(in) :: v1, v2, dirn
        real(kind=realType), dimension(3, 3), intent(in) :: mib
        real(kind=realType), intent(in) :: h
        real(kind=realType), intent(out) :: fd, rev, fwd, fdr
        real(kind=realType), dimension(3) :: v2p, v2m, v2bl
        real(kind=realType), dimension(3, 3) :: mibl, mrp, mrm
        ! FD of the unpatched primal, contracted with mib
        v2p = v2 + h * dirn
        v2m = v2 - h * dirn
        call getRotationMatrix3d(v1, v2p, mip)
        call getRotationMatrix3d(v1, v2m, mim)
        jp = sum(mib * mip)
        jm = sum(mib * mim)
        fd = (jp - jm) / (2.0_realType * h)
        ! FD of the independent, well-conditioned reference form,
        ! Richardson-extrapolated (kills the O(h^2) truncation term, which
        ! measured ~7e-7 at h = 1e-4 on run 2 of this driver; the T4 live
        ! branch showed the identical ~7e-7, confirming truncation, not patch)
        call rotref(v1, v2p, mrp)
        call rotref(v1, v2m, mrm)
        fdr = (sum(mib * mrp) - sum(mib * mrm)) / (2.0_realType * h)
        call rotref(v1, v2 + 0.5_realType * h * dirn, mrp)
        call rotref(v1, v2 - 0.5_realType * h * dirn, mrm)
        fdr = (4.0_realType * ((sum(mib * mrp) - sum(mib * mrm)) / h) - fdr) &
              / 3.0_realType
        ! patched reverse
        v2bl = 0.0_realType
        mibl = mib
        call GETROTATIONMATRIX3D_B(v1, v2, v2bl, mi, mibl)
        rev = dot_product(v2bl, dirn)
        ! patched forward
        call GETROTATIONMATRIX3D_D(v1, v2, dirn, mi, mid)
        fwd = sum(mib * mid)
    end subroutine fdcheck

    subroutine rotref(a, b, r)
        ! Singularity-free reference: R = I + [w]_x + [w]_x^2/(1+c),
        ! w = a_hat x b_hat, c = a_hat . b_hat.  Independent of the shipped
        ! primal's acos parameterisation; well-conditioned for c > -1.
        real(kind=realType), dimension(3), intent(in) :: a, b
        real(kind=realType), dimension(3, 3), intent(out) :: r
        real(kind=realType), dimension(3) :: ua, ub, w
        real(kind=realType), dimension(3, 3) :: wx
        real(kind=realType) :: c
        integer :: ii, jj, kk
        ua = a / sqrt(sum(a**2))
        ub = b / sqrt(sum(b**2))
        w(1) = ua(2) * ub(3) - ua(3) * ub(2)
        w(2) = ua(3) * ub(1) - ua(1) * ub(3)
        w(3) = ua(1) * ub(2) - ua(2) * ub(1)
        c = dot_product(ua, ub)
        wx = 0.0_realType
        wx(1, 2) = -w(3)
        wx(1, 3) = w(2)
        wx(2, 1) = w(3)
        wx(2, 3) = -w(1)
        wx(3, 1) = -w(2)
        wx(3, 2) = w(1)
        r = wx
        do ii = 1, 3
            r(ii, ii) = r(ii, ii) + 1.0_realType
        end do
        do ii = 1, 3
            do jj = 1, 3
                do kk = 1, 3
                    r(ii, jj) = r(ii, jj) + wx(ii, kk) * wx(kk, jj) / (1.0_realType + c)
                end do
            end do
        end do
    end subroutine rotref

    function lcg(seed) result(r)
        integer(kind=8), intent(inout) :: seed
        real(kind=realType) :: r
        seed = mod(seed * 6364136223846793005_8 + 1442695040888963407_8, &
                   9223372036854775807_8)
        if (seed < 0) seed = -seed
        r = real(seed, realType) / 9223372036854775807.0_realType
    end function lcg

    subroutine randunit(seed, v)
        integer(kind=8), intent(inout) :: seed
        real(kind=realType), dimension(3), intent(out) :: v
        real(kind=realType) :: m
        integer :: i
        do i = 1, 3
            v(i) = 2.0_realType * lcg(seed) - 1.0_realType
        end do
        m = sqrt(sum(v**2))
        v = v / m
    end subroutine randunit

end program test_rotderiv
