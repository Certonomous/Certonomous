!  FOILMOD. This program slightly modifies the airfoil section 
!  for the ONERA M6 wing to remove the trailing edge thickness.
!  The z/l coordinates from x/l=0.90 to the trailing edge are 
!  linearly scaled down.

   PROGRAM foilmod

   IMPLICIT none

   INTEGER :: i
   REAL, DIMENSION(72) :: x, z

!..Read the original section coordinates.

   OPEN ( unit=7, file='airfoil.txt' )

   DO  i = 1, 72
     READ(7,*) x(i), z(i)
   ENDDO

!..Scale from x=0.9 to x=1.0.

   DO  i = 59, 71
     z(i) = z(i) - ( ( x(i) - 0.9 ) / 0.1 ) * z(72)
   ENDDO

!..Ensure trailing edge is exactly zero.

   z(72) = 0.0

!..Write out modified airfoil.

   OPEN ( unit=8, file='foilmod.txt' )

   DO  i = 1, 72
     WRITE(8,'(2(2x,f10.7))') x(i), z(i)
   ENDDO

   END PROGRAM foilmod



