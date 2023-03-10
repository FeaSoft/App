! Description:
! Linear algebra computational routines (Intel MKL wrappers).
module m_linalg
    use mkl_spblas
    use mkl_solvers_ee
    use m_vector
    use m_matrix
    use m_sparse
    implicit none
    
    private
    public maxabs, add, subtract, dot, multiply, solve, eigen, determinant, inverse
    
    ! error messages
    character(*), parameter :: ERROR_SIZE_MISMATCH_FOR_VECTOR_VECTOR_OPERATION = 'Error: size mismatch for vector-vector operation', &
                               ERROR_SIZE_MISMATCH_FOR_MATRIX_VECTOR_OPERATION = 'Error: size mismatch for matrix-vector operation', &
                               ERROR_SIZE_MISMATCH_FOR_MATRIX_MATRIX_OPERATION = 'Error: size mismatch for matrix-matrix operation', &
                               ERROR_MATRIX_MUST_BE_SQUARE_FOR_OPERATION       = 'Error: matrix must be square for operation',     &
                               ERROR_MATRIX_MUST_BE_SMALL_FOR_OPERATION        = 'Error: matrix must be small for operation'
    
    interface add
        module procedure :: VML_add
    end interface
    
    interface subtract
        module procedure :: VML_sub
    end interface
    
    interface multiply
        module procedure :: BLAS_GEMV_1, BLAS_GEMV_2, BLAS_GEMM_1, BLAS_GEMM_2, SPBLAS_MV_1, SPBLAS_MV_2
    end interface
    
    interface solve
        module procedure :: MKL_PARDISO
    end interface
    
    interface eigen
        module procedure :: LAPACK_SYEV, EE_GV
    end interface
    
    contains
    
    ! Description:
    ! Returns the maximum absolute value in vector (infinity norm).
    real function maxabs(a) result(x)
        type(t_vector), intent(in) :: a
        x = maxval(abs(a%at(:)))
    end function
    
    ! Description:
    ! Computes element-wise addition of vectors.
    ! The operation is defined as y := a + b, where:
    ! * a, b, and y are vectors.
    type(t_vector) function VML_add(a, b) result(y)
        ! procedure arguments
        type(t_vector), intent(in) :: a, b
        
        ! external procedures
        external :: vdadd
        
        ! check for invalid arguments
        if (a%n_vals /= b%n_vals) error stop ERROR_SIZE_MISMATCH_FOR_VECTOR_VECTOR_OPERATION
        
        ! call computational routine
        y = new_vector(a%n_vals)
        call vdadd(a%n_vals, a%at, b%at, y%at)
    end function
    
    ! Description:
    ! Computes element-wise subtraction of vectors.
    ! The operation is defined as y := a - b, where:
    ! * a, b, and y are vectors.
    type(t_vector) function VML_sub(a, b) result(y)
        ! procedure arguments
        type(t_vector), intent(in) :: a, b
        
        ! external procedures
        external :: vdsub
        
        ! check for invalid arguments
        if (a%n_vals /= b%n_vals) error stop ERROR_SIZE_MISMATCH_FOR_VECTOR_VECTOR_OPERATION
        
        ! call computational routine
        y = new_vector(a%n_vals)
        call vdsub(a%n_vals, a%at, b%at, y%at)
    end function
    
    ! Description:
    ! Computes the dot product between two vectors.
    real function dot(a, b) result(x)
        ! procedure arguments
        type(t_vector), intent(in) :: a, b
        
        ! check for invalid arguments
        if (a%n_vals /= b%n_vals) error stop ERROR_SIZE_MISMATCH_FOR_VECTOR_VECTOR_OPERATION
        
        ! call computational routine
        x = dot_product(a%at(:), b%at(:))
    end function
    
    ! Description:
    ! Computes a matrix-vector product using a general matrix.
    ! The operation is defined as y := alpha*op(A)*x + beta*y, where:
    ! * A is a matrix.
    ! * x and y are vectors.
    ! * alpha and beta are scalars.
    ! * op(A) = transpose(A) if transposeA is true; otherwise, op(A) = A.
    subroutine BLAS_GEMV_1(A, x, y, alpha, beta, transposeA)
        ! procedure arguments
        type(t_matrix),    intent(in)    :: A
        type(t_vector),    intent(in)    :: x
        type(t_vector),    intent(inout) :: y
        real,    optional, intent(in)    :: alpha, beta
        logical, optional, intent(in)    :: transposeA
        
        ! external procedures
        external :: dgemv
        
        ! additional variables
        real         :: scalarA, scalarB
        character(1) :: transA
        
        ! initialize variables
        if (present(alpha)) then; scalarA = alpha; else; scalarA = 1.0; end if
        if (present(beta )) then; scalarB = beta ; else; scalarB = 1.0; end if
        if (present(transposeA).and.transposeA) then; transA = 't'; else; transA = 'n'; end if
        
        ! check for invalid arguments
        if (present(transposeA).and.transposeA) then
            if (A%n_rows /= x%n_vals .or. A%n_cols /= y%n_vals) error stop ERROR_SIZE_MISMATCH_FOR_MATRIX_VECTOR_OPERATION
        else
            if (A%n_cols /= x%n_vals .or. A%n_rows /= y%n_vals) error stop ERROR_SIZE_MISMATCH_FOR_MATRIX_VECTOR_OPERATION
        end if
        
        ! call computational routine
        call dgemv(transA, A%n_rows, A%n_cols, scalarA, A%at, A%n_rows, x%at, 1, scalarB, y%at, 1)
    end subroutine
    
    ! Description:
    ! Computes a matrix-vector product using a general matrix.
    ! The operation is defined as y := alpha*op(A)*x, where:
    ! * A is a matrix.
    ! * x and y are vectors.
    ! * alpha is a scalar.
    ! * op(A) = transpose(A) if transposeA is true; otherwise, op(A) = A.
    type(t_vector) function BLAS_GEMV_2(A, x, alpha, transposeA) result(y)
        ! procedure arguments
        type(t_matrix),    intent(in) :: A
        type(t_vector),    intent(in) :: x
        real,    optional, intent(in) :: alpha
        logical, optional, intent(in) :: transposeA
        
        ! additional variables
        real    :: scalarA
        logical :: transA
        
        ! initialize variables
        if (present(alpha)) then; scalarA = alpha; else; scalarA = 1.0; end if
        if (present(transposeA)) then; transA = transposeA; else; transA = .false.; end if
        if (.not.transA) then; y = new_vector(A%n_rows); else; y = new_vector(A%n_cols); end if
        
        ! call computational routine
        call BLAS_GEMV_1(A, x, y, scalarA, 0.0, transA)
    end function
    
    ! Description:
    ! Computes a matrix-matrix product with general matrices.
    ! The operation is defined as C := alpha*op(A)*op(B) + beta*C, where:
    ! * A, B, and C are matrices.
    ! * alpha and beta are scalars.
    ! * op(A) = transpose(A) if transposeA is true; otherwise, op(A) = A.
    ! * op(B) = transpose(B) if transposeB is true; otherwise, op(B) = B.
    subroutine BLAS_GEMM_1(A, B, C, alpha, beta, transposeA, transposeB)
        ! procedure arguments
        type(t_matrix),    intent(in)    :: A, B
        type(t_matrix),    intent(inout) :: C
        real,    optional, intent(in)    :: alpha, beta
        logical, optional, intent(in)    :: transposeA, transposeB
        
        ! external procedures
        external :: dgemm
        
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
        if (m /= C%n_rows .or. n /= C%n_cols) error stop ERROR_SIZE_MISMATCH_FOR_MATRIX_MATRIX_OPERATION
        
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
    ! Checks for runtime errors during sparse BLAS routines.
    subroutine SPBLAS_check_status(status)
        integer, intent(in) :: status ! operation status
        select case (status)
            case (SPARSE_STATUS_SUCCESS);         !print '("The operation was successful")'
            case (SPARSE_STATUS_NOT_INITIALIZED);  error stop 'Error: the routine encountered an empty handle or matrix array'
            case (SPARSE_STATUS_ALLOC_FAILED);     error stop 'Error: internal memory allocation failed'
            case (SPARSE_STATUS_INVALID_VALUE);    error stop 'Error: the input parameters contain an invalid value'
            case (SPARSE_STATUS_EXECUTION_FAILED); error stop 'Error: execution failed'
            case (SPARSE_STATUS_INTERNAL_ERROR);   error stop 'Error: an error in algorithm implementation occurred'
            case (SPARSE_STATUS_NOT_SUPPORTED);    error stop 'Error: the requested operation is not supported'
            case default;                          error stop 'Error: undefined sparse BLAS error'
        end select
    end subroutine
    
    ! Description:
    ! Creates a handle for a CSR-format matrix.
    type(sparse_matrix_t) function SPBLAS_create(A) result(handle)
        type(t_sparse), intent(in) :: A      ! sparse matrix to convert
        integer                    :: status ! operation status
        status = mkl_sparse_d_create_csr(handle, SPARSE_INDEX_BASE_ONE, A%n_rows, A%n_cols, A%row(1:A%n_rows), A%row(2:A%n_rows+1), A%col, A%val)
        call SPBLAS_check_status(status)
    end function
    
    ! Description:
    ! Frees memory allocated for matrix handle.
    subroutine SPBLAS_destroy(handle)
        type(sparse_matrix_t), intent(inout) :: handle ! sparse matrix handle to destroy
        integer                              :: status ! operation status
        status = mkl_sparse_destroy(handle)
        call SPBLAS_check_status(status)
    end subroutine
    
    ! Description:
    ! Computes a sparse matrix-vector product.
    ! The operation is defined as y := alpha*op(A)*x + beta*y, where:
    ! * A is a sparse matrix.
    ! * x and y are vectors.
    ! * alpha and beta are scalars.
    ! * op(A) = transpose(A) if transposeA is true; otherwise, op(A) = A.
    subroutine SPBLAS_MV_1(A, x, y, alpha, beta, transposeA)
        ! procedure arguments
        type(t_sparse),    intent(in)    :: A
        type(t_vector),    intent(in)    :: x
        type(t_vector),    intent(inout) :: y
        real,    optional, intent(in)    :: alpha, beta
        logical, optional, intent(in)    :: transposeA
        
        ! additional variables
        type(sparse_matrix_t) :: handle
        type(matrix_descr)    :: description
        real                  :: scalarA, scalarB
        integer               :: transA, status
        
        ! initialize variables
        if (present(alpha)) then; scalarA = alpha; else; scalarA = 1.0; end if
        if (present(beta )) then; scalarB = beta ; else; scalarB = 1.0; end if
        if (present(transposeA).and.transposeA) then; transA = SPARSE_OPERATION_TRANSPOSE; else; transA = SPARSE_OPERATION_NON_TRANSPOSE; end if
        
        ! check for invalid arguments
        if (present(transposeA).and.transposeA) then
            if (A%n_rows /= x%n_vals .or. A%n_cols /= y%n_vals) error stop ERROR_SIZE_MISMATCH_FOR_MATRIX_VECTOR_OPERATION
        else
            if (A%n_cols /= x%n_vals .or. A%n_rows /= y%n_vals) error stop ERROR_SIZE_MISMATCH_FOR_MATRIX_VECTOR_OPERATION
        end if
        
        ! call computational routine
        description%type = SPARSE_MATRIX_TYPE_GENERAL
        handle = SPBLAS_create(A)
        status = mkl_sparse_d_mv(transA, scalarA, handle, description, x%at, scalarB, y%at)
        call SPBLAS_check_status(status)
        call SPBLAS_destroy(handle)
    end subroutine
    
    ! Description:
    ! Computes a sparse matrix-vector product.
    ! The operation is defined as y := alpha*op(A)*x, where:
    ! * A is a sparse matrix.
    ! * x and y are vectors.
    ! * alpha is a scalar.
    ! * op(A) = transpose(A) if transposeA is true; otherwise, op(A) = A.
    type(t_vector) function SPBLAS_MV_2(A, x, alpha, transposeA) result(y)
        ! procedure arguments
        type(t_sparse),    intent(in) :: A
        type(t_vector),    intent(in) :: x
        real,    optional, intent(in) :: alpha
        logical, optional, intent(in) :: transposeA
        
        ! additional variables
        real    :: scalarA
        logical :: transA
        
        ! initialize variables
        if (present(alpha)) then; scalarA = alpha; else; scalarA = 1.0; end if
        if (present(transposeA)) then; transA = transposeA; else; transA = .false.; end if
        if (.not.transA) then; y = new_vector(A%n_rows); else; y = new_vector(A%n_cols); end if
        
        ! call computational routine
        call SPBLAS_MV_1(A, x, y, scalarA, 0.0, transA)
    end function
    
    ! Description:
    ! Checks for runtime errors during PARDISO routines.
    subroutine MKL_PARDISO_check_error(error)
        integer, intent(in) :: error ! operation error
        select case (error)
            case (0);    !print '("No error")'
            case (-1);    error stop 'Error: input inconsistent'
            case (-2);    error stop 'Error: not enough memory'
            case (-3);    error stop 'Error: reordering problem'
            case (-4);    error stop 'Error: zero pivot, numerical factorization or iterative refinement problem'
            case (-5);    error stop 'Error: unclassified (internal) error'
            case (-6);    error stop 'Error: reordering failed (matrix types 11 and 13 only)'
            case (-7);    error stop 'Error: diagonal matrix is singular'
            case (-8);    error stop 'Error: 32-bit integer overflow problem'
            case (-9);    error stop 'Error: not enough memory for OOC'
            case (-10);   error stop 'Error: problems with opening OOC temporary files'
            case (-11);   error stop 'Error: read/write problems with the OOC data file'
            case default; error stop 'Error: undefined PARDISO error'
        end select
    end subroutine
    
    ! Description:
    ! Solves a linear algebraic sparse system of equations.
    type(t_vector) function MKL_PARDISO(A, b) result(x)
        ! procedure arguments
        type(t_sparse), intent(in) :: A
        type(t_vector), intent(in) :: b
        
        ! external procedures
        external :: pardisoinit, pardiso
        
        ! additional variables
        integer              :: iparm(64) = 0  ! PARDISO parameters (use PARDISO defaults)
        integer              :: pt(64)    = 0  ! handle to internal data structure
        integer              :: mtype     = 1  ! matrix type (real and structurally symmetric matrix)
        integer              :: maxfct    = 1  ! maximal number of factors in memory
        integer              :: mnum      = 1  ! indicates the actual matrix for the solution phase
        integer              :: nrhs      = 1  ! number of right-hand sides
        integer              :: msglvl    = 0  ! message level information
        integer              :: phase          ! PARDISO operation flag
        integer              :: error          ! error information
        integer, allocatable :: perm(:)        ! permutation vector
        
        ! check for invalid arguments
        if (A%n_rows /= A%n_cols) error stop ERROR_MATRIX_MUST_BE_SQUARE_FOR_OPERATION
        if (A%n_rows /= b%n_vals) error stop ERROR_SIZE_MISMATCH_FOR_MATRIX_VECTOR_OPERATION
        
        ! allocate permutation vector
        allocate(perm(A%n_rows), source=0)
        
        ! call computational routine
        x = new_vector(A%n_rows)
        phase = 13 ! analysis, numerical factorization, solve, and iterative refinement
        call pardisoinit(pt, mtype, iparm)
        call pardiso(pt, maxfct, mnum, mtype, phase, A%n_rows, A%val, A%row, A%col, perm, nrhs, iparm, msglvl, b%at, x%at, error)
        call MKL_PARDISO_check_error(error)
        
        ! release memory
        phase = -1 ! release all internal memory for all matrices
        call pardiso(pt, maxfct, mnum, mtype, phase, A%n_rows, A%val, A%row, A%col, perm, nrhs, iparm, msglvl, b%at, x%at, error)
        call MKL_PARDISO_check_error(error)
        
        ! deallocate permutation vector
        if (allocated(perm)) deallocate(perm)
    end function
    
    ! Description:
    ! Computes all eigenvalues of a real symmetric matrix (in ascending order).
    type(t_vector) function LAPACK_SYEV(A) result(lambda)
        ! procedure arguments
        type(t_matrix), intent(in) :: A
        
        ! external procedures
        external :: dsyev
        
        ! additional variables
        integer           :: lwork, info
        real, allocatable :: work(:)
        
        ! check for invalid arguments
        if (A%n_rows /= A%n_cols) error stop ERROR_MATRIX_MUST_BE_SQUARE_FOR_OPERATION
        
        ! initialize vector
        lambda = new_vector(A%n_rows)
        
        ! query optimal size for the work array
        lwork = -1
        allocate(work(1))
        call dsyev('N', 'U', A%n_rows, A%at, A%n_rows, lambda%at, work, lwork, info)
        if (info /= 0) error stop 'Error: execution error'
        
        ! call computational routine
        lwork = int(work(1))
        if (allocated(work)) deallocate(work)
        allocate(work(lwork))
        call dsyev('N', 'U', A%n_rows, A%at, A%n_rows, lambda%at, work, lwork, info)
        if (info /= 0) error stop 'Error: execution error'
        
        ! deallocate work array
        if (allocated(work)) deallocate(work)
    end function
    
    ! Description:
    ! Computes the smallest or largest eigenvalues and corresponding eigenvectors of a generalized eigenproblem using sparse matrices.
    subroutine EE_GV(job, A, B, k0, k, E, X)
        ! procedure arguments
        character,      intent(in)  :: job  ! 'S': smallest eigenvalues; 'L': largest eigenvalues
        type(t_sparse), intent(in)  :: A, B ! sparse matrices
        integer,        intent(in)  :: k0   ! requested number of eigenpairs
        integer,        intent(out) :: k    ! number of eigenpairs found
        type(t_vector), intent(out) :: E    ! eigenvalues
        type(t_matrix), intent(out) :: X    ! eigenvectors
        
        ! additional variables
        type(sparse_matrix_t) :: handleA, handleB
        type(matrix_descr)    :: descriptionA, descriptionB
        integer               :: pm(128)
        integer               :: status
        real                  :: res(k0)
        
        ! check for invalid arguments
        if (A%n_rows /= A%n_cols) error stop ERROR_MATRIX_MUST_BE_SQUARE_FOR_OPERATION
        if (B%n_rows /= B%n_cols) error stop ERROR_MATRIX_MUST_BE_SQUARE_FOR_OPERATION
        if (A%n_rows /= B%n_rows) error stop ERROR_SIZE_MISMATCH_FOR_MATRIX_MATRIX_OPERATION
        
        ! create MKL handles
        handleA = SPBLAS_create(A)
        handleB = SPBLAS_create(B)
        descriptionA%type = SPARSE_MATRIX_TYPE_SYMMETRIC
        descriptionA%mode = SPARSE_FILL_MODE_UPPER
        descriptionA%diag = SPARSE_DIAG_NON_UNIT
        descriptionB%type = SPARSE_MATRIX_TYPE_SYMMETRIC
        descriptionB%mode = SPARSE_FILL_MODE_UPPER
        descriptionB%diag = SPARSE_DIAG_NON_UNIT
        
        ! initialize input parameters with default values
        status = mkl_sparse_ee_init(pm)
        call SPBLAS_check_status(status)
        
        ! call computational routine
        k = 0
        E = new_vector(k0)
        X = new_matrix(A%n_rows, k0)
        status = mkl_sparse_d_gv(job, pm, handleA, descriptionA, handleB, descriptionB, k0, k, E%at, X%at, res)
        call SPBLAS_check_status(status)
        
        ! destroy handles
        call SPBLAS_destroy(handleA)
        call SPBLAS_destroy(handleB)
    end subroutine
    
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
