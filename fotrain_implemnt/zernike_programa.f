      PROGRAM ZERNIKE_MAIN
C     ================================================================
C     DECLARACIONES Y PREPARACION DE DATOS
C     ================================================================

      DIMENSION X(50000),Y(50000),W(50000)
      DOUBLE PRECISION SMAX,TE,A(15)
      CHARACTER(LEN=100) :: ARCH
      INTEGER :: IGRADO, IPRINT, N, L, J, I

      IGRADO = 4
      IPRINT = 1
      N = 0

      WRITE(*,*) 'DA EL NOMBRE DEL ARCHIVO DE DATOS:'
      READ(*,'(A)') ARCH

      OPEN(UNIT=10, FILE=TRIM(ARCH), STATUS='OLD')
      OPEN(UNIT=20, FILE='INTER.DAT', STATUS='UNKNOWN')

C
C     *** LECTURA DE DATOS ***
C
      SMAX = 0.0
      J = 1
    2 READ(10,*,END=10) X(J),Y(J),W(J)
      IF(X(J) .EQ. 10000.0) GO TO 10
      N = N + 1
      TE = DBLE(X(J)**2) + DBLE(Y(J)**2)
C
C     *** SE OBTIENE EL VALOR MAXIMO DE <X**2 + Y**2> ***
      IF(TE.GT.SMAX) SMAX = TE
      J = J + 1
      IF(J .GT. 50000) THEN
         WRITE(*,*) 'ERROR: DEMASIADOS DATOS (MAX 50000)'
         GO TO 10
      END IF
      GO TO 2
   10 CONTINUE

C     *** NORMALIZACION DE COORDENADAS ***
      DO 15 I=1,N
      X(I)=X(I)/SQRT(SMAX)
      Y(I)=Y(I)/SQRT(SMAX)
   15 CONTINUE

C     *** SE CALCULA EL NUMERO DE POLINOMIOS ORTOGONALES POR GENERAR ***
      L=(IGRADO+1)*(IGRADO+2)/2

C     *** SE LLAMA A LA SUBRUTINA QUE CALCULA LOS COEFICIENTES ***
      CALL ZERXY2(X,Y,W,N,L,20,IPRINT,A)

      CLOSE(10)
      CLOSE(20)

      WRITE(*,*) 'PROCESO COMPLETADO. RESULTADOS EN INTER.DAT'
      END

C     ================================================================
C     NUCLEO MATEMATICO: SUBRUTINA ZERXY2
C     ================================================================
      SUBROUTINE ZERXY2(X,Y,W,N,L,LR,IPRINT,A)

      DIMENSION X(50000),Y(50000),W(50000),D(15,15),U(15,50000),
     * V(15,50000),B(15),WXY(50000),A(15),C(15,15)

      DOUBLE PRECISION U,D,V,SND,SDD,SUM,SNB,SDB,SUMA,
     * ACUM,ACUMA,B,C,A,RMS

C
C     *** ORTOGONALIZACION DE GRAM-SCHMIDT ***
C
      DO 15 I=1,N
      U(1,I)=1.0D0
      U(2,I)=DBLE(X(I))
      U(3,I)=DBLE(Y(I))
      U(4,I)=2.0D0*DBLE(X(I)*Y(I))
      U(5,I)= -1.0D0 + 2.0D0*DBLE(Y(I)*Y(I)) + 2.0D0*
     -        DBLE(X(I)*X(I))
      U(6,I)=DBLE(Y(I)*Y(I) - X(I)*X(I))
      U(7,I)=3.0D0*DBLE(X(I)*Y(I)*Y(I)) - DBLE(X(I)**3)
      U(8,I)=-2.0D0*DBLE(X(I)) + 3.0D0*DBLE(X(I)*Y(I)**2)
     -       + 3.0D0*DBLE(X(I)**3)
      U(9,I)=-2.0D0*DBLE(Y(I)) + 3.0D0*DBLE(Y(I)**3) + 3.0D0*
     -       DBLE((X(I)**2)*Y(I))
      U(10,I)=DBLE(Y(I)**3) - 3.0D0*DBLE((X(I)**2)*Y(I))
      U(11,I)=4.0D0*DBLE((Y(I)**3)*X(I)) - 4.0D0*DBLE((X(I)**3)*
     -        Y(I))
      U(12,I)=-6.0D0*DBLE(X(I)*Y(I)) + 8.0D0*DBLE((Y(I)**3)*
     -        X(I)) + 8.0D0*DBLE((X(I)**3)*Y(I))
      U(13,I)=1.0D0 - 6.0D0*DBLE(Y(I)**2)-6.0D0*DBLE(X(I)**2) +
     -        6.0D0*DBLE(Y(I)**4) + 12.0D0*DBLE((X(I)**2)*(Y(I)**2))
     -        + 6.0D0*DBLE(X(I)**4)
      U(14,I)=-3.0D0*DBLE(Y(I)**2) + 3.0D0*DBLE(X(I)**2) + 4.0D0*
     -        DBLE(Y(I)**4) - 4.0D0*DBLE(X(I)**4)
      U(15,I)=DBLE(Y(I)**4) - 6.0D0*DBLE((X(I)**2)*(Y(I)**2)) +
     -        DBLE(X(I)**4)
      V(1,I)=U(1,I)
   15 CONTINUE

C
C     *** CALCULO DE V(J,I), D(J,IS) ***
C
      DO 30 J=2,L
      DO 25 IS=1,J-1
      SND=0.0D0
      SDD=0.0D0
      DO 20 I=1,N
      SND=SND + U(J,I)*V(IS,I)
      SDD=SDD + V(IS,I)**2
   20 CONTINUE
      D(J,IS)=-(SND/SDD)
   25 CONTINUE
      DO 27 I=1,N
      SUM=0.0D0
      DO 26 JS=1,J-1
      SUM=SUM + D(J,JS)*V(JS,I)
   26 CONTINUE
      V(J,I)=U(J,I) + SUM
   27 CONTINUE
   30 CONTINUE

C
C     *** CALCULO DE B(J) ***
C
      DO 40 J=1,L
      SNB=0.0D0
      SDB=0.0D0
      DO 35 I=1,N
      SNB=SNB + DBLE(W(I))*V(J,I)
      SDB=SDB + V(J,I)**2
   35 CONTINUE
      B(J)=SNB/SDB
   40 CONTINUE

C
C     *** SE EVALUA LA FUNCION AJUSTADA ***
C
      IF(IPRINT.EQ.0) GO TO 70

      WRITE(LR,*)
     -'       * X * * Y * * W * * WXY * * ERROR *'
      WRITE(LR,*) ' '

      RMS=0.0D0
      SUM=0.0D0
      DO 50 I=1,N
      ACUM=0.0D0
      DO 60 J=1,L
      ACUM=ACUM + B(J)*V(J,I)
   60 CONTINUE
      WXY(I)=SNGL(ACUM)
      SUM=SUM + DBLE((W(I)-WXY(I))**2)
      WRITE(LR,65) X(I),Y(I),W(I),WXY(I),W(I)-WXY(I)
   65 FORMAT(' ',5(1PE16.8,1X))
   50 CONTINUE


      RMS=DSQRT(SUM/DBLE(FLOAT(N)))
      WRITE(LR,55) RMS
   55 FORMAT(//,8X,' LA DESVIACION ESTANDAR ES :',E15.5,//)

   70 CONTINUE

C
C     *** CALCULO DE LOS COEFICIENTES DE ABERRACION ***
C
      DO 200 J=2,L-1
      C(J,J-1)=D(J,J-1)
      C(J,J)=1.0D0
  200 CONTINUE
      C(1,1)=1.0D0
      C(L,L-1)=D(L,L-1)
      DO 210 J=2,L
      DO 220 KK=1,J-1
      SUMA=0.0
      DO 225 IS=1,J-KK
      SUMA=SUMA + D(J,J-IS)*C(J-IS,KK)
  225 CONTINUE
      C(J,KK)=SUMA
  220 CONTINUE
  210 CONTINUE

      DO 240 J=1,L-1
      ACUMA=0.0D0
      DO 250 IS=J+1,L
      ACUMA=ACUMA + B(IS)*C(IS,J)
  250 CONTINUE
      A(J)=B(J) + ACUMA
  240 CONTINUE

      A(L)=B(L)
      
C IMPRESION DE LOS COEFICIENTES A
      WRITE(*,*) ' '
      WRITE(*,*) '--- Coeficientes de Zernike A ---'
      DO 260 J=1,L
        IF (A(J) .GE. 0.0D0) THEN
          WRITE(*,265) J, A(J)
        ELSE
          WRITE(*,266) J, A(J)
        END IF
  260 CONTINUE
  265 FORMAT('  A_', I2, ' = +', F8.6)
  266 FORMAT('  A_', I2, ' = ', F9.6)
      
      WRITE(*,*) ' '
      WRITE(*,270) RMS
  270 FORMAT(' Error RMS del ajuste: ', 1PE9.2)

      RETURN
      END
