! Description:
! Linear algebra computational routines (Intel MKL wrappers).
module m_linalg
    use m_matrix
    implicit none
    
    private
    public multiply, determinant, inverse
    
    ! error messages
    character(*), parameter :: ERROR_SIZE_MISMATCH_FOR_MATRIX_MATRIX_PRODUCT = 'ERROR: Size mismatch for matrix-matrix product.', &
                               ERROR_MATRIX_MUST_BE_SQUARE_FOR_OPERATION     = 'ERROR: Matrix must be square for operation.',     &
                               ERROR_MATRIX_MUST_BE_SMALL_FOR_OPERATION      = 'ERROR: Matrix must be small for operation.'
    
    interface multiply
        module procedure :: BLAS_GEMM_1, BLAS_GEMM_2
    end interface
    
    contains
    
    ! Description:
    ! Computes a matrix-matrix product with general matrices.
    ! The operation is defined as C := alpha*op(A)*op(B) + beta*C, where:
    ! * A, B, and C are matrices.
    ! * alpha and beta are scalars.
    ! * op(A) = transpose(A) if transposeA is true; otherwise, op(A) = A.
    ! * op(B) = transpose(B) if transposeB is true; otherwise, op(B) = B.
    subroutine BLAS_GEMM_1(A, B, C, alpha, beta, transposeA, transposeB)
        ! procedure arguments
        type(t_matrix),    intent(in) :: A, B, C
        real,    optional, intent(in) :: alpha, beta
        logical, optional, intent(in) :: transposeA, transposeB
        
        ! additional variables
        integer      :: m, n, k, lda, ldb, ldc
        real         :: scalarA, scalarB
        character(1) :: transA, transB
        
        ! initialize variables
        if (present(alpha)) then; scalarA = alpha; else; scalarA = 1.0; end if
        if (present(beta )) then; scalarB = beta ; else; scalarB = 1.0; end if
        if (present(transposeA).and.transposeA) then; transA = 't'; else; transA = 'n'; end if
        if (present(transposeB).and.transposeB) then; transB = 't'; else; transB = 'n'; end if
        if (transA == 'n') then; m = A%n_rows; else; m = A%n_cols; end if
        if (transB == 'n') then; n = B%n_cols; else; n = B%n_rows; end if
        if (transA == 'n') then; k = A%n_cols; else; k = A%n_rows; end if
        if (transA == 'n') then; lda = m; else; lda = k; end if
        if (transB == 'n') then; ldb = k; else; ldb = n; end if
        ldc = m
        
        ! check for invalid arguments
        if (m /= C%n_rows .or. n /= C%n_cols) error stop ERROR_SIZE_MISMATCH_FOR_MATRIX_MATRIX_PRODUCT
        
        ! call computational routine
        call dgemm(transA, transB, m, n, k, scalarA, A%at, lda, B%at, ldb, scalarB, C%at, ldc)
    end subroutine
    
    ! Description:
    ! Computes a matrix-matrix product with general matrices.
    ! The operation is defined as C := alpha*op(A)*op(B), where:
    ! * A, B, and C are matrices.
    ! * alpha is a scalar.
    ! * op(A) = transpose(A) if transposeA is true; otherwise, op(A) = A.
    ! * op(B) = transpose(B) if transposeB is true; otherwise, op(B) = B.
    type(t_matrix) function BLAS_GEMM_2(A, B, alpha, transposeA, transposeB) result(C)
        ! procedure arguments
        type(t_matrix),    intent(in) :: A, B
        real,    optional, intent(in) :: alpha
        logical, optional, intent(in) :: transposeA, transposeB
        
        ! additional variables
        integer :: m, n
        real    :: scalarA
        logical :: transA, transB
        
        ! initialize variables
        if (present(alpha)) then; scalarA = alpha; else; scalarA = 1.0; end if
        if (present(transposeA)) then; transA = transposeA; else; transA = .false.; end if
        if (present(transposeB)) then; transB = transposeB; else; transB = .false.; end if
        if (.not.transA) then; m = A%n_rows; else; m = A%n_cols; end if
        if (.not.transB) then; n = B%n_cols; else; n = B%n_rows; end if
        C = new_matrix(m, n)
        
        ! call computational routine
        call BLAS_GEMM_1(A, B, C, scalarA, 0.0, transA, transB)
    end function
    
    ! Description:
    ! Matrix determinant for small matrices.
    real function determinant(A) result(det)
        ! procedure arguments
        type(t_matrix), intent(in) :: A
        
        ! check if A is square
        if (A%n_rows /= A%n_cols) error stop ERROR_MATRIX_MUST_BE_SQUARE_FOR_OPERATION
        
        ! compute determinant
        select case (A%n_rows)
            case (0)
                det = 1.0
            case (1)
                det = A%at(1,1)
            case (2)
                det = A%at(1,1)*A%at(2,2) - A%at(1,2)*A%at(2,1)
            case (3)
                det = A%at(1,1)*A%at(2,2)*A%at(3,3) - A%at(1,1)*A%at(2,3)*A%at(3,2) - A%at(1,2)*A%at(2,1)*A%at(3,3) + &
                      A%at(1,2)*A%at(2,3)*A%at(3,1) + A%at(1,3)*A%at(2,1)*A%at(3,2) - A%at(1,3)*A%at(2,2)*A%at(3,1)
            case (4)
                det = A%at(1,1)*A%at(2,2)*A%at(3,3)*A%at(4,4) - A%at(1,1)*A%at(2,2)*A%at(3,4)*A%at(4,3) - A%at(1,1)*A%at(2,3)*A%at(3,2)*A%at(4,4) + A%at(1,1)*A%at(2,3)*A%at(3,4)*A%at(4,2) + &
                      A%at(1,1)*A%at(2,4)*A%at(3,2)*A%at(4,3) - A%at(1,1)*A%at(2,4)*A%at(3,3)*A%at(4,2) - A%at(1,2)*A%at(2,1)*A%at(3,3)*A%at(4,4) + A%at(1,2)*A%at(2,1)*A%at(3,4)*A%at(4,3) + &
                      A%at(1,2)*A%at(2,3)*A%at(3,1)*A%at(4,4) - A%at(1,2)*A%at(2,3)*A%at(3,4)*A%at(4,1) - A%at(1,2)*A%at(2,4)*A%at(3,1)*A%at(4,3) + A%at(1,2)*A%at(2,4)*A%at(3,3)*A%at(4,1) + &
                      A%at(1,3)*A%at(2,1)*A%at(3,2)*A%at(4,4) - A%at(1,3)*A%at(2,1)*A%at(3,4)*A%at(4,2) - A%at(1,3)*A%at(2,2)*A%at(3,1)*A%at(4,4) + A%at(1,3)*A%at(2,2)*A%at(3,4)*A%at(4,1) + &
                      A%at(1,3)*A%at(2,4)*A%at(3,1)*A%at(4,2) - A%at(1,3)*A%at(2,4)*A%at(3,2)*A%at(4,1) - A%at(1,4)*A%at(2,1)*A%at(3,2)*A%at(4,3) + A%at(1,4)*A%at(2,1)*A%at(3,3)*A%at(4,2) + &
                      A%at(1,4)*A%at(2,2)*A%at(3,1)*A%at(4,3) - A%at(1,4)*A%at(2,2)*A%at(3,3)*A%at(4,1) - A%at(1,4)*A%at(2,3)*A%at(3,1)*A%at(4,2) + A%at(1,4)*A%at(2,3)*A%at(3,2)*A%at(4,1)
            case default
                error stop ERROR_MATRIX_MUST_BE_SMALL_FOR_OPERATION
        end select
    end function
    
    ! Description:
    ! Matrix inverse for small matrices.
    type(t_matrix) function inverse(A, detA) result(inv)
        ! procedure arguments
        type(t_matrix), intent(in)  :: A
        real, optional, intent(out) :: detA
        
        ! additional variables
        real :: det
        
        ! check if A is square
        if (A%n_rows /= A%n_cols) error stop ERROR_MATRIX_MUST_BE_SQUARE_FOR_OPERATION
        
        ! compute determinant
        det = determinant(A)
        if (present(detA)) detA = det
        
        ! compute inverse
        select case (A%n_rows)
            case (0)
                inv = new_matrix(0, 0)
            case (1)
                inv = new_matrix(1, 1)
                !---
                inv%at(1,1) = 1.0/det
            case (2)
                inv = new_matrix(2, 2)
                !---
                inv%at(1,1) = +A%at(2,2)/det
                inv%at(1,2) = -A%at(1,2)/det
                !---
                inv%at(2,1) = -A%at(2,1)/det
                inv%at(2,2) = +A%at(1,1)/det
            case (3)
                inv = new_matrix(3, 3)
                !---
                inv%at(1,1) = +(A%at(2,2)*A%at(3,3) - A%at(2,3)*A%at(3,2))/det
                inv%at(1,2) = -(A%at(1,2)*A%at(3,3) - A%at(1,3)*A%at(3,2))/det
                inv%at(1,3) = +(A%at(1,2)*A%at(2,3) - A%at(1,3)*A%at(2,2))/det
                !---
                inv%at(2,1) = -(A%at(2,1)*A%at(3,3) - A%at(2,3)*A%at(3,1))/det
                inv%at(2,2) = +(A%at(1,1)*A%at(3,3) - A%at(1,3)*A%at(3,1))/det
                inv%at(2,3) = -(A%at(1,1)*A%at(2,3) - A%at(1,3)*A%at(2,1))/det
                !---
                inv%at(3,1) = +(A%at(2,1)*A%at(3,2) - A%at(2,2)*A%at(3,1))/det
                inv%at(3,2) = -(A%at(1,1)*A%at(3,2) - A%at(1,2)*A%at(3,1))/det
                inv%at(3,3) = +(A%at(1,1)*A%at(2,2) - A%at(1,2)*A%at(2,1))/det
            case (4)
                inv = new_matrix(4, 4)
                !---
                inv%at(1,1) = +(A%at(2,2)*A%at(3,3)*A%at(4,4) - A%at(2,2)*A%at(3,4)*A%at(4,3) - A%at(2,3)*A%at(3,2)*A%at(4,4) + A%at(2,3)*A%at(3,4)*A%at(4,2) + A%at(2,4)*A%at(3,2)*A%at(4,3) - A%at(2,4)*A%at(3,3)*A%at(4,2))/det
                inv%at(1,2) = -(A%at(1,2)*A%at(3,3)*A%at(4,4) - A%at(1,2)*A%at(3,4)*A%at(4,3) - A%at(1,3)*A%at(3,2)*A%at(4,4) + A%at(1,3)*A%at(3,4)*A%at(4,2) + A%at(1,4)*A%at(3,2)*A%at(4,3) - A%at(1,4)*A%at(3,3)*A%at(4,2))/det
                inv%at(1,3) = +(A%at(1,2)*A%at(2,3)*A%at(4,4) - A%at(1,2)*A%at(2,4)*A%at(4,3) - A%at(1,3)*A%at(2,2)*A%at(4,4) + A%at(1,3)*A%at(2,4)*A%at(4,2) + A%at(1,4)*A%at(2,2)*A%at(4,3) - A%at(1,4)*A%at(2,3)*A%at(4,2))/det
                inv%at(1,4) = -(A%at(1,2)*A%at(2,3)*A%at(3,4) - A%at(1,2)*A%at(2,4)*A%at(3,3) - A%at(1,3)*A%at(2,2)*A%at(3,4) + A%at(1,3)*A%at(2,4)*A%at(3,2) + A%at(1,4)*A%at(2,2)*A%at(3,3) - A%at(1,4)*A%at(2,3)*A%at(3,2))/det
                !---
                inv%at(2,1) = -(A%at(2,1)*A%at(3,3)*A%at(4,4) - A%at(2,1)*A%at(3,4)*A%at(4,3) - A%at(2,3)*A%at(3,1)*A%at(4,4) + A%at(2,3)*A%at(3,4)*A%at(4,1) + A%at(2,4)*A%at(3,1)*A%at(4,3) - A%at(2,4)*A%at(3,3)*A%at(4,1))/det
                inv%at(2,2) = +(A%at(1,1)*A%at(3,3)*A%at(4,4) - A%at(1,1)*A%at(3,4)*A%at(4,3) - A%at(1,3)*A%at(3,1)*A%at(4,4) + A%at(1,3)*A%at(3,4)*A%at(4,1) + A%at(1,4)*A%at(3,1)*A%at(4,3) - A%at(1,4)*A%at(3,3)*A%at(4,1))/det
                inv%at(2,3) = -(A%at(1,1)*A%at(2,3)*A%at(4,4) - A%at(1,1)*A%at(2,4)*A%at(4,3) - A%at(1,3)*A%at(2,1)*A%at(4,4) + A%at(1,3)*A%at(2,4)*A%at(4,1) + A%at(1,4)*A%at(2,1)*A%at(4,3) - A%at(1,4)*A%at(2,3)*A%at(4,1))/det
                inv%at(2,4) = +(A%at(1,1)*A%at(2,3)*A%at(3,4) - A%at(1,1)*A%at(2,4)*A%at(3,3) - A%at(1,3)*A%at(2,1)*A%at(3,4) + A%at(1,3)*A%at(2,4)*A%at(3,1) + A%at(1,4)*A%at(2,1)*A%at(3,3) - A%at(1,4)*A%at(2,3)*A%at(3,1))/det
                !---
                inv%at(3,1) = +(A%at(2,1)*A%at(3,2)*A%at(4,4) - A%at(2,1)*A%at(3,4)*A%at(4,2) - A%at(2,2)*A%at(3,1)*A%at(4,4) + A%at(2,2)*A%at(3,4)*A%at(4,1) + A%at(2,4)*A%at(3,1)*A%at(4,2) - A%at(2,4)*A%at(3,2)*A%at(4,1))/det
                inv%at(3,2) = -(A%at(1,1)*A%at(3,2)*A%at(4,4) - A%at(1,1)*A%at(3,4)*A%at(4,2) - A%at(1,2)*A%at(3,1)*A%at(4,4) + A%at(1,2)*A%at(3,4)*A%at(4,1) + A%at(1,4)*A%at(3,1)*A%at(4,2) - A%at(1,4)*A%at(3,2)*A%at(4,1))/det
                inv%at(3,3) = +(A%at(1,1)*A%at(2,2)*A%at(4,4) - A%at(1,1)*A%at(2,4)*A%at(4,2) - A%at(1,2)*A%at(2,1)*A%at(4,4) + A%at(1,2)*A%at(2,4)*A%at(4,1) + A%at(1,4)*A%at(2,1)*A%at(4,2) - A%at(1,4)*A%at(2,2)*A%at(4,1))/det
                inv%at(3,4) = -(A%at(1,1)*A%at(2,2)*A%at(3,4) - A%at(1,1)*A%at(2,4)*A%at(3,2) - A%at(1,2)*A%at(2,1)*A%at(3,4) + A%at(1,2)*A%at(2,4)*A%at(3,1) + A%at(1,4)*A%at(2,1)*A%at(3,2) - A%at(1,4)*A%at(2,2)*A%at(3,1))/det
                !---
                inv%at(4,1) = -(A%at(2,1)*A%at(3,2)*A%at(4,3) - A%at(2,1)*A%at(3,3)*A%at(4,2) - A%at(2,2)*A%at(3,1)*A%at(4,3) + A%at(2,2)*A%at(3,3)*A%at(4,1) + A%at(2,3)*A%at(3,1)*A%at(4,2) - A%at(2,3)*A%at(3,2)*A%at(4,1))/det
                inv%at(4,2) = +(A%at(1,1)*A%at(3,2)*A%at(4,3) - A%at(1,1)*A%at(3,3)*A%at(4,2) - A%at(1,2)*A%at(3,1)*A%at(4,3) + A%at(1,2)*A%at(3,3)*A%at(4,1) + A%at(1,3)*A%at(3,1)*A%at(4,2) - A%at(1,3)*A%at(3,2)*A%at(4,1))/det
                inv%at(4,3) = -(A%at(1,1)*A%at(2,2)*A%at(4,3) - A%at(1,1)*A%at(2,3)*A%at(4,2) - A%at(1,2)*A%at(2,1)*A%at(4,3) + A%at(1,2)*A%at(2,3)*A%at(4,1) + A%at(1,3)*A%at(2,1)*A%at(4,2) - A%at(1,3)*A%at(2,2)*A%at(4,1))/det
                inv%at(4,4) = +(A%at(1,1)*A%at(2,2)*A%at(3,3) - A%at(1,1)*A%at(2,3)*A%at(3,2) - A%at(1,2)*A%at(2,1)*A%at(3,3) + A%at(1,2)*A%at(2,3)*A%at(3,1) + A%at(1,3)*A%at(2,1)*A%at(3,2) - A%at(1,3)*A%at(2,2)*A%at(3,1))/det
            case default
                error stop ERROR_MATRIX_MUST_BE_SMALL_FOR_OPERATION
        end select
    end function
    
end module
